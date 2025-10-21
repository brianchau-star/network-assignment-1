import sys, socket
import logging

from ServerWorker import ServerWorker
logger = logging.getLogger("Server")


class Server:

    def main(self):
        logger.info("Starting RTSP Server")

        try:
            SERVER_PORT = int(sys.argv[1])
            logger.info(f"Server port: {SERVER_PORT}")
        except:
            logger.error("Invalid server port argument")
            print("[Usage: Server.py Server_port]\n")
            return

        try:
            rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            rtspSocket.bind(("", SERVER_PORT))
            rtspSocket.listen(5)
            logger.info(f"RTSP server listening on port {SERVER_PORT}")
        except Exception as e:
            logger.error(f"Failed to start server: {str(e)}")
            return

        # Receive client info (address,port) through RTSP/TCP session
        client_count = 0
        while True:
            try:
                clientInfo = {}
                clientInfo["rtspSocket"] = rtspSocket.accept()
                client_count += 1
                client_addr = clientInfo["rtspSocket"][1][0]
                client_port = clientInfo["rtspSocket"][1][1]

                logger.info(
                    f"Client #{client_count} connected from {client_addr}:{client_port}"
                )

                ServerWorker(clientInfo).run()

            except KeyboardInterrupt:
                logger.info("Server shutdown requested")
                break
            except Exception as e:
                logger.error(f"Error handling client connection: {str(e)}")


if __name__ == "__main__":
    (Server()).main()
