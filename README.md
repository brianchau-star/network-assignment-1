# P2P File Sharing

This repository contains a simple P2P file sharing demo with three components:

- Server GUI: manages peers and tracks files
- Peer GUI: publishes local files and serves downloads
- Client GUI: lists files and downloads from peers

Default ports:

- Server: `5124`
- Peer server: `8500`
- Agent (UDP): `8501`
- Online tracking server: `8502`

Note: Prefer using Python entry points in this repo over bundled binaries to avoid platform or config mismatch.

## Requirements

- Python 3.8+ with Tkinter available
- macOS or Windows
- Open ports `5124`, `8500`, `8501`, `8502`

## Quick Start (macOS)

1) Make scripts executable (first run only):

```
chmod +x scripts/*.sh
```

2) Launch all three apps (server → peer → client) in Terminal windows:

```
./scripts/run_all_mac.sh 127.0.0.1
```

Optional: clean up any busy ports first:

```
CLEAN=1 ./scripts/run_all_mac.sh 127.0.0.1
```

3) In the Server GUI, add the peer IP as `127.0.0.1`. Then use the Peer GUI to Publish a file, and the Client GUI to Fetch/Download.

Run each component separately if preferred:

```
./scripts/run_server.sh
./scripts/run_peer.sh 127.0.0.1
./scripts/run_client.sh 127.0.0.1
```

## Quick Start (Windows)

Run from PowerShell (allow execution policy for local scripts):

```
powershell -ExecutionPolicy Bypass -File scripts/run_all_windows.ps1 -ServerIP 127.0.0.1
```

This opens three PowerShell windows for server, peer, and client. In the Server GUI, add the peer IP as `127.0.0.1`.

Run each component separately if preferred:

```
powershell -ExecutionPolicy Bypass -Command "Set-Location server; python main.py"
powershell -ExecutionPolicy Bypass -Command "Set-Location peer; python main.py -s 127.0.0.1"
powershell -ExecutionPolicy Bypass -Command "Set-Location client; python main.py -s 127.0.0.1"
```

## Port Cleanup

If a port is already in use or after a previous crash, clean up:

- macOS/Linux:

```
./scripts/kill_ports.sh
```

- Windows (PowerShell):

```
powershell -ExecutionPolicy Bypass -File scripts/kill_ports.ps1
```

## Notes and Troubleshooting

- Always add the peer using a numeric IP like `127.0.0.1` instead of `localhost` to match what the server stores.
- If the Peer shows "Can not connect to server" or the Server shows `Unauthorized` for `connect`:
  - Ensure the Server is running and listening on `8502`.
  - Ensure the peer IP was added in the Server GUI (IP must match exactly).
  - Clean ports with the scripts above and relaunch.
- If Tkinter is missing on your Python, install a Python build that includes Tk (e.g., from python.org).

## Legacy Binaries

The repo includes macOS arm64 binaries in `client/client` and `peer/peer`. These may not match your environment. The provided scripts prefer Python entry points; to force using the binaries, set `USE_BINARY=1` before running the script, e.g.:

```
USE_BINARY=1 ./scripts/run_peer.sh 127.0.0.1
```
