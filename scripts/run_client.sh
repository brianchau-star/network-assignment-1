#!/usr/bin/env bash
set -euo pipefail

# Run the client GUI (fetches file list from server port 5124 and downloads from peer on 8500)
# Usage: scripts/run_client.sh [SERVER_IP]

SERVER_IP="${1:-${SERVER_IP:-127.0.0.1}}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
cd "$ROOT_DIR/client"

# Prefer Python version to avoid mismatched compiled binary behavior.
# Set USE_BINARY=1 to use bundled binary instead.
if [[ "${USE_BINARY:-0}" == "1" && -x ./client ]]; then
  exec ./client -s "$SERVER_IP"
else
  exec python3 main.py -s "$SERVER_IP"
fi
