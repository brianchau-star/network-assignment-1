import socketserver
import sqlite3
import json
import datetime
import ping
import discover

def get_online_hosts():
    con = sqlite3.connect("server.db")
    cur = con.cursor()
    res = cur.execute("SELECT * FROM hosts WHERE online = TRUE")
    res = res.fetchall()
    res = list(map(lambda obj: obj[0], res))
    con.close()
    return res
    
def insert_file_host(host, file):
    con = sqlite3.connect("server.db")
    cur = con.cursor()
    cur.execute("INSERT INTO file_host(host, file) VALUES (?, ?)", (host, file))
    con.commit()
    con.close()
    
def get_host_from_file(file):
    con = sqlite3.connect("server.db")
    cur = con.cursor()
    res = cur.execute("SELECT host FROM file_host WHERE file=?", (file,))
    res = res.fetchall()
    res = list(map(lambda obj: obj[0], res))
    con.close()
    return res

def delete_file_host(host, file):
    con = sqlite3.connect("server.db")
    cur = con.cursor()
    res = cur.execute("DELETE FROM file_host WHERE host=? AND file=?", (host,file))
    con.commit()
    con.close()
    return res

def list_files():
    con = sqlite3.connect("server.db")
    cur = con.cursor()
    res = cur.execute("SELECT * FROM file_host")
    res = res.fetchall()
    res = set(map(lambda obj: obj[1], res))
    res = list(res)
    con.close()
    return res

def get_hosts_info():
    con = sqlite3.connect("server.db")
    cur = con.cursor()
    res = cur.execute("SELECT * FROM hosts")
    res = res.fetchall()
    res = list(map(lambda obj: (obj[0], obj[1]), res))
    return res

def update_online(host):
    con = sqlite3.connect("server.db")
    cur = con.cursor()
    cur.execute("UPDATE hosts SET online = TRUE WHERE ip = ?", (host,))
    con.commit()
    cur.execute("DELETE FROM file_host WHERE host = ?", (host,))
    con.commit()
    con.close()

def update_offline(host):
    con = sqlite3.connect("server.db")
    cur = con.cursor()
    cur.execute("UPDATE hosts SET online = FALSE WHERE ip = ?", (host,))
    con.commit()
    cur.execute("DELETE FROM file_host WHERE host = ?", (host,))
    con.commit()
    con.close()

# def delete_host(host):
#     con = sqlite3.connect("server.db")
#     cur = con.cursor()
#     res = cur.execute("DELETE FROM file_host WHERE host=?", (host,))
#     con.commit()
#     con.close()
#     return res

def get_file_host(file, host):
    con = sqlite3.connect("server.db")
    cur = con.cursor()
    res = cur.execute("SELECT * FROM file_host WHERE file=? AND host=?", (file, host))
    res = res.fetchone()
    con.close()
    return res

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        req = str(self.request.recv(1024), 'utf8')
        reqObj = json.loads(req)
        print(req, self.client_address[0])
        response = None
        # publish resolve
        if reqObj["type"] == "publish":
            try:
                hosts = get_host_from_file(reqObj["fname"])
                if len(hosts) > 0:
                    response = {
                        "code": 3,
                        "data": "File exists"
                    }
                else:
                    if self.client_address[0] in get_online_hosts():
                        insert_file_host(self.client_address[0], reqObj["fname"])
                        response = {
                            "code": 0,
                            "data": "File {} has been recorded".format(reqObj["fname"])
                        }
                    else:
                        response = {
                            "code": 4,
                            "data": "Unauthorized"
                        }
            except:
                response = {
                    "code": 1,
                    "data": "Server Error"
                }
        # list resolve
        elif reqObj["type"] == "list":
            try:
                files = list_files()
                response = {
                    "code": 0,
                    "data": files
                }
            except:
                response = {
                    "code": 1,
                    "data": "Server Error"
                }
        # fetch resolve
        elif reqObj["type"] == "fetch":
            try:
                response = get_host_from_file(reqObj["fname"])
                response = {
                    "code": 0,
                    "data": response
                }
            except:
                response = {
                    "code": 1,
                    "data": "Server Error"
                }
        # invalid_host resolve
        elif reqObj["type"] == "invalid_host":
            pingCount = ping.ping_host(reqObj["host"])
            # we do not use this response, just add for consistency
            response = {
                "code": 0,
                "data": "OK"
            }
            if pingCount < 8:
                # do something
                update_offline(reqObj["host"])
        # invalid_host_file resolve
        elif reqObj["type"] == "invalid_host_file":
            # we do not use this response, just add for consistency
            response = {
                "code": 0,
                "data": "OK"
            }
            try:
                if len(get_file_host(reqObj["fname"], reqObj["host"])) > 0:
                    list_file = discover.discover_host(reqObj["host"])
                    if reqObj["fname"] not in list_file:
                        delete_file_host(reqObj["host"], reqObj["fname"])
            except Exception as e:
                pingCount = ping.ping_host(reqObj["host"])
                if pingCount < 8:
                    # do something
                    update_offline(reqObj["host"])
        else:
            response = {
                "code": 2,
                "data": "Bad request"
            }
        print(response)
        response = json.dumps(response)
        response = bytes(response, 'utf8')
        self.request.sendall(response)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass
    