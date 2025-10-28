#!/usr/bin/env bash
set -euo pipefail

# Open three Terminal windows on macOS for server, peer, client
# Usage: scripts/run_all_mac.sh [SERVER_IP]

SERVER_IP="${1:-${SERVER_IP:-127.0.0.1}}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"

if ! command -v osascript >/dev/null 2>&1; then
  echo "osascript not found. This launcher is for macOS only." >&2
  exit 1
fi

# Optional cleanup of busy ports before launch
if [[ "${CLEAN:-0}" == "1" ]]; then
  if [[ -x "$ROOT_DIR/scripts/kill_ports.sh" ]]; then
    "$ROOT_DIR/scripts/kill_ports.sh" || true
  fi
fi

# Note: paths are quoted to survive spaces. Server starts first.
osascript <<OSA
tell application "Terminal"
  do script "cd " & quoted form of POSIX path of "$ROOT_DIR/server" & "; python3 main.py"
  delay 0.2
  do script "cd " & quoted form of POSIX path of "$ROOT_DIR/peer" & "; python3 main.py -s $SERVER_IP"
  delay 0.2
  do script "cd " & quoted form of POSIX path of "$ROOT_DIR/client" & "; python3 main.py -s $SERVER_IP"
  activate
end tell
OSA

echo "Launched server, peer, and client in Terminal."
