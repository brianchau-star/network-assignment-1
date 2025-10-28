import socket
import json

def ping_host(host):
    resCount = 0
    pingMessage = {
        "type": "ping"
    }
    pingMessage = bytes(json.dumps(pingMessage), "utf-8")
    pingSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    pingSocket.settimeout(1)
    for i in range(10):
        try:
            pingSocket.sendto(pingMessage, (host, 8501))
            response, peerAddress = pingSocket.recvfrom(1024)
            response = json.loads(response.decode())
            if response["type"] == "pong":
                resCount = resCount + 1
        except Exception as e:
            continue
    
    return resCount

def ping_cmd(args):
    pingCount = ping_host(args.host)
    print("Number of messages received: "+ str(pingCount) + "/10")
            
# print(ping_host("192.168.1.217"))
    