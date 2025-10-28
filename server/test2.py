import socket as s

HOST = ""
PORT = 5124

serverSocket = s.socket(s.AF_INET, s.SOCK_STREAM)
serverSocket.bind(("", PORT))
serverSocket.listen(1)
print("Server listening on port", PORT)
while True:
    connectionSocket, addr = serverSocket.accept()
    sentence = connectionSocket.recv(1024).decode()
    print(sentence)
    connectionSocket.send("Hello from server".encode()) 
    connectionSocket.close()
    break
serverSocket.close()