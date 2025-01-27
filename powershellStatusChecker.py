import subprocess

def check_services_powershell(username, password, server, service, jboss_cli_command=None):
    """
    Check the status of a single service using PowerShell, with enhanced JBoss checking.
    Args:
        username (str): Username for authentication
        password (str): Password for authentication
        server (str): Server to check the service on
        service (str): Name of the service to check
        jboss_cli_command (str, optional): JBoss CLI command to execute. If None, falls back to standard service check.
    Returns:
        str: Output from PowerShell command
    Raises:
        ValueError: If username or password is None or empty
        ConnectionError: If connection to remote server fails
    """

    # Validate inputs
    if not username or not password:
        print(f"Validation failed: Username: {username}, Password: {password}")
        raise ValueError("Username and password are required")
    else:
        print(f"Validation passed: Username: {username}, Password: {password}")


    # Build the PowerShell script
    ps_script = f'''
$password = ConvertTo-SecureString "{password}" -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ("{username}", $password)
$session = New-PSSession -ComputerName {server} -Credential $cred

Invoke-Command -Session $session -ScriptBlock {{
    param([string] $service, [string] $serverParam, [string] $jbossCliCommand)
    Write-Host "Checking service: $service"
    try {{
        if ($jbossCliCommand) {{
            # JBoss-specific check
            $targetDirectory = "D:\\EAP\\jboss-eap-7.4\\bin"
            Set-Location -Path $targetDirectory
            $serverLower = $serverParam.ToLower()
            $statusOutput = Invoke-Expression $jbossCliCommand
            $status = $null

            # Parse the output to find the status
            foreach ($line in $statusOutput) {{
                if ($line -match '"result"\\s*=>\\s*"(\\w+)"') {{
                    $status = $matches[1]
                    break
                }}
            }}

            # Determine the status
            if ($status -eq "STARTED" -or $status -eq "STARTING") {{
                Write-Host "Service '$service' is running."
            }} elseif ($status -eq "STOPPED" -or $status -eq "STOPPING") {{
                Write-Host "Service '$service' is not running."
            }} else {{
                Write-Host "Service '$service' status unknown: $status"
            }}
        }} else {{
            # Standard service check
            $svc = Get-Service -Name $service -ErrorAction Stop
            if ($svc.Status -eq "Running") {{
                Write-Host "Service '$service' is running."
            }} else {{
                Write-Host "Service '$service' is not running."
            }}
        }}
    }} catch {{
        # Properly format the error message
Write-Host "An error occurred while checking $service: $(${_.Exception.Message})"

    }}
}} -ArgumentList '{service}', '{server}', '{jboss_cli_command or ""}'

Remove-PSSession $session
'''

    # Print the PowerShell command being sent (with sensitive info masked)
    masked_script = ps_script.replace(password, "********") if password else ps_script
    print("\n=== PowerShell Command Being Sent ===")
    print(masked_script)
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
        raise ConnectionError("Failed to connect to remote server. Please check credentials.")

    return result.stdout


# import subprocess

# def check_services_powershell(username, password, server, service, jboss_cli_command=None):
#     """
#     Check the status of a single service using PowerShell, with enhanced JBoss checking.
#     Args:
#         username (str): Username for authentication
#         password (str): Password for authentication
#         server (str): Server to check the service on
#         service (str): Name of the service to check
#         jboss_cli_command (str, optional): JBoss CLI command to execute. If None, falls back to standard service check.
#     Returns:
#         str: Output from PowerShell command
#     Raises:
#         ValueError: If username or password is None or empty
#         ConnectionError: If connection to remote server fails
#     """
#     # Validate inputs
#     if not username or not password:
#         raise ValueError("Username and password are required")

#     # Build the PowerShell script
#     ps_script = f'''
# $password = ConvertTo-SecureString "{password}" -AsPlainText -Force
# $cred = New-Object System.Management.Automation.PSCredential ("{username}", $password)
# $session = New-PSSession -ComputerName {server} -Credential $cred

# Invoke-Command -Session $session -ScriptBlock {{
#     param([string] $service, [string] $serverParam, [string] $jbossCliCommand)
#     Write-Host "Checking service: $service"
#     try {{
#         if ($jbossCliCommand) {{
#             # JBoss-specific check
#             $targetDirectory = "D:\\EAP\\jboss-eap-7.4\\bin"
#             Set-Location -Path $targetDirectory
#             $serverLower = $serverParam.ToLower()
#             $statusOutput = Invoke-Expression $jbossCliCommand
#             $status = $null

