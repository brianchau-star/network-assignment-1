import socket
import json
import os
import base64
import io
import sys
from pathlib import Path

class Client:
    def __init__(self, SERVER_HOST, SERVER_PORT, PEER_PORT):
        self.SERVER_HOST = SERVER_HOST
        self.SERVER_PORT = SERVER_PORT
        self.PEER_PORT = PEER_PORT

    def fetch_list(self):
        try:
            print("Fetching list...")
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(10)
            req = {
                "type": "list"
            }

            client_socket.connect((self.SERVER_HOST, self.SERVER_PORT))
            reqJSON = json.dumps(req)
            client_socket.sendall(bytes(reqJSON, "utf-8"))

            received_bytes = client_socket.recv(1024)
            resJSON = b''
            while received_bytes:
                resJSON += received_bytes
                received_bytes = client_socket.recv(1024)

            resJSON = resJSON.decode('utf-8')
            res = json.loads(resJSON)

            client_socket.close()

            print("File list fetched.")
            return res["data"]
        except socket.error as e:
            print("[Server Error] ", *e.args)
        except Exception as e:
            print('[Client Error] ', *e.args)

    def download_file(self, selected_file, save_location):
        try: 
            if (selected_file == None or len(selected_file) <= 0):
                raise Exception("[File empty]", "Please choose a file")

            ips = self.get_ips(selected_file)
            self.load_file(ips, selected_file, save_location)
        except socket.error as e:
            print("[Server Error]", *e.args)
        except IOError as e:
            print("[Client Error]", "Cannot write file to file path.")
        except Exception as e:
            print('[Client Error] ', *e.args)

    def get_ips(self, filename):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(10)
        client_socket.connect((self.SERVER_HOST, self.SERVER_PORT))
        req = {
            "type": "fetch",
            "fname": filename
        }
        reqJSON = json.dumps(req)
        client_socket.sendall(bytes(reqJSON, "utf-8"))
        res = client_socket.recv(1024)
        res = res.decode()
        res = json.loads(res)
        client_socket.close()
        if res["code"] == 0:
            return res["data"]
        raise Exception("Client Error", res["data"])

    def load_file(self, ips, filename, save_location):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(10)
        req = {
            "type": "load",
            "fname": filename
        }
        delimiter = b"\r\n\r\n"

        for ip in ips:
            if os.path.exists(save_location):
                os.remove(save_location)
            print(f"Trying to download from {ip}")
            try:
                client_socket.connect((ip, self.PEER_PORT))
                reqJSON = json.dumps(req)
                client_socket.sendall(bytes(reqJSON, "utf-8"))
                res = b''
                res = client_socket.recv(1024)
                res_list = res.split(delimiter, 1)
                header = res_list[0]
                binary_content = len(res_list) > 1 and res_list[1] or b''
                header = header.decode()
                header = json.loads(header)
                if header["code"] == 1:
                    raise FileNotFoundError(header["data"])
                elif header["code"] == 2:
                    raise RuntimeError(header["data"])
                elif header["code"] == 0:
                    file_length = header["length"]
                    file_length = int(file_length)

                    # For tracking purposes
                    current_file_length=0

                    with open(save_location, "wb") as file:
                        if binary_content:
                            file.write(binary_content)
                            current_file_length += len(binary_content)
                        file_stream = client_socket.recv(1024)
                        while file_stream:
                            current_file_length += len(file_stream)
                            file.write(file_stream)
                            file_stream = client_socket.recv(1024)
                        file.flush()

                    if os.path.getsize(save_location) < file_length:
                        if os.path.exists(save_location):
                            os.remove(save_location)
                        print(f"Download failed (length = {current_file_length}/{file_length}) ")
                        continue

                    print(f"Download succeeded {filename} (length = {current_file_length}/{file_length})")

                client_socket.close()
                return
            except (ConnectionError, TimeoutError) as e:  
                connectionSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                connectionSocket.connect((self.SERVER_HOST, self.SERVER_PORT))
                req = {
                    "type": "invalid_host",
                    "host": ip
                }
                reqJSON = json.dumps(req)
                connectionSocket.sendall(bytes(reqJSON, "utf-8"))
                connectionSocket.close()
                print("[Peer error] ", *e.args)
            except FileNotFoundError as e:
                fileNotFoundSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                fileNotFoundSocket.connect((self.SERVER_HOST, self.SERVER_PORT))
                req = {
                    "type": "invalid_host_file",
                    "host": ip,
                    "fname": filename
                }
                reqJSON = json.dumps(req)
                fileNotFoundSocket.sendall(bytes(reqJSON, "utf-8"))
                fileNotFoundSocket.close()
                print("[Peer error] ", *e.args)
            except socket.error as e:  
                connectionSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                connectionSocket.connect((self.SERVER_HOST, self.SERVER_PORT))
                req = {
                    "type": "invalid_host",
                    "host": ip
                }
                reqJSON = json.dumps(req)
                connectionSocket.sendall(bytes(reqJSON, "utf-8"))
                connectionSocket.close()
                print("[Peer error] ", *e.args)
            except RuntimeError as e:
                print("[Peer error] ", *e.args)
        client_socket.close()
        print("No peer available.")

    def shutdown(self):
        print("Shutting down...")

