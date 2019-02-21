import struct
from typing import BinaryIO

"""
Functions to convert between Python values and C structs.
Python bytes objects are used to hold the data representing the C struct
and also as format strings (explained below) to describe the layout of data
in the C struct.

The optional first format char indicates byte order, size and alignment:
  @: native order, size & alignment (default)
  =: native order, std. size & alignment
  <: little-endian, std. size & alignment
  >: big-endian, std. size & alignment
  !: same as >

The remaining chars indicate types of args and must match exactly;
these can be preceded by a decimal repeat count:
  x: pad byte (no data); c:char; b:signed byte; B:unsigned byte;
  ?: _Bool (requires C99; if not available, char is used instead)
  h:short; H:unsigned short; i:int; I:unsigned int;
  l:long; L:unsigned long; f:float; d:double; e:half-float.
Special cases (preceding decimal count indicates length):
  s:string (array of char); p: pascal string (with count byte).
Special cases (only available in native format):
  n:ssize_t; N:size_t;
  P:an integer type that is wide enough to hold a pointer.
Special case (not in native mode unless 'long long' in platform C):
  q:long long; Q:unsigned long long
Whitespace between formats is ignored.

The variable struct.error is an exception raised on errors.
"""

class DataError(Exception):
    pass


class MglRecord(object):
    filePointer: BinaryIO

    timeStamp = None
    dataStream = None

    rawHeader = None
    rawMessageWithChecksum = None

    checksum = None
    dle = None
    messageLength = None
    messageType = None
    stx = None

    HEADERSIZE = 8
    PRIVATEHEADERSIZE = 8

    def __init__(self, filePointer):
        self.filePointer = filePointer

    def readRecord(self):
        self.readTimestamp()
        self.readDataStream()

    def readDataStream(self):
        self.dataStream = self.filePointer.read(508)

    def readTimestamp(self):
        t = self.filePointer.read(4)
        self.timeStamp = struct.unpack('I', t)

    def readChecksum(self):
        rawChecksum = self.filePointer.read(4)
        self.checksum = struct.unpack('I', rawChecksum)

    def readHeader(self):
        self.rawHeader = self.filePointer.read(8)
        (self.dle, self.stx, self.messageLength, self.messageType) = struct.unpack('BBBxBxxx', self.rawHeader)
        if 106 != self.dle or 48 != self.stx:
            raise DataError()

    def readMessageData(self):
        self.rawMessageWithChecksum = self.filePointer.read(self.messageLength + self.PRIVATEHEADERSIZE)


if '__main__' == __name__:
    with open('data/IEFISBB.DAT', 'rb') as filePointer:
        recordNumber = 0
        while True:
            m = MglRecord(filePointer)
            m.readRecord()
            print(recordNumber, m.timeStamp)
            recordNumber += 1
