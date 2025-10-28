import socket
import constants
import json
import sqlite3

def get_fcount():
    con = sqlite3.connect("peer.db")
    cur = con.cursor()

    res = cur.execute("SELECT COUNT(*) FROM file_path")
    count = res.fetchone()
    return count[0]

def get_file_list():
    con = sqlite3.connect("peer.db")
    cur = con.cursor()
    
    res = cur.execute("SELECT fname FROM file_path")
    res = res.fetchall()
    res = list(map(lambda obj: obj[0], res))
    return res

def agent(SERVER_IP):
    agent = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    agent.bind(("", constants.AGENT_PORT))
    print("Agent listen on port", constants.AGENT_PORT)
    while True:
        message, mainServerAddress = agent.recvfrom(1024)
        if mainServerAddress[0] == SERVER_IP:
            message = json.loads(message.decode())
            if message["type"] == "ping":
                print("Ping from server, count: ", get_fcount())
                response = {
                    "type": "pong",
                    "fcount": get_fcount()
                }
            elif message["type"] == "discover":
                res = get_file_list()
                print("Discovered from server", res)
                response = {
                    "type": "discover",
                    "list": res
                }
            response = bytes(json.dumps(response), 'utf-8')
            agent.sendto(response, mainServerAddress)    
        
    