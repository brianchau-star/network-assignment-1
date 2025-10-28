# import socket
# import json
# import sqlite3
# import constants


# class NMP_server:
#     def __init__(self, port):
#         self.port = port 

#     def start(self):
#         self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.server.bind(("", constants.AGENT_PORT))
#         while True:
#             message, peerAddress = self.server.recvfrom(1024)
#             if peerAddress[0] in get_hosts():
#                 message = json.loads(message.decode())
#                 if message["type"] == "connect":
#                     try:
#                         update_online(peerAddress[0])
#                         response = {
#                             "type": "Connected",
#                             "data": "Update online success"
#                         }
#                     except Exception as e:
#                         response = {
#                             "type": "Error",
#                             "data": "Server Error"
#                         }
#                         print(e)
#                 elif message["type"] == "disconnect":
#                     try:
#                         update_offline(peerAddress[0])
#                         response = {
#                             "code": "Disconnected",
#                             "data": "Update offline success"
#                         }
#                     except:
#                         response = {
#                             "type": "Error",
#                             "data": "Server Error"
#                         }
#                 response = bytes(json.dumps(response), 'utf-8')
#                 self.server.sendto(response, peerAddress)  
