from GUI import GUI
from client import Client
import argparse

SERVER_PORT = 5124
PEER_PORT = 8500

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--server", type=str, default='localhost', help="Specify the port number")
    args = parser.parse_args()

    client = Client(args.server, SERVER_PORT, PEER_PORT)
    gui = GUI(client)
    gui.start()
