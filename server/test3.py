import socket as s

clientSocket = s.socket(s.AF_INET, s.SOCK_STREAM)
try:
    clientSocket.connect(("127.0.0.1", 9999))
except ConnectionError:
    print("r Error")
except TimeoutError:
    print("Error")