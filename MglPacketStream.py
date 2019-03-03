import struct
from typing import BinaryIO, List

from Exceptions import *

class Packet(object):
    timestamp: int
    buffer: bytearray

    position: int
    eof: bool

    def __init__(self, timestamp: int, buffer: bytearray):
        self.timestamp = timestamp
        self.buffer = buffer
        self.position = 0
        self.eof = False

    def read(self, qty: int) -> bytearray:
        if self.eof:
            raise EndOfPacket()
        remaining = len(self.buffer) - self.position
        if qty < remaining:
            slice = self.buffer[self.position : self.position + qty]
            self.position += qty
            return slice
        else:
            self.eof = True
            return self.buffer[self.position : ]



class MglPacketStream(object):
    filePointer: BinaryIO
    packets: List[Packet]
    currentPacket: int
    eof: bool
    unreadBuffer: bytearray
    timestamp: int

    RECORDSIZE = 512

    def __init__(self, fp: BinaryIO, minTimestamp: int = 0):
        self.packets = []
        self.currentPacket = 0
        self.eof = False
        self.unreadBuffer = bytearray(0)

        self.filePointer = fp
        self.loadPackets(minTimestamp)

    def loadPackets(self, minTimestamp: int):
        while True:
            buffer = self.filePointer.read(self.RECORDSIZE)
            if 0 == len(buffer):
                return
            (timestamp, buf) = struct.unpack_from('I 508s', buffer)
            if 0 != timestamp and timestamp >= minTimestamp:
                self.packets.append(Packet(timestamp, bytearray(buf)))

    def read(self, qty: int) -> bytearray:
        if self.eof:
            raise EndOfFile()

        if 0 < len(self.unreadBuffer):
            unreadBytes = min(len(self.unreadBuffer), qty)
            buffer = self.unreadBuffer[:unreadBytes]
            self.unreadBuffer = self.unreadBuffer[unreadBytes:]
            if len(buffer) == qty:
                return buffer
        else:
            buffer = bytearray(0)

        stillNeeded = qty - len(buffer)
        if self.packets[self.currentPacket].eof:
            self.nextPacket()
        buffer.extend(self.packets[self.currentPacket].read(stillNeeded))
        self.timestamp = self.packets[self.currentPacket].timestamp
        if len(buffer) == qty:
            return buffer
        else:
            self.nextPacket()
            stillNeeded = qty - len(buffer)
            buffer2 = self.read(stillNeeded)
            buffer.extend(buffer2)
            return buffer

    def nextPacket(self):
        self.currentPacket += 1
        if self.currentPacket >= len(self.packets):
            self.eof = True
            raise EndOfFile()

    def unread(self, buffer: int):
        b = bytearray([buffer])
        self.unreadBuffer.extend(b)
