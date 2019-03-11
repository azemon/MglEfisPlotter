from .Flight import *
from .Message import *
from .MglPacketStream import *
from .TimestampMap import *


def createFlights(datafile: str, minTimestamp: int = 0, maxTimestamp: int = 9000000000) -> List[Flight]:
    """
    create a list of flights from an IEFISBB.DAT datafile
    :param datafile:
    :param minTimestamp:
    :param maxTimestamp:
    :return: List[Flight]
    """

    flights: List[Flight] = []

    with open(datafile, 'rb') as filePointer:
        packetStream = MglPacketStream(filePointer, minTimestamp, maxTimestamp)

    try:
        while True:
            message = findMessage(packetStream)
            flight = Flight(message)
            try:
                while True:
                    try:
                        message = findMessage(packetStream)
                        flight.addMessage(message)
                    except NotAMessage as e:
                        pass
                    except struct.error as e:
                        pass
            except NotPartOfFlightException as e:
                pass
            finally:
                flights.append(flight)
    except EndOfFile as e:
        pass

    timestampMap = TimestampMap()
    timestampMap.buildFromFlights(flights)

    for flight in flights:
        flight.timeStampMap = timestampMap

    return flights
