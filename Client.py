from tkinter import *
import tkinter.messagebox
from PIL import Image, ImageTk
import socket, threading, sys, traceback, os

from RtpPacket import RtpPacket

CACHE_FILE_NAME = "cache-"
CACHE_FILE_EXT = ".jpg"


class Client:
    INIT = 0
    READY = 1
    PLAYING = 2
    state = INIT

    SETUP = 0
    PLAY = 1
    PAUSE = 2
    TEARDOWN = 3

    # Initiation..
    def __init__(self, master, serveraddr, serverport, rtpport, filename):
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.handler)
        self.createWidgets()
        self.serverAddr = serveraddr
        self.serverPort = int(serverport)
        self.rtpPort = int(rtpport)
        self.fileName = filename
        self.rtspSeq = 0
        self.sessionId = 0
        self.requestSent = -1
        self.teardownAcked = 0
        self.connectToServer()
        self.frameNbr = 0

    # THIS GUI IS JUST FOR REFERENCE ONLY, STUDENTS HAVE TO CREATE THEIR OWN GUI
    def createWidgets(self):
        """Build GUI."""
        # Create Setup button
        self.setup = Button(self.master, width=20, padx=3, pady=3)
        self.setup["text"] = "Setup"
        self.setup["command"] = self.setupMovie
        self.setup.grid(row=1, column=0, padx=2, pady=2)

        # Create Play button
        self.start = Button(self.master, width=20, padx=3, pady=3)
        self.start["text"] = "Play"
        self.start["command"] = self.playMovie
        self.start.grid(row=1, column=1, padx=2, pady=2)

        # Create Pause button
        self.pause = Button(self.master, width=20, padx=3, pady=3)
        self.pause["text"] = "Pause"
        self.pause["command"] = self.pauseMovie
        self.pause.grid(row=1, column=2, padx=2, pady=2)

        # Create Teardown button
        self.teardown = Button(self.master, width=20, padx=3, pady=3)
        self.teardown["text"] = "Teardown"
        self.teardown["command"] = self.exitClient
        self.teardown.grid(row=1, column=3, padx=2, pady=2)

        # Create a label to display the movie
        self.label = Label(self.master, height=19)
        self.label.grid(
            row=0, column=0, columnspan=4, sticky=W + E + N + S, padx=5, pady=5
        )

    def setupMovie(self):
        """Set up the movie for streaming"""
        if(self.state == self.PLAYING  | self.state == self.PAUSE):
            print(f"[CLIENT] Please TearDown current video before playing newVideo")
        self.sendRtspRequest('SETUP')

    def exitClient(self):
        """Teardown button handler."""
        print("[CLIENT] Teardown button clicked")

    # TODO

    def pauseMovie(self):
        """Pause button handler."""
        print("[CLIENT] Pause button clicked")

    # TODO

    def playMovie(self):
        """Play button handler."""
        print("[CLIENT] Play button clicked")

    # TODO

    def listenRtp(self):
        """Listen for RTP packets."""
        print("[CLIENT] Starting to listen for RTP packets")
        # TODO

    def writeFrame(self, data):
        """Write the received frame to a temp image file. Return the image file."""
        print(f"[CLIENT] Writing frame data to cache file")

    # TODO

    def updateMovie(self, imageFile):
        """Update the image file as video frame in the GUI."""
        print(f"[CLIENT] Updating movie display with image: {imageFile}")

    # TODO

    def connectToServer(self):
        """Connect to the Server. Start a new RTSP/TCP session."""
        print(f"[CLIENT] Connecting to server {self.serverAddr}:{self.serverPort}")

        try:
            # Create a TCP socket for RTSP communication
            self.rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("[CLIENT] Created RTSP socket")

            # Connect to the server
            self.rtspSocket.connect((self.serverAddr, self.serverPort))
            print(
                f"[CLIENT] Successfully connected to server {self.serverAddr}:{self.serverPort}"
            )

        except socket.error as e:
            print(
                f"[CLIENT] ERROR: Failed to connect to server {self.serverAddr}:{self.serverPort}"
            )
            print(f"[CLIENT] Socket error: {e}")
            tkinter.messagebox.showwarning(
                "Connection Failed", f"Connection to '{self.serverAddr}' failed."
            )

    def formatRequest(self, statusCode):
        self.rtspSeq += 1
        return f"{statusCode} {self.fileName} RTSP/1.0\nCSeq: {self.rtspSeq}\nTransport: RTP/UDP; client_port= {self.rtpPort}"

    # TODO

    def sendRtspRequest(self, requestCode):
        """Send RTSP request to the server."""
        print(f"[CLIENT] Sending RTSP request with code: {requestCode}")
        request = self.formatRequest(requestCode)
        self.rtspSocket.send(request.encode())
        self.recvRtspReply()

    def recvRtspReply(self):
        """Receive RTSP reply from the server."""
        print("[CLIENT] Waiting for RTSP reply from server")
        response = self.rtspSocket.recv(1024).decode()
        self.parseRtspReply(response)
        # TODO

    def parseRtspReply(self, data):
        """Parse the RTSP reply from the server."""
        print("[CLIENT] Parsing RTSP reply from server")

        try:
            lines = data.split('\n')
            
            status_line = lines[0].split(' ')
            status_code = status_line[1]
            status_message = ' '.join(status_line[2:])
            
            cseq = None
            session = None
            
            for line in lines[1:]:
                if line.strip() == "":
                    break
                    
                if line.startswith("CSeq: "):
                    cseq = line.split(" ")[1].strip()
                    
                elif line.startswith("Session: "):
                    session = line.split(" ")[1].strip()
            
            if status_code == "200":
                if session and session != "":
                    self.sessionId = session
                    print(f"[CLIENT] Session ID updated: {self.sessionId}")
                
                print(f"[CLIENT] Request successful with CSEQ: {self.rtspSeq} and Session ID: {self.sessionId}") 
            elif status_code == "404":
                print("[CLIENT] ERROR: File not found")
                tkinter.messagebox.showerror("Error", "File not found on server")
                
            elif status_code == "500":
                print("[CLIENT] ERROR: Server internal error")
                tkinter.messagebox.showerror("Error", "Server internal error")
                
            else:
                print(f"[CLIENT] ERROR: Unknown status code {status_code}")
                tkinter.messagebox.showerror("Error", f"Server returned error: {status_code} {status_message}")
                
        except Exception as e:
            print(f"[CLIENT] ERROR: Failed to parse RTSP reply: {e}")
            print(f"[CLIENT] Raw data: {repr(data)}")
            tkinter.messagebox.showerror("Error", "Failed to parse server response")
        # TODO

    def openRtpPort(self):
        """Open RTP socket binded to a specified port."""
        print(f"[CLIENT] Opening RTP port: {self.rtpPort}")
        # -------------
        # TO COMPLETE
        # -------------
        # Create a new datagram socket to receive RTP packets from the server
        # self.rtpSocket = ...

        # Set the timeout value of the socket to 0.5sec
        # ...

    def handler(self):
        """Handler on explicitly closing the GUI window."""
        print("[CLIENT] GUI window closing handler called")
        # TODO
