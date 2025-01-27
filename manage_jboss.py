import json
import subprocess
import os
import logging
import datetime
from logging.handlers import RotatingFileHandler

# Configure logging
def setup_logger():
    """
    Sets up a logger with both file and console handlers.
    File logs will be stored in 'logs/jboss_management.log' with rotation.
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger('jboss_management')
    logger.setLevel(logging.DEBUG)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s\n'
        'Details: %(details)s\n'
        '-------------------------'
    )
    console_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    
    # File handler (with rotation)
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'jboss_management.log'),
        maxBytes=1024*1024,  # 1MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Initialize logger
logger = setup_logger()

def manage_jboss(server_key, action, username, password, config_path="config.json"):
    """
    Manages JBoss (start or stop) on a given server by reading the *entire command* 
    from a JSON config (including directory changes). Passes credentials dynamically to PowerShell.

    :param server_key: The key in the JSON ("wpdhsappl84", "prod92", etc.)
    :param action: "start" or "stop"
    :param username: The credential username for the remote machine
    :param password: The credential password for the remote machine
    :param config_path: Path to the JSON configuration file
    """
    
    try:
        # Log operation start
        logger.info(
            f"Initiating JBoss {action} operation for server {server_key}",
            extra={'details': {
                'server': server_key,
                'action': action,
                'username': username,
                'config_path': config_path,
                'timestamp': datetime.datetime.now().isoformat()
            }}
        )

        # 1. Load the configuration
        if not os.path.exists(config_path):
            error_msg = f"Could not find config file: {config_path}"
            logger.error(error_msg, extra={'details': {'error_type': 'FileNotFound'}})
            raise FileNotFoundError(error_msg)

        with open(config_path, 'r') as f:
            config = json.load(f)
            logger.debug(
                "Successfully loaded configuration file",
                extra={'details': {'config_path': config_path}}
            )

        servers = config.get("servers", {})
        server_data = servers.get(server_key)
        if not server_data:
            error_msg = f"Server '{server_key}' not found in configuration"
            logger.error(error_msg, extra={'details': {'available_servers': list(servers.keys())}})
            raise ValueError(error_msg)

        # 2. Decide which CLI command to run
        if action.lower() == "start":
            jboss_script = server_data["start_jboss"]
        elif action.lower() == "stop":
            jboss_script = server_data["stop_jboss"]
        else:
            error_msg = "Invalid action. Must be 'start' or 'stop'"
            logger.error(error_msg, extra={'details': {'provided_action': action}})
            raise ValueError(error_msg)

        logger.debug(
            f"Retrieved JBoss {action} script from configuration",
            extra={'details': {'script': jboss_script}}
        )

        # 3. Construct PowerShell script
        powershell_script = f'''
        $securePassword = ConvertTo-SecureString "{password}" -AsPlainText -Force
        $cred = New-Object System.Management.Automation.PSCredential ("{username}", $securePassword)

        Write-Host "Creating PowerShell session to {server_key}..."
        $session = New-PSSession -ComputerName {server_key} -Credential $cred

        Invoke-Command -Session $session -ScriptBlock {{
            {jboss_script}
        }}

        Remove-PSSession -Session $session
        '''

        logger.debug(
            "Constructed PowerShell script",
            extra={'details': {'script_length': len(powershell_script)}}
        )

        # 4. Invoke PowerShell
        logger.info(
            f"Executing PowerShell script for {action} operation",
            extra={'details': {
                'server': server_key,
                'action': action,
                'execution_time': datetime.datetime.now().isoformat()
            }}
        )

        process = subprocess.run(
            ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", powershell_script],
            capture_output=True, text=True
        )

        # 5. Check results
        if process.returncode == 0:
            logger.info(
                f"Successfully executed {action} operation",
                extra={'details': {
                    'stdout': process.stdout,
                    'execution_time': datetime.datetime.now().isoformat()
                }}
            )
        else:
            error_msg = f"PowerShell script failed with return code {process.returncode}"
            logger.error(
                error_msg,
                extra={'details': {
                    'stderr': process.stderr,
                    'stdout': process.stdout,
                    'return_code': process.returncode
                }}
            )
            raise subprocess.CalledProcessError(
                process.returncode, process.args,
                output=process.stdout, stderr=process.stderr
            )

    except Exception as e:
        logger.exception(
            f"Unexpected error during {action} operation",
            extra={'details': {
                'error_type': type(e).__name__,
                'error_message': str(e)
            }}
        )
        raise
