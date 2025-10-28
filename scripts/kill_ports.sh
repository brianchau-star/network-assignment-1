#!/usr/bin/env bash
set -euo pipefail

# Kill processes listening on the app's ports (server + peer + agent + OT)
# Ports: 5124 (server), 8500 (peer), 8501 (agent), 8502 (online tracking)

PORTS=(5124 8500 8501 8502)

if ! command -v lsof >/dev/null 2>&1; then
  echo "lsof is required for this script. Install lsof and retry." >&2
  exit 1
fi

get_pids_for_port() {
  local port="$1"
  lsof -ti tcp:"$port" -sTCP:LISTEN 2>/dev/null | awk 'NF'
}

unique_lines() {
  awk 'NF' | sort -u
}

ALL_PIDS=""
for port in "${PORTS[@]}"; do
  pids=$(get_pids_for_port "$port" || true)
  if [ -n "$pids" ]; then
    echo "Port $port in use by PIDs: $pids"
    ALL_PIDS="$ALL_PIDS
$pids"
  else
    echo "Port $port is free"
  fi
done

UNIQ_PIDS=$(printf "%s\n" "$ALL_PIDS" | unique_lines || true)

if [ -z "$UNIQ_PIDS" ]; then
  echo "No processes found on target ports."
  exit 0
fi

echo "Sending TERM to:"
printf "%s\n" "$UNIQ_PIDS"
kill -TERM $UNIQ_PIDS 2>/dev/null || true
sleep 1

LEFT=""
for port in "${PORTS[@]}"; do
  p=$(get_pids_for_port "$port" || true)
  [ -n "$p" ] && LEFT="$LEFT
$p"
done
LEFT=$(printf "%s\n" "$LEFT" | unique_lines || true)

if [ -n "$LEFT" ]; then
  echo "Sending KILL to:"
  printf "%s\n" "$LEFT"
  kill -KILL $LEFT 2>/dev/null || true
fi

echo "Done."
