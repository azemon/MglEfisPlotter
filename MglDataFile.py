import datetime
import struct
from typing import BinaryIO, List

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


class NotPartOfFlightException(Exception):
    pass


class NotAMessage(Exception):
    pass


class MessageData(object):
    pass


class PrimaryFlight(MessageData):
    pAltitude: int
    bAltitude: int
    asi: int
    tas: int
    aoa: int
    vsi: int
    baro: int
    local: int
    oat: int
    humidity: int
    systemFlags: int
    hour: int
    minute: int
    second: int
    date: int
    month: int
    year: int
    ftHour: int
    ftMin: int

    baroHg: float
    oatF: float
    dateTime: datetime

    exception: Exception

    def __init__(self, buffer: bytearray):
        (self.pAltitude, self.bAltitude, # ii
         self.asi, self.tas, # HH
         self.aoa, self.vsi, # hh
         self.baro, self.local, # HH
         self.oat, self.humidity, # hb
         self.systemFlags, # B
         self.hour, self.minute, self.second, self.date, self.month, self.year, # bbbbbb
         self.ftHour, self.ftMin, # bb
         ) = struct.unpack('ii HH hh HH hb B bbbbbb bb', buffer)

        self.baroHg = self.baro / 33.864 / 10
        self.oatF = (self.oat + 40) * 9 / 5 - 40
        try:
            self.dateTime = datetime.datetime(self.year + 2000, self.month, self.date, self.hour, self.minute, self.second)
        except ValueError as e:
            self.exception = e


class Gps(MessageData):
    latitude: int
    longitude: int
    gpsAltitude: int
    agl: int
    northVelocity: int
    eastVelocity: int
    downVelocity: int
    groundSpeed: int
    trueTrack: int
    variation: int
    gps: int
    satsTracked: int
    satsVisible: int
    horizontalAccuracy: int
    verticalAccuracy: int
    gpsCapability: int
    raimStatus: int
    raimHError: int
    raimVError: int

    latitudeDegrees: float
    longitudeDegrees: float
    groundSpeedKnots: float

    def __init__(self, buffer: bytearray):
        (self.latitude, self.longitude, # ii
         self.gpsAltitude, self.agl, # ii
         self.northVelocity, self.eastVelocity, self.downVelocity, # iii
         self.groundSpeed, self.trueTrack, self.variation, # HHh
         self.gps, self.satsTracked, self.satsVisible, # bbb
         self.horizontalAccuracy, self.verticalAccuracy, self.gpsCapability, # bbb
         self.raimStatus, self.raimHError, self.raimVError, # bbb
         ) = struct.unpack_from('ii ii iii HHh bbb bbb bbb x', buffer)

        self.latitudeDegrees = self.latitude / 180 / 1000
        self.longitudeDegrees = self.longitude / 180 / 1000
        self.groundSpeedKnots = self.groundSpeed * 0.1944



class Message(object):
    totalBytes: int
    type: int
    rate: int
    count: int
    version: int
    data: bytearray
    checksun: int

    messageData: MessageData

    def __init__(self, buffer: bytearray):
        (dle, stx, length, lengthXor) = struct.unpack_from('BBBB', buffer)
        calculatedLength = lengthXor ^ 0xff
        if dle != 0x5 or stx != 0x2 or length != calculatedLength:
            raise NotAMessage()
        self.totalBytes = 4

        (self.type, self.rate, self.count, self.version) = struct.unpack_from('BBBB', buffer, self.totalBytes)
        self.totalBytes += 4

        length += 8
        format = '{length}s I'.format(length=length)
        slice = buffer[self.totalBytes : self.totalBytes + length + 4]
        sliceLen = len(slice)
        (self.data, self.checksum) = struct.unpack(format, slice)
        self.totalBytes += length + 4

        self.setMessageData()
        return

    def setMessageData(self):
        if 1 == self.type:
            self.messageData = PrimaryFlight(self.data)
        elif 2 == self.type:
            self.messageData = Gps(self.data)


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
            raise NotPartOfFlightException()
        self.latestTimestamp = timestamp
        self.byteStream.extend(buffer)

    def analyze(self):
        totalBytes = 0
        self.messages = []
        while totalBytes < len(self.byteStream):
            message = Message(self.byteStream[totalBytes:])
            self.messages.append(message)
            totalBytes += message.totalBytes
        return

    def __str__(self):
        return 'Flight from {earliest} to {latest} with {bytes} bytes'.format(earliest=self.earliestTimestamp,
                                                                              latest=self.latestTimestamp,
                                                                              bytes=len(self.byteStream))


class Packet(object):
    timestamp: int
    buffer: bytearray

    def __init__(self, timestamp: int, buffer: bytearray):
        self.timestamp = timestamp
        self.buffer = buffer


class MglPacketStream(object):
    filePointer: BinaryIO
    packets: List[Packet]
    flights: List[Flight]

    RECORDSIZE = 512

    def __init__(self, fp: BinaryIO):
        self.filePointer = fp
        self.packets = []
        self.flights = []
        self.readPackets()
        self.createFlights()

    def createFlights(self):
        flight = None
        for packet in self.packets:
            if flight is None:
                flight = Flight(packet.timestamp, packet.buffer)
            else:
                try:
                    flight.addBytes(packet.timestamp, packet.buffer)
                except NotPartOfFlightException:
                    self.flights.append(flight)
                    flight = Flight(packet.timestamp, packet.buffer)
        self.flights.append(flight)

    def readPackets(self):
        while True:
            buffer = self.filePointer.read(self.RECORDSIZE)
            if 0 == len(buffer):
                return
            (ts, buf) = struct.unpack_from('I 508s', buffer)
            if 0 != ts:
                self.packets.append(Packet(ts, bytearray(buf)))


if '__main__' == __name__:
    minDate = datetime.datetime(2015, 3, 17)
    maxDate = datetime.datetime(2021, 1, 1)

    first = maxDate
    last = minDate

    with open('data/IEFISBB.DAT', 'rb') as filePointer:
        packetStream = MglPacketStream(filePointer)
    print(packetStream)
    print(packetStream.flights)

    for flight in packetStream.flights:
        flight.analyze()
        print(flight)
        print(flight.messages)
