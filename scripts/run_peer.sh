#!/usr/bin/env bash
set -euo pipefail

# Run the peer GUI (connects to server OT port 8502)
# Usage: scripts/run_peer.sh [SERVER_IP]

SERVER_IP="${1:-${SERVER_IP:-127.0.0.1}}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
cd "$ROOT_DIR/peer"

# Prefer Python version to avoid mismatched compiled binary behavior.
# Set USE_BINARY=1 to use bundled binary instead.
if [[ "${USE_BINARY:-0}" == "1" && -x ./peer ]]; then
  exec ./peer -s "$SERVER_IP"
else
  exec python3 main.py -s "$SERVER_IP"
fi
