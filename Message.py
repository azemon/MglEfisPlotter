import binascii

from Exceptions import *
from MessageData import *

class Message(object):
    totalBytes: int
    type: int
    rate: int
    count: int
    version: int
    data: bytearray
    checksum: int
    rawHeader: bytearray

    messageData: MessageData

    def __init__(self, buffer: bytearray):
        self.rawHeader = buffer[:8]

        (dle, stx, length, lengthXor) = struct.unpack_from('BBBB', buffer)
        calculatedLength = lengthXor ^ 0xff
        if dle != 0x5 or stx != 0x2 or length != calculatedLength:
            raise NotAMessage()
        self.totalBytes = 4

        (self.type, self.rate, self.count, self.version) = \
            struct.unpack_from('BBBB', buffer, self.totalBytes)
        self.totalBytes += 4

        length += 8
        format = '{length}s I'.format(length=length)
        slice = buffer[self.totalBytes: self.totalBytes + length + 4]
        (self.data, self.checksum) = struct.unpack(format, slice)
        self.totalBytes += length + 4

        self.setMessageData()

        self.verifyChecksum()

    def setMessageData(self):
        if PrimaryFlight.MESSAGETYPE == self.type:
            self.messageData = PrimaryFlight(self.data)
        elif Gps.MESSAGETYPE == self.type:
            self.messageData = Gps(self.data)
        elif Attitude.MESSAGETYPE == self.type:
            self.messageData = Attitude(self.data)
        elif EngineData.MESSAGETYPE == self.type:
            self.messageData = EngineData(self.data)
        else:
            self.messageData = MessageData(self.data)

    def verifyChecksum(self):
        buffer = self.rawHeader[4:]
        buffer.extend(self.messageData.rawData)
        crc = binascii.crc32(buffer)  # % (1 << 32) # convert to unsigned CRC32
        if crc != self.checksum:
            raise CrcMismatch(self.totalBytes)

    def __str__(self):
        if self.messageData.MESSAGETYPE is None:
            return 'Message type {type}  {msgData!s}'.format(type=self.type, msgData=self.messageData)
        else:
            return str(self.messageData)
