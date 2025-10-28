import threading
import sqlite3
import mainServer
import onlineTrackingServer
import os
import time
from GUI import GUI
import argparse
import sys
import socket
import constants

import ping
import discover
import add_host
import delete_host

HOST, PORT = "", 5124
class Server:
    def __init__(self):
        #create and connect to sqlite database
        # if os.path.exists("server.db"):
        #     os.remove("server.db")
        con = sqlite3.connect("server.db", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)                                      
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS hosts(
                    ip text,
                    online boolean  default(FALSE), 
                    primary key(ip));""")
        con.commit()
        cur.execute("""CREATE TABLE IF NOT EXISTS file_host(
                    host text, 
                    file text, 
                    primary key(host, file),
                    foreign key (host) REFERENCES hosts(ip) ON DELETE CASCADE ON UPDATE CASCADE)""")
        con.commit()
        res = cur.execute("SELECT name FROM sqlite_master")
        print(res.fetchall())
        con.close()

        #initialize server and server thread
        self.server = mainServer.ThreadedTCPServer((HOST, PORT), mainServer.ThreadedTCPRequestHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        #initialize heartbeat server and server thread
        self.ot_server = onlineTrackingServer.ThreadedTCPServer((HOST, constants.OT_PORT), onlineTrackingServer.ThreadedTCPRequestHandler)
        self.ot_server_thread = threading.Thread(target=self.ot_server.serve_forever)
        self.ot_server_thread.daemon = True
        self.ot_server_thread.start()

    def add_host(self, ip):
        try:
            add_host.add_host(ip)
        except Exception as e:
            print('[Server Error]', *e.args)
            
    def delete_host(self, ip):
        try:
            delete_host.delete_host(ip)
        except Exception as e:
            print('[Server Error]', *e.args)

    def fetch_peers(self):
        try:
            list_file = mainServer.get_hosts_info()
            if list_file == None:
                return []

            return list_file
        except socket.error as e:
            print("[Server Error] ", *e.args)
        except Exception as e:
            print('[Client Error]', *e.args)

    def ping(self, hostname):
        try:
            print("Ping: " + hostname)
            count = ping.ping_host(hostname)
            print("Ping count: " + str(count))
            return count
        except socket.error as e:
            print("[Server Error] ", *e.args)
            return -1
        except Exception as e:
            print('[Client Error]', *e.args)
            return -1 

    def discover(self, hostname):
        try:
            print("Discover: " + hostname)
            file_list = discover.discover_host(hostname)
            print("Discover list: " + hostname + " " + str(file_list))
            return file_list
        except socket.error as e:
            print("[Server Error] ", *e.args)
        except Exception as e:
            print('[Client Error]', *e.args)

    def stop(self):
        self.server.shutdown()
        self.server_thread.join()

        # if os.path.exists("server.db"):
        #     os.remove("server.db")
        # else:
        #     print("The file does not exist")


if __name__ == "__main__":
    server = Server()
    gui = GUI(server)
    gui.start()

    time.sleep(2)
