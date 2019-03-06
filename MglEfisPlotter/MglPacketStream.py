import struct
from typing import BinaryIO, List, Set

from .Exceptions import *


class Record(object):
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
            raise EndOfRecord()
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
    records: List[Record]
    currentRecord: int
    eof: bool
    unreadBuffer: bytearray
    timestamp: int

    RECORDSIZE = 512

    def __init__(self, fp: BinaryIO, minTimestamp: int = 0, maxTimestamp: int = 9000000000):
        self.records = []
        self.currentRecord = 0
        self.eof = False
        self.unreadBuffer = bytearray(0)

        self.filePointer = fp
        self.loadRecords(minTimestamp, maxTimestamp)

        # print('Record timestamps:')
        # lastTs = 0
        # for record in self.records:
        #     print('  {ts:,}'.format(ts=record.timestamp))
        #     lastTs = record.timestamp
        # print('*' * 100)

    def loadRecords(self, minTimestamp: int, maxTimestamp: int):
        while True:
            buffer = self.filePointer.read(self.RECORDSIZE)
            if 0 == len(buffer):
                return
            (timestamp, buf) = struct.unpack_from('I 508s', buffer)
            if 0 != timestamp and timestamp >= minTimestamp and timestamp <= maxTimestamp:
                self.records.append(Record(timestamp, bytearray(buf)))

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
        if self.records[self.currentRecord].eof:
            self.nextRecord()
        buffer.extend(self.records[self.currentRecord].read(stillNeeded))
        self.timestamp = self.records[self.currentRecord].timestamp
        if len(buffer) == qty:
            return buffer
        else:
            self.nextRecord()
            stillNeeded = qty - len(buffer)
            buffer2 = self.read(stillNeeded)
            buffer.extend(buffer2)
            return buffer

    def nextRecord(self):
        self.currentRecord += 1
        if self.currentRecord >= len(self.records):
            self.eof = True
            raise EndOfFile()

    def unread(self, buffer: int):
        b = bytearray([buffer])
        self.unreadBuffer.extend(b)
