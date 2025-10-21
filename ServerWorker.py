from random import randint
import sys, traceback, threading, socket
import logging

from VideoStream import VideoStream
from RtpPacket import RtpPacket

logger = logging.getLogger('ServerWorker')


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
        self.clientInfo = clientInfo
        client_addr = clientInfo["rtspSocket"][1][0]
        logger.info(f"ServerWorker initialized for client: {client_addr}")

    def run(self):
        logger.info("Starting RTSP request handler thread")
        threading.Thread(target=self.recvRtspRequest).start()

    def recvRtspRequest(self):
        """Receive RTSP request from the client."""
        connSocket = self.clientInfo["rtspSocket"][0]
        client_addr = self.clientInfo["rtspSocket"][1][0]
        logger.info(f"Listening for RTSP requests from client: {client_addr}")

        while True:
            try:
                data = connSocket.recv(256)
                if data:
                    logger.info(f"RTSP request received from {client_addr}")
                    logger.debug(f"Request data:\n{data.decode('utf-8')}")
                    print("Data received:\n" + data.decode("utf-8"))
                    self.processRtspRequest(data.decode("utf-8"))
                else:
                    logger.warning(f"Empty data received from {client_addr}")
                    break
            except Exception as e:
                logger.error(f"Error receiving RTSP request: {str(e)}")
                break

    def processRtspRequest(self, data):
        """Process RTSP request sent from the client."""
        # Get the request type
        request = data.split("\n")
        line1 = request[0].split(" ")
        requestType = line1[0]

        # Get the media file name
        filename = line1[1]

        # Get the RTSP sequence number
        seq = request[1].split(" ")

        logger.info(
            f"Processing {requestType} request for file: {filename}, sequence: {seq[1]}"
        )

        # Process SETUP request
        if requestType == self.SETUP:
            if self.state == self.INIT:
                # Update state
                logger.info("Processing SETUP request")
                print("processing SETUP\n")

                try:
                    self.clientInfo["videoStream"] = VideoStream(filename)
                    self.state = self.READY
                    logger.info(
                        f"Video stream created for {filename}, state changed to READY"
                    )
                except IOError:
                    logger.error(f"File not found: {filename}")
                    self.replyRtsp(self.FILE_NOT_FOUND_404, seq[1])
                    return

                # Generate a randomized RTSP session ID
                self.clientInfo["session"] = randint(100000, 999999)
                logger.info(f"Generated session ID: {self.clientInfo['session']}")

                # Send RTSP reply
                self.replyRtsp(self.OK_200, seq[1])

                # Get the RTP/UDP port from the last line
                self.clientInfo["rtpPort"] = request[2].split(" ")[3]
                logger.info(f"Client RTP port: {self.clientInfo['rtpPort']}")

        # Process PLAY request
        elif requestType == self.PLAY:
            if self.state == self.READY:
                logger.info("Processing PLAY request")
                print("processing PLAY\n")
                self.state = self.PLAYING

                # Create a new socket for RTP/UDP
                self.clientInfo["rtpSocket"] = socket.socket(
                    socket.AF_INET, socket.SOCK_DGRAM
                )
                logger.info("RTP socket created for streaming")

                self.replyRtsp(self.OK_200, seq[1])

                # Create a new thread and start sending RTP packets
                self.clientInfo["event"] = threading.Event()
                self.clientInfo["worker"] = threading.Thread(target=self.sendRtp)
                self.clientInfo["worker"].start()
                logger.info("RTP streaming thread started")

        # Process PAUSE request
        elif requestType == self.PAUSE:
            if self.state == self.PLAYING:
                logger.info("Processing PAUSE request")
                print("processing PAUSE\n")
                self.state = self.READY

                self.clientInfo["event"].set()
                logger.info("Streaming paused, state changed to READY")

                self.replyRtsp(self.OK_200, seq[1])

        # Process TEARDOWN request
        elif requestType == self.TEARDOWN:
            logger.info("Processing TEARDOWN request")
            print("processing TEARDOWN\n")

            self.clientInfo["event"].set()

            self.replyRtsp(self.OK_200, seq[1])

            # Close the RTP socket
            self.clientInfo["rtpSocket"].close()
            logger.info("RTP socket closed, session terminated")

    def sendRtp(self):
        """Send RTP packets over UDP."""
        logger.info("Starting RTP packet transmission")
        packet_count = 0

        while True:
            self.clientInfo["event"].wait(0.05)

            # Stop sending if request is PAUSE or TEARDOWN
            if self.clientInfo["event"].isSet():
                logger.info(f"RTP streaming stopped after {packet_count} packets")
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
                    packet_count += 1
                    if packet_count % 30 == 0:  # Log every 30 packets to avoid spam
                        logger.debug(f"Sent {packet_count} RTP packets")
                except Exception as e:
                    logger.error(f"RTP transmission error: {str(e)}")
                    print("Connection Error")
            else:
                logger.info("End of video stream reached")
                break

    def makeRtp(self, payload, frameNbr):
        """RTP-packetize the video data."""
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

        logger.debug(
            f"RTP packet created for frame {frameNbr}, payload size: {len(payload)}"
        )
        return rtpPacket.getPacket()

    def replyRtsp(self, code, seq):
        """Send RTSP reply to the client."""
        if code == self.OK_200:
            logger.info(f"Sending RTSP 200 OK reply, sequence: {seq}")
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
            logger.error(f"Sending RTSP 404 NOT FOUND reply, sequence: {seq}")
            print("404 NOT FOUND")
        elif code == self.CON_ERR_500:
            logger.error(f"Sending RTSP 500 CONNECTION ERROR reply, sequence: {seq}")
            print("500 CONNECTION ERROR")
