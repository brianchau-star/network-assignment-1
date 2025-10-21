class VideoStream:
    def __init__(self, filename):
        print(f"[VIDEOSTREAM] Initializing video stream with file: {filename}")
        self.filename = filename
        try:
            self.file = open(filename, "rb")
            print(f"[VIDEOSTREAM] Successfully opened file: {filename}")
        except:
            print(f"[VIDEOSTREAM] ERROR: Failed to open file: {filename}")
            raise IOError
        self.frameNum = 0

    def nextFrame(self):
        """Get next frame."""
        print(f"[VIDEOSTREAM] Reading next frame (frame #{self.frameNum + 1})")
        data = self.file.read(5)  # Get the framelength from the first 5 bits
        if data:
            framelength = int(data)
            print(f"[VIDEOSTREAM] Frame length: {framelength} bytes")

            # Read the current frame
            data = self.file.read(framelength)
            self.frameNum += 1
            print(f"[VIDEOSTREAM] Successfully read frame #{self.frameNum}")
        else:
            print("[VIDEOSTREAM] No more frames available")
        return data

    def frameNbr(self):
        """Get frame number."""
        return self.frameNum
