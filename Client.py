from tkinter import *
import tkinter.messagebox
from tkinter import scrolledtext
from PIL import Image, ImageTk
import socket, threading, sys, traceback, os
import logging
from datetime import datetime

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
        self.frameNbr = 0
        
        # Setup logging
        self.setupLogging()
        self.log("INFO", f"Client initialized - Server: {serveraddr}:{serverport}, RTP Port: {rtpport}, File: {filename}")
        
        self.connectToServer()

    def setupLogging(self):
        """Setup logging configuration."""
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def log(self, level, message):
        """Add log message to the log display and console."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {level}: {message}"
        
        # Add to GUI log display
        self.log_text.insert(END, log_message + "\n")
        self.log_text.see(END)
        
        # Also log to console
        if level == "ERROR":
            self.logger.error(message)
        elif level == "WARNING":
            self.logger.warning(message)
        else:
            self.logger.info(message)

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
        """Setup button handler."""
        self.log("INFO", "Setup button clicked")
        # TODO

    def exitClient(self):
        """Teardown button handler."""
        self.log("INFO", "Teardown initiated")
        # Signal teardown and attempt to notify server
        self.teardownAcked = 1
        try:
            # If a session exists, send TEARDOWN via RTSP
            if self.state in (self.READY, self.PLAYING):
                self.log("INFO", "Sending TEARDOWN request to server")
                self.sendRtspRequest(self.TEARDOWN)
        except Exception as e:
            self.log("ERROR", f"Failed to send TEARDOWN request: {str(e)}")

        # Best-effort close of RTP/RTSP sockets
        try:
            if hasattr(self, "rtpSocket") and self.rtpSocket:
                self.rtpSocket.close()
                self.log("INFO", "RTP socket closed")
        except Exception as e:
            self.log("ERROR", f"Error closing RTP socket: {str(e)}")
            
        try:
            if hasattr(self, "rtspSocket") and self.rtspSocket:
                self.rtspSocket.close()
                self.log("INFO", "RTSP socket closed")
        except Exception as e:
            self.log("ERROR", f"Error closing RTSP socket: {str(e)}")

        # Remove cached frame image if present
        try:
            cache_name = f"{CACHE_FILE_NAME}{self.sessionId}{CACHE_FILE_EXT}"
            if os.path.exists(cache_name):
                os.remove(cache_name)
                self.log("INFO", f"Cached file {cache_name} removed")
        except Exception as e:
            self.log("ERROR", f"Error removing cache file: {str(e)}")

        # Close the UI
        try:
            self.log("INFO", "Client shutdown complete")
            self.master.destroy()
        except Exception as e:
            self.log("ERROR", f"Error closing GUI: {str(e)}")

    def pauseMovie(self):
        """Pause button handler."""
        self.log("INFO", "Pause button clicked")
        # TODO

    def playMovie(self):
        """Play button handler."""
        self.log("INFO", "Play button clicked")
        # TODO

    def listenRtp(self):
        """Listen for RTP packets."""
        self.log("INFO", "Started listening for RTP packets")
        # TODO

    def writeFrame(self, data):
        """Write the received frame to a temp image file. Return the image file."""
        self.log("INFO", f"Writing frame {self.frameNbr} to cache")
        # TODO

    def updateMovie(self, imageFile):
        """Update the image file as video frame in the GUI."""
        self.log("INFO", f"Updating movie frame: {imageFile}")
        # TODO

    def connectToServer(self):
        """Connect to the Server. Start a new RTSP/TCP session."""
        self.log("INFO", f"Attempting to connect to server {self.serverAddr}:{self.serverPort}")
        # TODO

    def sendRtspRequest(self, requestCode):
        """Send RTSP request to the server."""
        request_types = {self.SETUP: "SETUP", self.PLAY: "PLAY", 
                        self.PAUSE: "PAUSE", self.TEARDOWN: "TEARDOWN"}
        self.log("INFO", f"Sending {request_types.get(requestCode, 'UNKNOWN')} request")
        # -------------
        # TO COMPLETE
        # -------------

    def recvRtspReply(self):
        """Receive RTSP reply from the server."""
        self.log("INFO", "Waiting for RTSP reply from server")
        # TODO

    def parseRtspReply(self, data):
        """Parse the RTSP reply from the server."""
        self.log("INFO", "Parsing RTSP reply")
        # TODO

    def openRtpPort(self):
        """Open RTP socket binded to a specified port."""
        self.log("INFO", f"Opening RTP socket on port {self.rtpPort}")
        # -------------
        # TO COMPLETE
        # -------------
        # Create a new datagram socket to receive RTP packets from the server
        # self.rtpSocket = ...

        # Set the timeout value of the socket to 0.5sec
        # ...

    def handler(self):
        """Handler on explicitly closing the GUI window."""
        self.log("INFO", "GUI window close event triggered")
        self.exitClient()
