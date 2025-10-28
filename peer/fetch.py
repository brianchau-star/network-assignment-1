import socket
import os
import json
import constants

def fetch(args):
    ips = getAdd(args.fname)
    loadFile(ips, args.fname)

def getAdd(filename):
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((constants.SERVER_IP, constants.SERVER_PORT))
    req = {
        "type": "fetch",
        "fname": filename
    }
    reqJSON = json.dumps(req)
    clientSocket.sendall(bytes(reqJSON, "utf-8"))
    res = clientSocket.recv(1024)
    res = res.decode()
    res = json.loads(res)
    clientSocket.close()
    if res["code"] == 0:
        return res["data"]
    else:
        print(res["data"])

def loadFile(ips, filename):
    peerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    req = {
        "type": "load",
        "fname": filename
    }
    peerSocket.settimeout(1)
    for ip in ips:
        if os.path.exists("./repo"+filename):
            break
        try:
            peerSocket.connect((ip, constants.PEER_PORT))
            reqJSON = json.dumps(req)
            peerSocket.sendall(bytes(reqJSON, "utf-8"))
            res = peerSocket.recv(1024)
            res = res.decode()
            res = json.loads(res)
            peerSocket.close()
            if res["code"] == 1:
                raise FileNotFoundError(res["data"])
            elif res["code"] == 2:
                raise RuntimeError(res["data"])
            elif res["code"] == 0:
                with open("./repo/" + filename, "w") as file:
                    file.write(res["data"])
        except ConnectionError as e:
            clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientSocket.connect((constants.SERVER_IP, constants.SERVER_PORT))
            req = {
                "type": "invalid_host",
                "host": ip
            }
            reqJSON = json.dumps(req)
            clientSocket.sendall(bytes(reqJSON, "utf-8"))
            clientSocket.close()
            print(e + "on peer " + ip)
            print("Trying another peer...")
        except TimeoutError as e:
            clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientSocket.connect((constants.SERVER_IP, constants.SERVER_PORT))
            req = {
                "type": "invalid_host",
                "host": ip
            }
            reqJSON = json.dumps(req)
            clientSocket.sendall(bytes(reqJSON, "utf-8"))
            clientSocket.close()
            print(e + "on peer " + ip)
            print("Trying another peer...")
        except FileNotFoundError as e:
            clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientSocket.connect((constants.SERVER_IP, constants.SERVER_PORT))
            req = {
                "type": "invalid_host_file",
                "host": ip,
                "fname": filename
            }
            reqJSON = json.dumps(req)
            clientSocket.sendall(bytes(reqJSON, "utf-8"))
            clientSocket.close()
            print(e + "on peer " + ip)
            print("Trying another peer...")
        except RuntimeError as e:
            print(e + "on peer " + ip)
            print("Trying another peer...")
            
