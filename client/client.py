import socket
import threading
import os
import sys
import argparse
import time
import mimetypes
import platform

from client_helper import parse_client_cmd, parse_server_response, MyException
from pathlib import Path

class Client():
    def __init__(
        self, 
        hostname,
        server_host, 
        server_port=7734, 

    ):
        self.server_host = server_host
        self.server_port = server_port
        
        self.hostname = hostname
        
        self.is_selecting_peer = False
        self.peer_options = {}
        self.upload_port = None
        
    def start(self):
        """
            Start the client
        """
        print('Start connecting to the server on %s:%s' % (self.server_host, self.server_port))
        
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            if(not self.hostname):
                raise Exception('Hostname is empty')
            
            # TODO: Fetch hostname from the system, if exists then terminate the program
            self.server.connect((self.server_host, self.server_port))
            
        except Exception as e:
            print(e)
            self.shutdown()
        
        # Init upload to start listening for peers, as well as setting upload port
        self.init_upload_thread = threading.Thread(target=self.init_upload)
        self.init_upload_thread.start()
        
        # Wait for the upload port to be set. Could use thread.join()
        while not self.upload_port:
            pass
        
        self.set_host_addresses()
        
        print(f'Start listening for peers on port {self.upload_port}')
        
        # Start a new thread for cli
        self.cli_thread = threading.Thread(target=self.cli)
        self.cli_thread.start()
                
        while True:
            try:
                data = self.server.recv(1024).decode()
                
                if data:
                    method, payload = parse_server_response(data)
                    # If the method is print, then print the payload
                    if(method == 'print'):
                        inputStr = 'Select option > ' if self.is_selecting_peer else '> '
                        print(data + '\n' + inputStr, end = '', flush=True)
                    # Else if the method is defined in the client, then call it
                    elif(hasattr(self, method) and callable(getattr(self, method))):
                        getattr(self, method)(payload)
                    
            except Exception as e:
                print(e)
                break
            except BaseException:
                print('Client is shutting down...')
                self.shutdown()
                break
       
    def set_host_addresses(self):
        try:            
            # TODO: Fetch hostname from the system, if exists then terminate the program
            message = 'SET_HOST_ADDRESSES\n' + self.hostname + '\n' + str(self.upload_port)
            self.server.send(message.encode())
        except Exception as e:
            print(e)
            self.shutdown()
                  
    def cli(self):
        while True:
            inputStr = 'Select option > ' if self.is_selecting_peer else '> '
            
            try:
                command = input(inputStr)
                
                if command == '':
                    continue
                
                method, payload = parse_client_cmd(command, self.is_selecting_peer,  self.peer_options)
                
                if hasattr(self, method) and callable(getattr(self, method)):
                    getattr(self, method)(payload)
                
                self.is_selecting_peer = False
                self.peer_options = {}

            except Exception as e:
                print(e)
            except BaseException:
                print('Client is shutting down...')
                self.shutdown()
            
    def publish_file_info(self, payload):
        file_path, file_name = payload
        
        self.create_folder_if_not_exists(file_path)
        file_exists = self.check_file_exist(file_path, file_name)
        
        if not file_exists:
            print(f'File {file_name} does not exist.\n')
            return
        
        message = 'PUBLISH_FILE_INFO\n' + file_path + '\n' + file_name + '\n' + str(self.upload_port)
        self.server.send(message.encode())
        print(f'Published file {file_name} from {file_path}\n')
    
    def create_folder_if_not_exists(self, file_path):
        if(file_path == '.'):
            return
        
        Path(file_path).mkdir(parents=True, exist_ok=True)
        
    def check_file_exist (self, file_path, file_name):
        if file_path == '.':
            path = file_name
        else:
            path = file_path + '/' + file_name
        return Path(path).exists()
    
    def fetch_file_info(self, payload):
        file_name = payload
        
        message = 'FETCH_FILE_INFO\n' + file_name
        self.server.send(message.encode())

    def display_peer_options(self, payload):
        file_name, options = payload
        
        self.peer_options = {}
        
        if(len(options) == 0):
            print(f'No peer has file {file_name}.\n> ', end = '', flush=True)
            self.is_selecting_peer = False
            return
        
        print(f'Select peer to download file {file_name} from: (example: 0)\n')
        
        for i in range(len(options)):
            self.peer_options[i] = options[i] + ' ' + file_name
            
            hostname, uploader_host, uploader_port, file_path = options[i].split()
            print(f'{i}) Hostname: {hostname}, IP: {uploader_host}, Port: {uploader_port}, File Path: {file_path}')
        
        print('\nSelect option > ', end = '', flush=True)
        self.is_selecting_peer = True

    def download_from_peer(self, payload):
        hostname, host, port, file_path, file_name = payload
        
        port = int(port)
        
        print(f'\rDownloading file {file_name} from {hostname}...\n', flush=True)
        
        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            start_time = time.time()
            peer_socket.connect((host, port))
            
            message = 'DOWNLOAD_FILE\n' + file_path + '\n' + file_name
            peer_socket.send(message.encode())
            
            # Receive and parse header
            header_data = b''
            while b'\n\n' not in header_data:
                chunk = peer_socket.recv(1024)
                if not chunk:
                    break
                header_data += chunk
            
            # Split header and potential file data
            header_end = header_data.find(b'\n\n')
            if header_end != -1:
                header = header_data[:header_end].decode("utf-8")
                first_file_chunk = header_data[header_end + 2:]
            else:
                header = header_data.decode("utf-8")
                first_file_chunk = b''
            
            if header:
                print(header)
            
            # Save to current directory
            save_path = file_name
            
            bytes_received = 0
            with open(save_path, 'wb') as f:
                if first_file_chunk:
                    f.write(first_file_chunk)
                    bytes_received += len(first_file_chunk)
                
                while True:
                    data = peer_socket.recv(1024)
                    if not data:
                        break
                    bytes_received += len(data)
                    f.write(data)
                
                f.flush()
            end_time = time.time()
            
            download_time = end_time - start_time
            print(f'\rDownloaded file {file_name} ({bytes_received} bytes) from {hostname} in {download_time:.2f}s to ./{save_path}', flush=True)
            
            peer_socket.close()
        except Exception as e:
            print(f'Error downloading file: {e}')
            
    def init_upload(self):
        try:
            self.upload_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.upload_socket.bind(('', 0))

            self.upload_port = self.upload_socket.getsockname()[1]
            self.upload_socket.listen(5)
            
        except Exception as e:
            print(e)
                
        while True:
            try:
                conn, addr = self.upload_socket.accept()
                print(f'\rUpload request from {addr[0]}:{addr[1]}\n', flush=True)
                
                upload_thread = threading.Thread(target=self.upload_file, args=(conn, addr))
                upload_thread.start()
            except Exception as e:
                print(e)
                break
            except BaseException:
                print('Client is shutting down...')
                self.shutdown()
                break
        self.upload_socket.close()
            
    def upload_file(self, conn: socket.socket , addr):
        try:
            data = conn.recv(1024).decode("utf-8")

            if not data:
                return
            
            lines = data.splitlines()
            if len(lines) < 3:
                return
            
            method = lines[0].strip()
            file_path = lines[1].strip()
            file_name = lines[2].strip()
            
            if method != 'DOWNLOAD_FILE':
                return
            
            file_exists = self.check_file_exist(file_path, file_name)
            
            if not file_exists:
                conn.send(f'File {file_name} does not exist at {file_path}'.encode())
                return
            
            if file_path == '.':
                # Lấy thư mục chứa script client
                script_dir = os.path.dirname(os.path.abspath(__file__))
                path = os.path.join(script_dir, file_name)
            else:
                path = file_path + '/' + file_name
            
            # Kiểm tra file có tồn tại không
            if not os.path.exists(path):
                conn.send(f'File {file_name} not found at {path}'.encode())
                return
            
            header = 'OS: %s\n' % (platform.platform())
            header += 'Content-Length: %s\n' % (os.path.getsize(path))
            header += 'Content-Type: %s\n\n' % (
                    mimetypes.MimeTypes().guess_type(path)[0])
            
            print('File metadata: \n' + header)
            
            conn.send(header.encode())
            
            try:
                print('Uploading...')

                send_length = 0
                with open(path, 'rb') as file:
                    to_send = file.read(1024)
                    
                    while to_send:
                        send_length += len(to_send)
                        conn.sendall(to_send)
                        to_send = file.read(1024)

                print(f'Uploading successfully ({send_length} bytes)')
                
                inputStr = 'Select option > ' if self.is_selecting_peer else '> '
                print(inputStr, end='', flush=True)
            except Exception:
                raise MyException('Uploading Failed')

                    
        except Exception as e:
            print(e)
        except BaseException:
            print('Client is shutting down...')
            self.shutdown()
        finally:
            conn.close()
    def list_peers(self, payload = None):
        message = 'FETCH_AVAILABLE_PEERS\n'
        self.server.send(message.encode())
        
    def list_files(self, payload = None):
        message = 'FETCH_ALL_FILE_INFO\n'
        self.server.send(message.encode())

    def shutdown(self, payload = None):
        print('\nShutting Down...')
        try:
                message = 'DISCONNECT\n'
                self.server.send(message.encode())
                
                # Đóng socket
                self.server.close()
                
                # Đóng upload socket
                if hasattr(self, 'upload_socket'):
                    self.upload_socket.close()
                    
        except Exception as e:
                print(f'Error during shutdown: {e}')
        finally:
                try:
                    sys.exit(0)
                except SystemExit:
                    os._exit(0)
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--hostname', dest='hostname', type=str, help='Client hostname')
    parser.add_argument('--server_host', dest='server_host', type=str, default='10.128.17.239', help='Server host address')
    
    args = parser.parse_args()
    
    client = Client(hostname=args.hostname, server_host=args.server_host)
    
    client.start()