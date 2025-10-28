param(
  [string]$ServerIP = "127.0.0.1"
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Resolve-Path (Join-Path $ScriptDir ".."); $RootDir = $RootDir.Path

function Start-Window($title, $command) {
  $ps = "-NoExit -Command `$Host.UI.RawUI.WindowTitle='$title'; $command"
  Start-Process -FilePath powershell -ArgumentList $ps -WindowStyle Normal
}

function PythonCmd { if (Get-Command python -ErrorAction SilentlyContinue) { return "python" } elseif (Get-Command py -ErrorAction SilentlyContinue) { return "py -3" } else { throw "Python not found in PATH" } }

$py = PythonCmd

# Server
$srvCmd = "Set-Location '$RootDir/server'; $py main.py"
Start-Window -title "P2P Server" -command $srvCmd
Start-Sleep -Seconds 1

# Peer
$peerCmd = "Set-Location '$RootDir/peer'; $py main.py -s $ServerIP"
Start-Window -title "P2P Peer" -command $peerCmd
Start-Sleep -Seconds 1

# Client
$clientCmd = "Set-Location '$RootDir/client'; $py main.py -s $ServerIP"
Start-Window -title "P2P Client" -command $clientCmd

Write-Host "Launched server, peer, and client."

