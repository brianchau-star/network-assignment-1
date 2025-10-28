import socketserver
import sqlite3
import json

def get_hosts():
    con = sqlite3.connect("server.db")
    cur = con.cursor()
    res = cur.execute("SELECT * FROM hosts")
    res = res.fetchall()
    res = list(map(lambda obj: obj[0], res))
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

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.request.settimeout(10)
        while True:
            try:
                req = str(self.request.recv(1024), 'utf8')
                print(self.client_address, req)
                reqObj = json.loads(req)
                peerAddress = self.client_address
                if reqObj["type"] == "connect":
                    if peerAddress[0] in get_hosts():
                        try:
                            update_online(peerAddress[0])
                            response = {
                                "code": 0,
                                "data": "Update online success"
                            }
                        except Exception as e:
                            response = {
                                "code": 1,
                                "data": "Server Error"
                            }
                            print(e)
                    else:
                        response = {
                            "code": 4,
                            "data": "Unauthorized"
                        }
                elif reqObj["type"] == "disconnect":
                    if peerAddress[0] in get_hosts():
                        try:
                            update_offline(peerAddress[0])
                            response = {
                                "code": 0,
                                "data": "Update offline success"
                            }
                        except:
                            response = {
                                "code": 1,
                                "data": "Server Error"
                            }
                    else:
                        response = {
                            "code": 4,
                            "data": "Unauthorized"
                        }                          
                if reqObj["type"] == "heartbeat":
                    response = {
                        "code": 0,
                        "data": "Heartbeat received"
                    }
                response = json.dumps(response)
                response = bytes(response, 'utf8')
                self.request.sendall(response)
            except (TimeoutError, ConnectionResetError) as e:
                print(e)
                update_offline(peerAddress[0])
                break
            except Exception as e:
                print(e)
                break
    
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass