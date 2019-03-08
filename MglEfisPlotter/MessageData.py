import datetime
import struct
from typing import List

from .Exceptions import WrongLength


class MessageData(object):
    MESSAGETYPE = None

    rawData: bytearray

    def __init__(self, buffer: bytearray):
        self.rawData = buffer

    def cToF(self, c) -> float:
        return (c * 9 / 5) + 32

    def kphToKnots(self, k) -> float:
        return k / 1.852 / 10

    def litersToGallons(self, liters):
        return liters / 3.785 / 100

    def millibarsToHg(self, m) -> float:
        return m / 33.864 / 10

    def millibarsToPsi(self, m) -> float:
        return m / 68.948

    def __str__(self):
        return 'data={data!s}...'.format(data=self.rawData[:10])


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

        bufferLen = len(buffer)
        if 32 < bufferLen:
            raise WrongLength(bufferLen, 32)

        (self.pAltitude, self.bAltitude,  # ii
         self.asi, self.tas,  # HH
         self.aoa, self.vsi,  # hh
         self.baro, self.local,  # HH
         self.oat, self.humidity,  # hb
         self.systemFlags,  # B
         self.hour, self.minute, self.second, self.date, self.month, self.year,  # bbbbbb
         self.ftHour, self.ftMin,  # bb
         ) = struct.unpack('ii HH hh HH hb B bbbbbb bb', buffer)

        self.asi = self.kphToKnots(self.asi)
        self.tas = self.kphToKnots(self.tas)
        self.aoa /= 10
        self.baro = self.millibarsToHg(self.baro)
        self.oat = self.cToF(self.oat)
        try:
            self.dateTime = datetime.datetime(self.year + 2000, self.month, self.date, self.hour, self.minute,
                                              self.second)
        except ValueError as e:
            self.dateTime = None
            self.exception = e

    def __str__(self):
        return 'PrimaryFlight altitude={alt:.0f} ASI={asi:.0f} VSI={vsi:.0f}'.format(
            alt=self.pAltitude, asi=self.asi, vsi=self.vsi
        )


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
        (self.latitude, self.longitude,  # ii
         self.gpsAltitude, self.agl,  # ii
         self.northVelocity, self.eastVelocity, self.downVelocity,  # iii
         self.groundSpeed, self.trueTrack, self.variation,  # HHh
         self.gps, self.satsTracked, self.satsVisible,  # bbb
         self.horizontalAccuracy, self.verticalAccuracy, self.gpsCapability,  # bbb
         self.raimStatus, self.raimHError, self.raimVError,  # bbb
         ) = struct.unpack_from('ii ii iii HHh bbb bbb bbb x', buffer)

        self.latitude /= 180 / 1000
        self.longitude /= 180 / 1000
        self.groundSpeed = self.kphToKnots(self.groundSpeed)
        self.trueTrack /= 10

    def __str__(self):
        return 'GPS lat={lat:.4f} lon={lon:.4f} speed={speed:.0f} alt={alt:.0f} agl={agl:.0f}'.format(
            lat=self.latitudeDegrees, lon=self.longitudeDegrees, speed=self.groundSpeedKnots,
            alt=self.gpsAltitude, agl=self.agl
        )


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
        (self.headingMag,  # H
         self.pitchAngle, self.bankAngle, self.yawAngle,  # hhh
         self.turnRate, self.slip,  # hh
         self.gForce, self.lrForce, self.frForce,  # hhh
         self.bankRate, self.pitchRate, self.yawRate,  # hhh
         self.sensorFlags,  # b
         ) = struct.unpack_from('H hhh hh hhh hhh b xxx', buffer)

        self.headingMag /= 10
        self.pitchAngle /= 10
        self.bankAngle /= 10
        self.yawAngle /= 10

    def __str__(self):
        return 'Attitude heading={heading:.0f} pitch={pitch:.1f} bank={bank:.1f}'.format(
            heading=self.headingMag, pitch=self.pitchAngleDegrees, bank=self.bankAngleDegrees
        )


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
        format = 'bb bb HH HHH h hh hhhh HH HH hH '  # 40 bytes
        bufferLen = len(buffer)
        (self.engineNumber, self.engineType,  # bb
         self.numberOfEgt, self.numberOfCht,  # bb
         self.rpm, self.pulse,  # HH
         self.oilPressure1, self.oilPressure2, self.fuelPressure,  # HHH
         self.coolantTemperature,  # h
         self.oilTemperature1, self.oilTemperature2,  # hh
         self.auxTemperature1, self.auxTemperature2, self.auxTemperature3, self.auxTemperature4,  # hhhh
         self.fuelFlow, self.auxFlow,  # HH
         self.manifoldPressure, self.boostPressure,  # HH
         self.inletTemperature, self.ambientPressure,  # hH
         ) = struct.unpack_from(format, buffer)

        format = 'h' * self.numberOfEgt + 'h' * self.numberOfCht
        egtChtTemp = struct.unpack_from(format, buffer, 40)
        self.cht = [egtChtTemp[i] for i in range(0, self.numberOfCht * 2, 2)]
        self.egt = [egtChtTemp[i] for i in range(1, self.numberOfEgt * 2 + 1, 2)]

        self.convertUnits()

    def convertUnits(self):
        self.coolantTemperature = self.cToF(self.coolantTemperature)
        self.oilTemperature1 = self.cToF(self.oilTemperature1)
        self.oilTemperature2 = self.cToF(self.oilTemperature2)

        self.auxTemperature1 = self.cToF(self.auxTemperature1)
        self.auxTemperature2 = self.cToF(self.auxTemperature2)
        self.auxTemperature3 = self.cToF(self.auxTemperature3)
        self.auxTemperature4 = self.cToF(self.auxTemperature4)

        self.inletTemperature = self.cToF(self.inletTemperature)

        self.ambientPressure = self.millibarsToHg(self.ambientPressure)
        self.manifoldPressure = self.millibarsToHg(self.manifoldPressure)

        self.oilPressure1 = self.millibarsToPsi(self.oilPressure1)
        self.oilPressure2 = self.millibarsToPsi(self.oilPressure2)

        self.fuelFlow = self.litersToGallons(self.fuelFlow)

        for i in range(0, len(self.egt)):
            self.egt[i] = self.cToF(self.egt[i])
        for i in range(0, len(self.cht)):
            self.cht[i] = self.cToF(self.cht[i])

    def __str__(self):
        return 'EngineData RPM={rpm} OilP={oilp:.0f} OilT={oilt:.0f} MAP={map:.2f} FuelF={fuelf:.1f} EGT={egt!s} CHT={cht!s}'.format(
            rpm=self.rpm, oilp=self.oilPressure1, oilt=self.oilTemperature1,
            map=self.manifoldPressure, fuelf=self.fuelFlow, egt=self.egt, cht=self.cht
        )