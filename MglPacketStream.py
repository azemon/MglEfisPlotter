from typing import BinaryIO

from Flight import *


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
