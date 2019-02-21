import datetime
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


class EOF(Exception):
    pass


class Timestamp(object):
    mglTimestamp = None
    datetime = None

    def __init__(self, mglTimestamp):
        self.mglTimestamp = mglTimestamp
        self.calculateDatetime()

    def calculateDatetime(self):
        mglEpoch = datetime.datetime(2000, 1, 1, 0, 0, 0)
        sinceEpoch = datetime.timedelta(seconds=self.mglTimestamp)
        self.datetime = mglEpoch + sinceEpoch

    def __str__(self):
        return str(self.datetime)

    def __le__(self, other):
        return self.datetime <= other

    def __lt__(self, other):
        return self.datetime < other

    def __eq__(self, other):
        return self.datetime == other

    def __ne__(self, other):
        return self.datetime != other

    def __gt__(self, other):
        return self.datetime > other

    def __ge__(self, other):
        return self.datetime >= other


class MglRecord(object):
    filePointer: BinaryIO

    timeStamp = None
    dataStream = None

    rawHeader = None
    rawMessageWithChecksum = None

    checksum = None
    dle = None
    messageCount = None
    messageLength = None
    messageType = None
    stx = None

    HEADERSIZE = 8
    PRIVATEHEADERSIZE = 8

    def __init__(self, fp):
        self.filePointer = fp

    def readRecord(self):
        self.readTimestamp()
        self.readDataStream()
        self.parseHeader()

    def readDataStream(self):
        self.dataStream = self.read(508)

    def readTimestamp(self):
        buffer = self.read(4)
        (ts,) = struct.unpack('I', buffer)
        self.timeStamp = Timestamp(ts)

    def readChecksum(self):
        buffer = self.read(4)
        (self.checksum,) = struct.unpack('I', buffer)

    def parseHeader(self):
        (self.dle, self.stx, self.messageLength, self.messageType, self.messageCount) = \
            struct.unpack('BBBxBxBx', self.dataStream[0:8])

    def readMessageData(self):
        self.rawMessageWithChecksum = self.read(self.messageLength + self.PRIVATEHEADERSIZE)

    def read(self, length):
        buffer = self.filePointer.read(length)
        if 0 == len(buffer):
            raise EOF()
        return buffer


if '__main__' == __name__:
    minDate = datetime.datetime(2015, 3, 16)
    maxDate = datetime.datetime(2021, 1, 1)

    first = maxDate
    last = minDate

    try:
        with open('data/IEFISBB.DAT', 'rb') as filePointer:
            recordNumber = 0
            while True:
                m = MglRecord(filePointer)
                m.readRecord()
                if minDate <= m.timeStamp <= maxDate:
                    print('%4d   %s   type=%d' % (recordNumber, m.timeStamp, m.messageType))
                    recordNumber += 1

                    if m.timeStamp < first:
                        first = m.timeStamp

                    if m.timeStamp > last:
                        last = m.timeStamp
    except EOF as e:
        print('--eof--')

    print('first =', first)
    print('last  =', last)
