from Flight import *
from Message import *
from MglPacketStream import *
from TimestampMap import *

def createFlights(datafile: str, minTimestamp: int = 0) -> List[Flight]:
    flights: List[Flight] = []

    with open(datafile, 'rb') as filePointer:
        packetStream = MglPacketStream(filePointer, minTimestamp)

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
                        # print(e, message)
                        pass
                    except struct.error as e:
                        pass
            except NotPartOfFlightException:
                break
            finally:
                flights.append(flight)
    except EndOfFile as e:
        pass

    timestampMap = TimestampMap()
    timestampMap.buildFromFlights(flights)

    for flight in flights:
        flight.timeStampMap = timestampMap

    return flights

def printFlights(flights: List[Flight]):
    for flight in flights:
        flight.print()
        for message in flight.messages:
            message.print(flight.timeStampMap, '  ')
        print()

if '__main__' == __name__:
    datafile = 'data/IEFISBB.DAT'
    minTimestamp = 479912852

    flights = createFlights(datafile, minTimestamp)
    printFlights(flights)
