import json
import subprocess
import os

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

    # 1. Load the configuration
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Could not find config file: {config_path}")

    with open(config_path, 'r') as f:
        config = json.load(f)

    servers = config.get("servers", {})
    server_data = servers.get(server_key)
    if not server_data:
        raise ValueError(f"Server '{server_key}' not found in configuration.")

    # 2. Decide which CLI command to run, based on "start" or "stop"
    #    Each one in the JSON is the *entire* command to run inside the ScriptBlock.
    if action.lower() == "start":
        jboss_script = server_data["start_jboss"]
    elif action.lower() == "stop":
        jboss_script = server_data["stop_jboss"]
    else:
        raise ValueError("Invalid action. Must be 'start' or 'stop'.")

    # 3. Construct your PowerShell script. The entire "jboss_script" 
    #    (cd + CLI invocation) is inserted inside the ScriptBlock.
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

    # 4. Invoke PowerShell from Python using subprocess
    process = subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", powershell_script],
        capture_output=True, text=True
    )

    # 5. Check for success or error
    if process.returncode == 0:
        print("PowerShell script executed successfully.")
        print("STDOUT:")
        print(process.stdout)
    else:
        print("PowerShell script failed.")
        print("STDERR:")
        print(process.stderr)
        raise subprocess.CalledProcessError(process.returncode, process.args, 
                                            output=process.stdout, stderr=process.stderr)


# --------------------
# Example usage:

if __name__ == "__main__":
    # In real usage, read these from environment variables or a vault:
    username = "swetzel_admin"
    password = "zzzt"

    manage_jboss("wpdhsappl84", "start", username, password)
    # manage_jboss("wpdhsappl84", "stop", username, password)
