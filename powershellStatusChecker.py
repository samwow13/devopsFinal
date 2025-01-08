import subprocess

def check_services_powershell(username, password, server, services):
    # Build a PowerShell script dynamically
    ps_script = f'''
$services = @("{'","'.join(services)}")
$password = ConvertTo-SecureString "{password}" -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ("{username}", $password)
$session = New-PSSession -ComputerName {server} -Credential $cred

Invoke-Command -Session $session -ScriptBlock {{
    param([string[]] $servicesList)s
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

    # Execute the PowerShell script
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps_script],
        capture_output=True,
        text=True
    )
    return result.stdout