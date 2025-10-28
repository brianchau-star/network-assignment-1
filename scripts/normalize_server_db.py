#!/usr/bin/env python3
import sqlite3
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB = os.path.join(ROOT, 'server', 'server.db')

def main():
    if not os.path.exists(DB):
        print('No server DB at', DB)
        sys.exit(0)
    con = sqlite3.connect(DB)
    cur = con.cursor()
    # Trim whitespace from primary key ip and host columns
    cur.execute("UPDATE hosts SET ip = TRIM(ip)")
    cur.execute("UPDATE file_host SET host = TRIM(host)")
    con.commit()
    rows = list(cur.execute('SELECT ip, online FROM hosts'))
    print('hosts:', rows)
    con.close()
    print('Normalization complete.')

if __name__ == '__main__':
    main()

