import subprocess

def check_services_powershell(username, password, server, services):
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
    masked_script = ps_script.replace(password, "********")
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
    
    return result.stdout