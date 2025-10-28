#!/usr/bin/env bash
set -euo pipefail

# Run the server GUI (listens on 5124 and 8502)
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
cd "$ROOT_DIR/server"

exec python3 main.py

