import struct
from typing import BinaryIO, List, Set

from .Exceptions import *


class Record(object):
    """
    one 512 byte record from IEFISBB.DAT
    """

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
        """
        read qty bytes from the record
        :param qty:
        :return: bytearray
        """
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
    """
    stream of packets (a/k/a records) sent from the MGL iEFIS and stored in IEFISBB.DAT
    """
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
        self.sortRecords()

        # print('Record timestamps:')
        # lastTs = 0
        # for record in self.records:
        #     print('  {ts:,}'.format(ts=record.timestamp))
        #     lastTs = record.timestamp
        # print('*' * 100)

    def loadRecords(self, minTimestamp: int, maxTimestamp: int) -> None:
        while True:
            buffer = self.filePointer.read(self.RECORDSIZE)
            if 0 == len(buffer):
                return
            (timestamp, buf) = struct.unpack_from('I 508s', buffer)
            if 0 != timestamp and timestamp >= minTimestamp and timestamp <= maxTimestamp:
                self.records.append(Record(timestamp, bytearray(buf)))

    def sortRecords(self) -> None:
        """
        Reorder the records so that they are in ascending order, so that nothing else has to deal with a flight
        which wraps back to the beginning of the file
        :return:
        """
        for boundary in range(0, len(self.records) - 2):
            if self.records[boundary].timestamp > self.records[boundary+1].timestamp:
                a = self.records[boundary+1:]
                b = self.records[:boundary+1]
                self.records = a + b

    def read(self, qty: int) -> bytearray:
        """
        read qty bytes from the stream, first checking for unread bytes (had been read and then pushed back ito the
        stream) and then reading from as many records as necessary
        :param qty:
        :return: bytearray
        """
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

    def nextRecord(self) -> None:
        """
        get another record
        :return:
        """
        self.currentRecord += 1
        if self.currentRecord >= len(self.records):
            self.eof = True
            raise EndOfFile()

    def unread(self, buffer: int) -> None:
        """
        take back, and store, a few bytes which had been read but were not needed
        :param buffer:
        :return:
        """
        b = bytearray([buffer])
        self.unreadBuffer.extend(b)
