import fetch
import socket
import json

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
req = {
    "type": "list"
}

client_socket.connect(("192.168.1.217", 5124))
reqJSON = json.dumps(req)
client_socket.sendall(bytes(reqJSON, "utf-8"))

received_bytes = client_socket.recv(1024)
print(received_bytes.decode())

