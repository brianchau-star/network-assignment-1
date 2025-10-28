import socket
import constants
import json

def connect(SERVER_IP):
    connectSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connectSocket.settimeout(10)
    req = {
        "type": "connect"
    }
    reqJSON = bytes(json.dumps(req), "utf-8")
    try:
        connectSocket.connect((SERVER_IP, constants.OT_PORT))
        connectSocket.sendall(reqJSON)
        response = connectSocket.recv(1024)
        response = json.loads(response.decode())
        if(response["code"] == 0):
            print("Connected to server")
        else:
            raise Exception(response["data"])
        return connectSocket
    except Exception as e:
        print("Can not connect to server")
        print(e)
        return None
    