import argparse
import sys
import threading
import sqlite3
import os

import fetch
import publish
import constants
import socket
import peerServer
from GUI import GUI
import agent
import connect
import disconnect
import sys
import heartbeat

class Peer:
    def __init__(self, SERVER_IP):
        self.SERVER_IP = SERVER_IP
        #connect to the main server
        self.connectionSocket = connect.connect(self.SERVER_IP)
        if not self.connectionSocket:
            sys.exit(0)

        #create a local repo, which stores local path and fname
        if os.path.exists("peer.db"):
            os.remove("peer.db")
        con = sqlite3.connect("peer.db", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)                                      
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS file_path(
                    fname text,
                    path text, 
                    primary key (fname))""")
        con.commit()
        res = cur.execute("SELECT name FROM sqlite_master")
        print(res.fetchall())
        con.close()

        #ping server for the main server to ping
        self.agent_server_thread = threading.Thread(target=agent.agent, args=(self.SERVER_IP,))
        self.agent_server_thread.daemon = True
        self.agent_server_thread.start()

        #peer server for other peers get file
        self.peer_server = peerServer.ThreadedTCPServer(("", constants.PEER_PORT), peerServer.ThreadedTCPRequestHandler)
        self.peer_server_thread = threading.Thread(target=self.peer_server.serve_forever)
        self.peer_server_thread.daemon = True
        self.peer_server_thread.start()
        
        self.heartbeat_thread = threading.Thread(target=heartbeat.send_heartbeat, args=(self.connectionSocket,))
        self.heartbeat_thread.daemon = True
        self.heartbeat_thread.start()

    def publish(self, fname, path):
        try:
            print("publishing", fname, path)
            publish.publish(self.SERVER_IP, fname, path)
        except socket.error as e:
            print("[Server Error] ", *e.args)
            return []
        except Exception as e:
            print('[Client Error]', *e.args)
            
            return []

    def fetch_local_list(self):
        con = sqlite3.connect("peer.db")
        cur = con.cursor()
        
        list_file = cur.execute("SELECT * FROM file_path")
        list_file = list_file.fetchall()
        list_file = list(map(lambda obj: (obj[0], obj[1]), list_file))
        if list_file is None:
            return []
        return list_file

    def stop(self):
        self.peer_server.shutdown()
        self.peer_server_thread.join()
        disconnect.disconnect(self.connectionSocket)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--server", type=str, default='localhost', help="Specify the port number")
    args = parser.parse_args()

    peer = Peer(args.server)
    gui = GUI(peer)
    gui.start()

