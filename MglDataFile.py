from Flight import *
from Message import *
from MglPacketStream import *
from TimestampMap import *

flights: List[Flight]
timestampMap: TimestampMap

def createFlights(packetStream: MglPacketStream):
    global flights, timestampMap
    flights = []

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

def printFlights():
    global flights, timestampMap
    for flight in flights:
        flight.print(timestampMap)
        for message in flight.messages:
            message.print(timestampMap, '  ')
        print()

if '__main__' == __name__:
    minTimestamp = 479912852
    datafile = 'data/IEFISBB.DAT'

    with open(datafile, 'rb') as filePointer:
        packetStream = MglPacketStream(filePointer, minTimestamp)

    createFlights(packetStream)
    printFlights()