#             # Parse the output to find the status
#             foreach ($line in $statusOutput) {{
#                 if ($line -match '"result"\\s*=>\\s*"(\\w+)"') {{
#                     $status = $matches[1]
#                     break
#                 }}
#             }}

#             # Determine the status
#             if ($status -eq "STARTED" -or $status -eq "STARTING") {{
#                 Write-Host "Service '$service' is running."
#             }} elseif ($status -eq "STOPPED" -or $status -eq "STOPPING") {{
#                 Write-Host "Service '$service' is not running."
#             }} else {{
#                 Write-Host "Service '$service' status unknown: $status"
#             }}
#         }} else {{
#             # Standard service check
#             $svc = Get-Service -Name $service -ErrorAction Stop
#             if ($svc.Status -eq "Running") {{
#                 Write-Host "Service '$service' is running."
#             }} else {{
#                 Write-Host "Service '$service' is not running."
#             }}
#         }}
#     }} catch {{
#         Write-Host "An error occurred while checking $service: $_"
#     }}
# }} -ArgumentList '{service}', '{server}', '{jboss_cli_command or ""}'

# Remove-PSSession $session
# '''

#     # Print the PowerShell command being sent (with sensitive info masked)
#     masked_script = ps_script.replace(password, "********") if password else ps_script
#     print("\n=== PowerShell Command Being Sent ===")
#     print(masked_script)
#     print("===================================\n")

#     # Execute the PowerShell script
#     result = subprocess.run(
#         ["powershell", "-NoProfile", "-Command", ps_script],
#         capture_output=True,
#         text=True
#     )

#     # Print the response
#     print("\n=== PowerShell Response ===")
#     print(result.stdout)
#     if result.stderr:
#         print("\n=== PowerShell Errors ===")
#         print(result.stderr)
#     print("===========================\n")

#     # Check for connection errors in both stdout and stderr
#     output = result.stdout + result.stderr
#     if "New-PSSession : " in output and "Connecting to remote server" in output and "failed" in output:
#         raise ConnectionError("Failed to connect to remote server. Please check credentials.")

#     return result.stdout



# import subprocess

# def check_services_powershell(username, password, server, services):
#     """
#     Check services status using PowerShell
#     Args:
#         username (str): Username for authentication
#         password (str): Password for authentication
#         server (str): Server to check services on
#         services (list): List of service names to check
#     Returns:
#         str: Output from PowerShell command
#     Raises:
#         ValueError: If username or password is None or empty
#         ConnectionError: If connection to remote server fails
#     """
#     # Validate inputs
#     if not username or not password:
#         raise ValueError("Username and password are required")
        
#     # Build a PowerShell script dynamically
#     ps_script = f'''
# $services = @("{'","'.join(services)}")
# $password = ConvertTo-SecureString "{password}" -AsPlainText -Force
# $cred = New-Object System.Management.Automation.PSCredential ("{username}", $password)
# $session = New-PSSession -ComputerName {server} -Credential $cred

# Invoke-Command -Session $session -ScriptBlock {{
#     param([string[]] $servicesList)
#     foreach ($service in $servicesList) {{
#         Write-Host "Checking service: $service"
#         try {{
#             $svc = Get-Service -Name $service -ErrorAction Stop
#             if ($svc.Status -eq "Running") {{
#                 Write-Host "Service '$service' is running."
#             }} else {{
#                 Write-Host "Service '$service' is not running."
#             }}
#         }} catch {{
#             Write-Host "Service '$service' not found or inaccessible."
#         }}
#     }}
# }} -ArgumentList (,$services)

# Remove-PSSession $session
# '''
    
#     # Print the PowerShell command being sent (with sensitive info masked)
#     masked_script = ps_script.replace(password, "********") if password else ps_script
#     print("\n=== PowerShell Command Being Sent ===")
#     print(ps_script)
#     print("===================================\n")

#     # Execute the PowerShell script
#     result = subprocess.run(
#         ["powershell", "-NoProfile", "-Command", ps_script],
#         capture_output=True,
#         text=True
#     )
    
#     # Print the response
#     print("\n=== PowerShell Response ===")
#     print(result.stdout)
#     if result.stderr:
#         print("\n=== PowerShell Errors ===")
#         print(result.stderr)
#     print("===========================\n")
    
#     # Check for connection errors in both stdout and stderr
#     output = result.stdout + result.stderr
#     if "New-PSSession : " in output and "Connecting to remote server" in output and "failed" in output:
#         raise ConnectionError("Failed to connect to remote server. Please logout and re-type your credentials.")
    
#     return result.stdout