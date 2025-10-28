import sqlite3

def delete_host(ip):
    con = sqlite3.connect("server.db")
    cur = con.cursor()
    cur.execute("DELETE FROM hosts WHERE ip = ?", (ip,))
    con.commit()
    cur.execute("DELETE FROM file_host WHERE host = ?", (ip,))
    con.commit()
    con.close()
    print("Host: {} has been deleted".format(ip,))
    