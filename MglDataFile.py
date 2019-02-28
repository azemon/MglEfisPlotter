import binascii
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
    def __init__(self, m=''):
        super().__init__('Not part of flight' + m)


class NotAMessage(Exception):
    def __init__(self, m=''):
        super().__init__('Not a message' + m)


class CrcMismatch(NotAMessage):
    totalBytes: int

    def __init__(self, totalBytes: int, m=''):
        self.totalBytes = totalBytes
        super().__init__('CRC Mismatch' + m)


class NoMoreMessages(Exception):
    def __init__(self, m=''):
        super().__init__('Not part of flight' + m)


class MessageData(object):
    MESSAGETYPE = None

    rawData: bytearray

    def __init__(self, buffer: bytearray):
        self.rawData = buffer

    def cToF(self, c: float) -> float:
        return (c * 9 / 5) + 32

    def litersToGallons(self, liters: float):
        return liters / 3.785 / 10

    def millibarsToHg(self, m: float) -> float:
        return m / 33.864 / 10

    def millibarsToPsi(self, m: float):
        return m / 68.948 / 10


class PrimaryFlight(MessageData):
    MESSAGETYPE = 1

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
        super().__init__(buffer)
        (self.pAltitude, self.bAltitude, # ii
         self.asi, self.tas, # HH
         self.aoa, self.vsi, # hh
         self.baro, self.local, # HH
         self.oat, self.humidity, # hb
         self.systemFlags, # B
         self.hour, self.minute, self.second, self.date, self.month, self.year, # bbbbbb
         self.ftHour, self.ftMin, # bb
         ) = struct.unpack('ii HH hh HH hb B bbbbbb bb', buffer)

        self.baroHg = self.millibarsToHg(self.baro)
        self.oatF = self.cToF(self.oat)
        try:
            self.dateTime = datetime.datetime(self.year + 2000, self.month, self.date, self.hour, self.minute, self.second)
        except ValueError as e:
            self.dateTime = None
            self.exception = e


class Gps(MessageData):
    MESSAGETYPE = 2

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
        super().__init__(buffer)
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


class Attitude(MessageData):
    MESSAGETYPE = 3

    headingMag: int
    pitchAngle: int
    bankAngle: int
    yawAngle: int
    turnRate: int
    slip: int
    gForce: int
    lrForce: int
    frForce: int
    bankRate: int
    pitchRate: int
    yawRate: int
    sensorFlags: int

    pitchAngleDegrees: float
    bankAngleDegrees: float
    yawAngleDegrees: float

    def __init__(self, buffer: bytearray):
        super().__init__(buffer)
        (self.headingMag, # H
         self.pitchAngle, self.bankAngle, self.yawAngle, # hhh
         self.turnRate, self.slip, # hh
         self.gForce, self.lrForce, self.frForce, # hhh
         self.bankRate, self.pitchRate, self.yawRate, # hhh
         self.sensorFlags, # b
         ) = struct.unpack_from('H hhh hh hhh hhh b xxx', buffer)

        self.pitchAngleDegrees = self.pitchAngle / 10
        self.bankAngleDegrees = self.bankAngle / 10
        self.yawAngleDegrees = self.yawAngle / 10


