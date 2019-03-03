from Exceptions import NotAMessage
from Flight import *
from Message import *
from MglPacketStream import *


def findMessage(packetStream: MglPacketStream) -> Message:
    while True:
        (dle,) = struct.unpack('B', packetStream.read(1))
        if 0x5 == dle:
            break
    (ste,) = struct.unpack('B', packetStream.read(1))
    if 0x5 == ste:
        packetStream.unread(ste)
        return findMessage(packetStream)
    if 0x2 != ste:
        return findMessage(packetStream)
    (length, lengthXor) = struct.unpack('BB', packetStream.read(2))
    if length != (lengthXor ^ 0xff):
        return findMessage(packetStream)

    message = Message(packetStream.timestamp, length, packetStream)
    return message




if '__main__' == __name__:
    minTimestapm = 479912852
    flights = []

    with open('data/IEFISBB.DAT', 'rb') as filePointer:
        packetStream = MglPacketStream(filePointer, minTimestapm)

    flight = None

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
                        #print(e, message)
                        pass
                    except struct.error as e:
                        pass

            except NotPartOfFlightException:
                break
            finally:
                flights.append(flight)

    except EndOfFile as e:
        pass

    for flight in flights:
        print(flight)
        for message in flight.messages:
            print(message)
        print()
