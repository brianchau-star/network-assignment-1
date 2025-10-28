import sqlite3
import ping

def add_host(ip):
    ping_count = ping.ping_host(ip)
    is_online = ping_count > 8 
    print("Ping count: " + str(ping_count))
    con = sqlite3.connect("server.db")
    cur = con.cursor()
    cur.execute("INSERT INTO hosts(ip,online) VALUES (?,?)", (ip,is_online))
    con.commit()
    con.close()
    print("Host: {} has been added".format(ip,))
    
def add_cmd(args):
    try:
        add_host(args.hostname, args.ip)
    except Exception as e:
        print(e)
