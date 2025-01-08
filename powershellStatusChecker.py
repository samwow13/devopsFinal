import subprocess

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
    
    return result.stdout