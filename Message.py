import binascii

from Exceptions import *
from MessageData import *
from MglPacketStream import *

class Message(object):
    timestamp: int

    totalBytes: int
    type: int
    rate: int
    count: int
    version: int
    data: bytearray
    checksum: int

    rawHeader: bytearray
    messageData: MessageData

    def __init__(self, timestamp: int, length: int, packetStream: MglPacketStream):
        self.timestamp = timestamp

        self.totalBytes = 0
        buffer = packetStream.read(length + 16)
        self.rawHeader = buffer[:4]
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
        buffer = self.rawHeader
        buffer.extend(self.messageData.rawData)
        crc = binascii.crc32(buffer)  # % (1 << 32) # convert to unsigned CRC32
        if crc != self.checksum:
            raise CrcMismatch(self.totalBytes)

    def __str__(self):
        print('{ts}.{count}: '.format(ts=self.timestamp, count=self.count), end='')
        if self.messageData.MESSAGETYPE is None:
            # return 'Message type {type}  {msgData!s}'.format(type=self.type, msgData=self.messageData)
            return 'Message type {type}'.format(type=self.type)
        else:
            return str(self.messageData)
