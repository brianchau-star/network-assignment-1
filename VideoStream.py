import logging

logger = logging.getLogger('VideoStream')

class VideoStream:
    def __init__(self, filename):
        self.filename = filename
        logger.info(f"Initializing video stream for file: {filename}")
        try:
            self.file = open(filename, "rb")
            logger.info(f"Successfully opened video file: {filename}")
        except Exception as e:
            logger.error(f"Failed to open video file {filename}: {str(e)}")
            raise IOError
        self.frameNum = 0

    def nextFrame(self):
        """Get next frame."""
        data = self.file.read(5)  # Get the framelength from the first 5 bits
        if data:
            framelength = int(data)
            logger.debug(f"Reading frame {self.frameNum + 1}, length: {framelength} bytes")

            # Read the current frame
            data = self.file.read(framelength)
            self.frameNum += 1
            logger.debug(f"Frame {self.frameNum} read successfully ({len(data)} bytes)")
        else:
            logger.info("End of video file reached")
        return data

    def frameNbr(self):
        """Get frame number."""
        return self.frameNum
