import sys, socket

from ServerWorker import ServerWorker


class Server:

    def main(self):
        try:
            SERVER_PORT = int(sys.argv[1])
            print(f"[SERVER] Starting server on port {SERVER_PORT}")
        except:
            print("[Usage: Server.py Server_port]\n")
        rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        rtspSocket.bind(("", SERVER_PORT))
        rtspSocket.listen(5)
        print(f"[SERVER] Server listening on port {SERVER_PORT}")

        # Receive client info (address,port) through RTSP/TCP session
        while True:
            print("[SERVER] Waiting for client connections...")
            clientInfo = {}
            clientInfo["rtspSocket"] = rtspSocket.accept()
            client_addr = clientInfo["rtspSocket"][1]
            print(f"[SERVER] New client connected from {client_addr[0]}:{client_addr[1]}")
            ServerWorker(clientInfo).run()


if __name__ == "__main__":
    (Server()).main()