class EngineData(MessageData):
    MESSAGETYPE = 10

    engineNumber: int
    engineType: int

    numberOfEgt: int
    numberOfCht: int
    rpm: int
    pulse: int
    oilPressure1: int
    oilPressure2: int
    fuelPressure: int
    coolantTemperature: int
    oilTemperature1: int
    oilTemperature2: int
    auxTemperature1: int
    auxTemperature2: int
    auxTemperature3: int
    auxTemperature4: int
    fuelFlow: int
    auxFlow: int
    manifoldPressure: int
    boostPressure: int
    inletTemperature: int
    ambientPressure: int
    egt: List[int]
    cht: List[int]

    def __init__(self, buffer: bytearray):
        super().__init__(buffer)
        format = 'bb bb HH HHH h hh hhhh HH HH hH ' # 40 bytes
        bufferLen = len(buffer)
        (self.engineNumber, self.engineType, # bb
         self.numberOfEgt, self.numberOfCht, # bb
         self.rpm, self.pulse, # HH
         self.oilPressure1, self.oilPressure2, self.fuelPressure, # HHH
         self.coolantTemperature, # h
         self.oilTemperature1, self.oilTemperature2, # hh
         self.auxTemperature1, self.auxTemperature2, self.auxTemperature3, self.auxTemperature4, # hhhh
         self.fuelFlow, self.auxFlow, # HH
         self.manifoldPressure, self.boostPressure, # HH
         self.inletTemperature, self.ambientPressure, # hH
         ) = struct.unpack_from(format, buffer)

        format = 'h' * self.numberOfEgt + 'h' * self.numberOfCht
        egtChtTemp = struct.unpack_from(format, buffer, 40)
        self.cht = [egtChtTemp[i] for i in range(0, self.numberOfCht * 2, 2)]
        self.egt = [egtChtTemp[i] for i in range(1, self.numberOfEgt * 2 + 1, 2)]

        self.convertUnits()

        return

    def convertUnits(self):
        self.coolantTemperature = self.cToF(self.coolantTemperature)
        self.oilTemperature1 = self.cToF(self.oilTemperature1)
        self.oilTemperature2 = self.cToF(self.oilTemperature2)

        self.auxTemperature1 = self.cToF(self.auxTemperature1)
        self.auxTemperature2 = self.cToF(self.auxTemperature2)
        self.auxTemperature3 = self.cToF(self.auxTemperature3)
        self.auxTemperature4 = self.cToF(self.auxTemperature4)

        self.inletTemperature = self.cToF(self.inletTemperature)

        self.manifoldPressure = self.millibarsToHg(self.manifoldPressure)

        self.oilPressure1 = self.millibarsToPsi(self.oilPressure1)
        self.oilPressure2 = self.millibarsToPsi(self.oilPressure2)

        self.fuelFlow = self.litersToGallons(self.fuelFlow)

        for i in range(0, len(self.egt)):
            self.egt[i] = self.cToF(self.egt[i])
        for i in range(0, len(self.cht)):
            self.cht[i] = self.cToF(self.cht[i])


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
        slice = buffer[self.totalBytes : self.totalBytes + length + 4]
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
        crc = binascii.crc32(buffer) # % (1 << 32) # convert to unsigned CRC32
        if crc != self.checksum:
            raise CrcMismatch(self.totalBytes)

    def __str__(self):
        base = 'Message type {type}'.format(type=self.type)
        if isinstance(self.messageData, PrimaryFlight):
            base += ' at ' + str(self.messageData.dateTime)
        elif isinstance(self.messageData, EngineData):
            base += ' EGT ' + str(self.messageData.egt)
            base += ' CHT ' + str(self.messageData.cht)
        return base


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
        try:
            while totalBytes < len(self.byteStream):
                totalBytes = self.findBeginningOfNextMessage(totalBytes)
                try:
                    message = Message(self.byteStream[totalBytes:])
                    self.messages.append(message)
                    messageTotalBytes = message.totalBytes
                except CrcMismatch as e:
                    messageTotalBytes = e.totalBytes
                totalBytes += messageTotalBytes
        except NoMoreMessages:
            return

    def findBeginningOfNextMessage(self, totalBytes: int) -> int:
        while totalBytes < len(self.byteStream):
            (dle, stx, length, lengthXor) = struct.unpack_from('BBBB', self.byteStream[totalBytes : totalBytes+4])
            calculatedLength = lengthXor ^ 0xff
            if dle == 0x5 and stx == 0x2 and length == calculatedLength:
                return totalBytes
            totalBytes += 1
        raise NoMoreMessages()

    def __str__(self):
        return 'Flight from {earliest} with {count} messages'.format(earliest=self.earliestTimestamp, count=len(self.messages))


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

    def __init__(self, fp: BinaryIO, minTimestamp: int = 0):
        self.filePointer = fp
        self.packets = []
        self.flights = []
        self.readPackets(minTimestamp)
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

    def readPackets(self, minTimestamp: int):
        while True:
            buffer = self.filePointer.read(self.RECORDSIZE)
            if 0 == len(buffer):
                return
            (ts, buf) = struct.unpack_from('I 508s', buffer)
            if 0 != ts and ts >= minTimestamp:
                self.packets.append(Packet(ts, bytearray(buf)))


if '__main__' == __name__:
    with open('data/IEFISBB.DAT', 'rb') as filePointer:
        packetStream = MglPacketStream(filePointer, 479912852)
    print(packetStream)
    print(packetStream.flights)

    for flight in packetStream.flights:
        try:
            flight.analyze()
        except NotAMessage as e:
            pass
        except struct.error as e:
            pass
        except Exception as e:
            print(e)
        finally:
            if 0 < len(flight.messages):
                print(flight)
                for message in flight.messages:
                    print('  ', message)
