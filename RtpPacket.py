import sys
from time import time

HEADER_SIZE = 12


class RtpPacket:
    header = bytearray(HEADER_SIZE)

    def __init__(self):
        print("[RTPPACKET] Initializing RTP packet")
        pass

    def encode(
        self, version, padding, extension, cc, seqnum, marker, pt, ssrc, payload
    ):
        """Encode the RTP packet with header fields and payload."""
        print(f"[RTPPACKET] Encoding RTP packet - seq: {seqnum}, pt: {pt}")
        timestamp = int(time())
        header = bytearray(HEADER_SIZE)
        # --------------
        # TO COMPLETE
        # --------------
        # Fill the header bytearray with RTP header fields

        # header[0] = ...
        # ...

        # Get the payload from the argument
        # self.payload = ...

    def decode(self, byteStream):
        """Decode the RTP packet."""
        print(f"[RTPPACKET] Decoding RTP packet of {len(byteStream)} bytes")
        self.header = bytearray(byteStream[:HEADER_SIZE])
        self.payload = byteStream[HEADER_SIZE:]
        print(f"[RTPPACKET] Decoded - seq: {self.seqNum()}, payload size: {len(self.payload)}")

    def version(self):
        """Return RTP version."""
        return int(self.header[0] >> 6)

    def seqNum(self):
        """Return sequence (frame) number."""
        seqNum = self.header[2] << 8 | self.header[3]
        return int(seqNum)

    def timestamp(self):
        """Return timestamp."""
        timestamp = (
            self.header[4] << 24
            | self.header[5] << 16
            | self.header[6] << 8
            | self.header[7]
        )
        return int(timestamp)

    def payloadType(self):
        """Return payload type."""
        pt = self.header[1] & 127
        return int(pt)

    def getPayload(self):
        """Return payload."""
        return self.payload

    def getPacket(self):
        """Return RTP packet."""
        packet = self.header + self.payload
        print(f"[RTPPACKET] Returning complete packet of {len(packet)} bytes")
        return packet
