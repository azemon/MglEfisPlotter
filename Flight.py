import sys
import traceback

from Message import *

class Flight(object):
    earliestTimestamp: int
    latestTimestamp: int

    byteStream: bytearray
    messages: List[Message]

    NEWFLIGHTDELTA = 60

    def __init__(self, timestamp: int, buffer: bytes):
        self.earliestTimestamp = timestamp
        self.latestTimestamp = timestamp
        self.byteStream = bytearray(buffer)

    def addBytes(self, timestamp: int, buffer: bytes):
        if timestamp == 0 or timestamp > (self.latestTimestamp + self.NEWFLIGHTDELTA):
            raise NotPartOfFlightException('timestamp = {timestamp}'.format(timestamp=timestamp))
        self.latestTimestamp = timestamp
        self.byteStream.extend(buffer)

    def analyze(self):
        totalBytes = 0
        self.messages = []
        try:
            while totalBytes < len(self.byteStream):
                try:
                    totalBytes = self.findBeginningOfNextMessage(totalBytes)
                    message = Message(self.byteStream[totalBytes:])
                    self.messages.append(message)
                    messageTotalBytes = message.totalBytes
                except CrcMismatch as e:
                    messageTotalBytes = e.totalBytes
                except struct.error as e:
                    print('unpack error: {exception!s}, bytes remaining: {remaining}'.format(
                        exception=e, remaining=(len(self.byteStream) - totalBytes)
                    ))
                    traceback.print_exc(file=sys.stdout)
                    print()
                    return
                totalBytes += messageTotalBytes
        except NoMoreMessages:
            return

    def findBeginningOfNextMessage(self, totalBytes: int) -> int:
        while totalBytes < len(self.byteStream) - 4:
            (dle, stx, length, lengthXor) = struct.unpack_from('BBBB', self.byteStream[totalBytes: totalBytes + 4])
            calculatedLength = lengthXor ^ 0xff
            if dle == 0x5 and stx == 0x2 and length == calculatedLength:
                return totalBytes
            totalBytes += 1
        raise NoMoreMessages()

    def __str__(self):
        return 'Flight from {earliest} with {count} messages'.format(earliest=self.earliestTimestamp,
                                                                     count=len(self.messages))
