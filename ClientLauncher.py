import sys
import logging
from tkinter import Tk
from Client import Client

logger = logging.getLogger("ClientLauncher")

if __name__ == "__main__":
    logger.info("Starting RTP Client Application")

    try:
        serverAddr = sys.argv[1]
        serverPort = sys.argv[2]
        rtpPort = sys.argv[3]
        fileName = sys.argv[4]

        logger.info(
            f"Arguments parsed - Server: {serverAddr}:{serverPort}, RTP Port: {rtpPort}, File: {fileName}"
        )

    except:
        error_msg = (
            "[Usage: ClientLauncher.py Server_name Server_port RTP_port Video_file]\n"
        )
        logger.error("Invalid arguments provided")
        print(error_msg)
        sys.exit(1)

    try:
        root = Tk()
        logger.info("Tkinter root window created")

        # Create a new client
        app = Client(root, serverAddr, serverPort, rtpPort, fileName)
        app.master.title("RTPClient")
        logger.info("Client application initialized successfully")

        root.mainloop()
        logger.info("Application terminated")

    except Exception as e:
        logger.error(f"Failed to start client application: {str(e)}")
        sys.exit(1)
