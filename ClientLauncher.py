import sys
from tkinter import Tk
from Client import Client

if __name__ == "__main__":
    print("[LAUNCHER] Starting RTP Client...")
    try:
        serverAddr = sys.argv[1]
        serverPort = sys.argv[2]
        rtpPort = sys.argv[3]
        fileName = sys.argv[4]
        print(f"[LAUNCHER] Server: {serverAddr}:{serverPort}")
        print(f"[LAUNCHER] RTP Port: {rtpPort}")
        print(f"[LAUNCHER] Video file: {fileName}")
    except:
        print(
            "[Usage: ClientLauncher.py Server_name Server_port RTP_port Video_file]\n"
        )

    root = Tk()

    # Create a new client
    print("[LAUNCHER] Creating client application...")
    app = Client(root, serverAddr, serverPort, rtpPort, fileName)
    app.master.title("RTPClient")
    print("[LAUNCHER] Starting GUI main loop...")
    root.mainloop()
