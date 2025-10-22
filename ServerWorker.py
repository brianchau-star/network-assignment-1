from random import randint
import sys, traceback, threading, socket

from VideoStream import VideoStream
from RtpPacket import RtpPacket


class ServerWorker:
    SETUP = "SETUP"
    PLAY = "PLAY"
    PAUSE = "PAUSE"
    TEARDOWN = "TEARDOWN"

    INIT = 0
    READY = 1
    PLAYING = 2
    state = INIT

    OK_200 = 0
    FILE_NOT_FOUND_404 = 1
    CON_ERR_500 = 2

    clientInfo = {}

    def __init__(self, clientInfo):
        print("[SERVERWORKER] Initializing server worker for new client")
        self.clientInfo = clientInfo
        print("[SERVERWORKER] Client Info: ", self.clientInfo)

    def run(self):
        print("[SERVERWORKER] Starting server worker thread")
        threading.Thread(target=self.recvRtspRequest).start()

    def recvRtspRequest(self):
        """Receive RTSP request from the client."""
        print("[SERVERWORKER] Starting to listen for RTSP requests")
        connSocket = self.clientInfo["rtspSocket"][0]
        while True:
            data = connSocket.recv(1024)
            if data:
                print("Data received:\n" + data.decode("utf-8"))
                self.processRtspRequest(data.decode("utf-8"))

    def processRtspRequest(self, data):
        """Process RTSP request sent from the client."""
        print("[SERVERWORKER] Processing RTSP request")
        # Get the request type
        request = data.split("\n")
        line1 = request[0].split(" ")
        requestType = line1[0]
        print(f"[SERVERWORKER] Request type: {requestType}")

        # Get the media file name
        filename = line1[1]
        print(f"[SERVERWORKER] Requested file: {filename}")

        # Get the RTSP sequence number
        seq = request[1].split(" ")

        # Process SETUP request
        if requestType == self.SETUP:
            if self.state == self.INIT:
                # Update state
                print("processing SETUP\n")
                print(f"[SERVERWORKER] State changed from INIT to READY")

                try:
                    self.clientInfo["videoStream"] = VideoStream(filename)
                    self.state = self.READY
                    print(f"[SERVERWORKER] Video stream created successfully")
                except IOError:
                    print(f"[SERVERWORKER] ERROR: File not found - {filename}")
                    self.replyRtsp(self.FILE_NOT_FOUND_404, seq[1])

                # Generate a randomized RTSP session ID
                self.clientInfo["session"] = randint(100000, 999999)
                print(
                    f"[SERVERWORKER] Generated session ID: {self.clientInfo['session']}"
                )

                # Send RTSP reply
                self.replyRtsp(self.OK_200, seq[1])

                # Get the RTP/UDP port from the last line
                self.clientInfo["rtpPort"] = request[2].split(" ")[3]
                print(f"[SERVERWORKER] Client RTP port: {self.clientInfo['rtpPort']}")

        # Process PLAY request
        elif requestType == self.PLAY:
            if self.state == self.READY:
                print("processing PLAY\n")
                print(f"[SERVERWORKER] State changed from READY to PLAYING")
                self.state = self.PLAYING

                # Create a new socket for RTP/UDP
                self.clientInfo["rtpSocket"] = socket.socket(
                    socket.AF_INET, socket.SOCK_DGRAM
                )
                print("[SERVERWORKER] Created RTP socket")

                self.replyRtsp(self.OK_200, seq[1])

                # Create a new thread and start sending RTP packets
                self.clientInfo["event"] = threading.Event()
                self.clientInfo["worker"] = threading.Thread(target=self.sendRtp)
                self.clientInfo["worker"].start()
                print("[SERVERWORKER] Started RTP sending thread")

        # Process PAUSE request
        elif requestType == self.PAUSE:
            if self.state == self.PLAYING:
                print("processing PAUSE\n")
                print(f"[SERVERWORKER] State changed from PLAYING to READY")
                self.state = self.READY

                self.clientInfo["event"].set()
                print("[SERVERWORKER] Stopped RTP sending")

                self.replyRtsp(self.OK_200, seq[1])

        # Process TEARDOWN request
        elif requestType == self.TEARDOWN:
            print("processing TEARDOWN\n")
            print("[SERVERWORKER] Processing teardown request")

            self.clientInfo["event"].set()

            self.replyRtsp(self.OK_200, seq[1])

            # Close the RTP socket
            self.clientInfo["rtpSocket"].close()
            print("[SERVERWORKER] Closed RTP socket")

    def sendRtp(self):
        """Send RTP packets over UDP."""
        print("[SERVERWORKER] Starting RTP packet transmission")
        while True:
            self.clientInfo["event"].wait(0.05)

            # Stop sending if request is PAUSE or TEARDOWN
            if self.clientInfo["event"].isSet():
                print("[SERVERWORKER] Stopping RTP transmission")
                break

            data = self.clientInfo["videoStream"].nextFrame()
            if data:
                frameNumber = self.clientInfo["videoStream"].frameNbr()
                try:
                    address = self.clientInfo["rtspSocket"][1][0]
                    port = int(self.clientInfo["rtpPort"])
                    self.clientInfo["rtpSocket"].sendto(
                        self.makeRtp(data, frameNumber), (address, port)
                    )
                    print(f"[SERVERWORKER] Sent RTP packet for frame #{frameNumber}")
                except:
                    print("Connection Error")
                    print("[SERVERWORKER] ERROR: Failed to send RTP packet")
                    # print('-'*60)
                    # traceback.print_exc(file=sys.stdout)
                    # print('-'*60)

    def makeRtp(self, payload, frameNbr):
        """RTP-packetize the video data."""
        print(f"[SERVERWORKER] Creating RTP packet for frame #{frameNbr}")
        version = 2
        padding = 0
        extension = 0
        cc = 0
        marker = 0
        pt = 26  # MJPEG type
        seqnum = frameNbr
        ssrc = 0

        rtpPacket = RtpPacket()

        rtpPacket.encode(
            version, padding, extension, cc, seqnum, marker, pt, ssrc, payload
        )

        return rtpPacket.getPacket()

    def replyRtsp(self, code, seq):
        """Send RTSP reply to the client."""
        if code == self.OK_200:
            print(f"[SERVERWORKER] Sending 200 OK reply (seq: {seq})")
            # print("200 OK")
            reply = (
                "RTSP/1.0 200 OK\nCSeq: "
                + seq
                + "\nSession: "
                + str(self.clientInfo["session"])
            )
            connSocket = self.clientInfo["rtspSocket"][0]
            connSocket.send(reply.encode())

        # Error messages
        elif code == self.FILE_NOT_FOUND_404:
            print("404 NOT FOUND")
            print("[SERVERWORKER] Sending 404 NOT FOUND reply")
        elif code == self.CON_ERR_500:
            print("500 CONNECTION ERROR")
            print("[SERVERWORKER] Sending 500 CONNECTION ERROR reply")
