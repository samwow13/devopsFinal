import subprocess

def check_start_or_stop_EAP_services(username, password, server, startOrStop, ):
    """
    Check services status using PowerShell
    Args:
        username (str): Username for authentication
        password (str): Password for authentication
        server (str): Server to check services on
    Returns:
        str: Output from PowerShell command
    Raises:
        ValueError: If username or password is None or empty
        ConnectionError: If connection to remote server fails
    """
    # Validate inputs
    if not username or not password:
        raise ValueError("Username and password are required")
        
    # Build a PowerShell script dynamically
    ps_script = f'''
$services = @("{'","'.join(services)}")
$password = ConvertTo-SecureString "{password}" -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ("{username}", $password)
$session = New-PSSession -ComputerName {server} -Credential $cred

Invoke-Command -Session $session -ScriptBlock {{
    param([string[]] $servicesList)
    foreach ($service in $servicesList) {{
        Write-Host "Checking service: $service"
        try {{
            $svc = Get-Service -Name $service -ErrorAction Stop
            if ($svc.Status -eq "Running") {{
                Write-Host "Service '$service' is running."
            }} else {{
                Write-Host "Service '$service' is not running."
            }}
        }} catch {{
            Write-Host "Service '$service' not found or inaccessible."
        }}
    }}
}} -ArgumentList (,$services)

Remove-PSSession $session
'''
    
    # Print the PowerShell command being sent
    print("PS command sent for starting or stopping EAP services:")
    print(ps_script)


def check_services_powershell(username, password, server, services):
    """
    Check services status using PowerShell
    Args:
        username (str): Username for authentication
        password (str): Password for authentication
        server (str): Server to check services on
        services (list): List of service names to check
    Returns:
        str: Output from PowerShell command
    Raises:
        ValueError: If username or password is None or empty
        ConnectionError: If connection to remote server fails
    """
    # Validate inputs
    if not username or not password:
        raise ValueError("Username and password are required")
        
    # Build a PowerShell script dynamically
    ps_script = f'''
$services = @("{'","'.join(services)}")
$password = ConvertTo-SecureString "{password}" -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ("{username}", $password)
$session = New-PSSession -ComputerName {server} -Credential $cred

Invoke-Command -Session $session -ScriptBlock {{
    param([string[]] $servicesList)
    foreach ($service in $servicesList) {{
        Write-Host "Checking service: $service"
        try {{
            $svc = Get-Service -Name $service -ErrorAction Stop
            if ($svc.Status -eq "Running") {{
                Write-Host "Service '$service' is running."
            }} else {{
                Write-Host "Service '$service' is not running."
            }}
        }} catch {{
            Write-Host "Service '$service' not found or inaccessible."
        }}
    }}
}} -ArgumentList (,$services)

Remove-PSSession $session
'''
    
    # Print the PowerShell command being sent (with sensitive info masked)
    masked_script = ps_script.replace(password, "********") if password else ps_script
    print("\n=== PowerShell Command Being Sent ===")
    print(ps_script)
    print("===================================\n")

    # Execute the PowerShell script
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps_script],
        capture_output=True,
        text=True
    )
    
    # Print the response
    print("\n=== PowerShell Response ===")
    print(result.stdout)
    if result.stderr:
        print("\n=== PowerShell Errors ===")
        print(result.stderr)
    print("===========================\n")
    
    # Check for connection errors in both stdout and stderr
    output = result.stdout + result.stderr
    if "New-PSSession : " in output and "Connecting to remote server" in output and "failed" in output:
        raise ConnectionError("Failed to connect to remote server. Please logout and re-type your credentials.")
    
    return result.stdout