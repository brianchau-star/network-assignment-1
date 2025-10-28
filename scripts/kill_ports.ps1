# Kill processes listening on the app's ports (server + peer + agent + OT)
# Ports: 5124 (server), 8500 (peer), 8501 (agent), 8502 (online tracking)

param(
  [int[]]$Ports = @(5124, 8500, 8501, 8502)
)

function Kill-PortPids($port) {
  try {
    $conns = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if (-not $conns) {
      Write-Host "Port $port is free"
      return
    }
    $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique
    if ($pids) {
      Write-Host "Port $port in use by PIDs: $($pids -join ', ')"
      foreach ($pid in $pids) {
        try { Stop-Process -Id $pid -ErrorAction SilentlyContinue } catch {}
      }
    }
  } catch {
    # Fallback to netstat parsing (older PowerShell)
    $lines = & netstat -ano | Select-String ":$port" | ForEach-Object { $_.ToString() }
    if ($lines) {
      $pids = @()
      foreach ($line in $lines) {
        $parts = $line -split '\s+'
        if ($parts.Length -ge 5) { $pids += $parts[-1] }
      }
      $pids = $pids | Sort-Object -Unique
      if ($pids) {
        Write-Host "Port $port in use by PIDs: $($pids -join ', ')"
        foreach ($pid in $pids) {
          try { Stop-Process -Id $pid -ErrorAction SilentlyContinue } catch {}
        }
      } else {
        Write-Host "Port $port is free"
      }
    } else {
      Write-Host "Port $port is free"
    }
  }
}

foreach ($p in $Ports) { Kill-PortPids $p }

Write-Host "Done."

