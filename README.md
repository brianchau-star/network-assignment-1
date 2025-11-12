# P2P File Sharing System

A peer-to-peer file sharing system with a central server for peer discovery and direct P2P file transfers.

## System Architecture

- **Server**: Central registry for peer discovery and file location
- **Client**: Peer nodes that can publish and download files directly from other peers

## Prerequisites

- Python 3.x
- Network connectivity between server and clients

## Setup and Running

### Starting the Server

```bash
cd server
python server.py --server_host <SERVER_IP>
```

**Arguments:**
- `--server_host`: Server IP address (default: `10.128.17.239`)

**Example:**
```bash
python server.py --server_host 192.168.1.100
```

### Starting the Client

```bash
cd client1
python client.py --hostname <CLIENT_NAME> --server_host <SERVER_IP>
```

**Arguments:**
- `--hostname`: Unique name for this client (required)
- `--server_host`: Server IP address (default: `10.128.17.239`)

**Example:**
```bash
python client.py --hostname client1 --server_host 192.168.1.100
```

## Server CLI Commands

Once the server is running, you can use the following commands:

### `ping <hostname>`
Test connection to a specific client.

**Example:**
```
> ping client1
```

### `discover <hostname>`
List all files published by a specific client.

**Example:**
```
> discover client1
```
**Output:**
```
Files from host client1:
File name: test.txt, file path: ./documents
File name: image.png, file path: ./images
```

### `exit`
Shutdown the server.

**Example:**
```
> exit
```

## Client CLI Commands

Once connected to the server, clients can use the following commands:

### `publish <file_path> <file_name>`
Publish a file to make it available for other peers to download.

**Syntax:**
```
publish <file_path> <file_name>
```

**Examples:**
```
> publish ./documents test.txt
> publish . readme.md
> publish C:\Users\files data.csv
```

**Note:** If the file is in the current directory, you can use `.` as the path.

### `fetch <file_name>`
Search for a file and get a list of peers that have it.

**Syntax:**
```
fetch <file_name>
```

**Example:**
```
> fetch test.txt
```

**Output:**
```
Select peer to download file test.txt from:

0) Hostname: client2, IP: 192.168.1.101, Port: 7735, File Path: ./documents
1) Hostname: client3, IP: 192.168.1.102, Port: 7736, File Path: ./shared

Select option > 
```

After displaying options, enter the number of the peer you want to download from:
```
Select option > 0
```

### `list peers`
Display all available peers in the network.

**Example:**
```
> list peers
```

**Output:**
```
1) Hostname: client2, IP: 192.168.1.101, Port: 7735, Upload port: 8001
2) Hostname: client3, IP: 192.168.1.102, Port: 7736, Upload port: 8002
```

### `list files`
Display all available files from other peers.

**Example:**
```
> list files
```

**Output:**
```
1) File name: test.txt, File path: ./documents, Host: client2, IP: 192.168.1.101, Upload port: 8001
2) File name: data.csv, File path: ./shared, Host: client3, IP: 192.168.1.102, Upload port: 8002
```

### `exit`
Disconnect from the server and shutdown the client.

**Example:**
```
> exit
```

## Complete Usage Example

### Scenario: Client1 wants to download a file from Client2

**Step 1: Start Server**
```bash
cd server
python server.py --server_host 192.168.1.100
```

**Step 2: Start Client2 (File Provider)**
```bash
cd client1
python client.py --hostname client2 --server_host 192.168.1.100
```

**Step 3: Client2 publishes a file**
```
> publish ./documents test.txt
```

**Step 4: Start Client1 (File Requester)**
```bash
cd client1
python client.py --hostname client1 --server_host 192.168.1.100
```

**Step 5: Client1 searches for the file**
```
> fetch test.txt
```

**Output:**
```
Select peer to download file test.txt from:

0) Hostname: client2, IP: 192.168.1.101, Port: 7735, File Path: ./documents

Select option > 
```

**Step 6: Client1 selects peer and downloads**
```
Select option > 0
```

**Output:**
```
Downloading file test.txt from client2...
Downloaded file test.txt from client2 in 0.523s.
```

## File Transfer Details

- Files are transferred directly between peers (P2P)
- The server only facilitates peer discovery
- Downloaded files are saved to the same path structure as published
- Upload/download progress is displayed in the console

## Network Configuration

- Default server port: `7734`
- Client upload ports are dynamically assigned
- Ensure firewall allows connections on these ports

## Troubleshooting

### Client cannot connect to server
- Verify server IP address is correct
- Ensure server is running
- Check firewall settings

### File not found during download
- Verify the file still exists on the peer's system
- Check if the peer is still online
- Ensure the file path is correct

### Peer disconnection
- The server automatically detects and removes disconnected peers
- File references from disconnected peers are cleaned up automatically

## Notes

- Each client must have a unique hostname
- File paths use forward slashes (`/`) internally
- The system supports multiple clients downloading the same file simultaneously
- File metadata (OS, content type, size) is transmitted during downloads
