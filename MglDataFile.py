from MglPacketStream import *



if '__main__' == __name__:
    minTimestapm = 479912852

    with open('data/IEFISBB.DAT', 'rb') as filePointer:
        packetStream = MglPacketStream(filePointer, minTimestapm)
    print(packetStream)
    print(packetStream.flights)

    for flight in packetStream.flights:
        try:
            flight.analyze()
        except NotAMessage as e:
            pass
        except Exception as e:
            print(e)
        finally:
            if 0 < len(flight.messages):
                print(flight)
                for message in flight.messages:
                    print('  ', message)
