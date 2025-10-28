import socket
import sqlite3
import constants
import json

def insert_repo(fname, path):
    con = sqlite3.connect("peer.db")
    cur = con.cursor()
    cur.execute("INSERT INTO file_path(fname, path) VALUES (?, ?)", (fname, path))
    con.commit()
    con.close()

def publish(SERVER_IP, fname, lname):
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.settimeout(10)
    clientSocket.connect((SERVER_IP, constants.SERVER_PORT))
    req = {
        "type": "publish",
        "fname": fname
    }
    reqJSON = json.dumps(req)
    clientSocket.sendall(bytes(reqJSON, "utf8"))
    res = clientSocket.recv(1024)
    res = res.decode()
    res = json.loads(res)
    clientSocket.close()
    if res["code"] == 0:
        insert_repo(fname, lname)
        print(res["data"])
    elif res["code"] == 1:
        raise RuntimeError(res["data"])
    elif res["code"] == 2:
        raise SyntaxError(res["data"])
    elif res["code"] == 3:
        raise Exception("File exists, can not publish")
    elif res["code"] == 4:
        raise Exception(res["data"])
