import sqlite3

def delete_host(ip):
    ip = ip.strip()
    con = sqlite3.connect("server.db")
    cur = con.cursor()
    cur.execute("DELETE FROM hosts WHERE TRIM(ip) = ?", (ip,))
    con.commit()
    cur.execute("DELETE FROM file_host WHERE TRIM(host) = ?", (ip,))
    con.commit()
    con.close()
    print("Host: {} has been deleted".format(ip,))
    
