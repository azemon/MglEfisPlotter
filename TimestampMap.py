from Flight import *

class TimestampMap(dict):
    lastValue = None

    def __getitem__(self, item):
        if item in self.keys():
            self.lastValue = super().__getitem__(item)
        return self.lastValue

    def buildFromFlights(self, flights: List[Flight]):
        for flight in flights:
            for message in flight.messages:
                if isinstance(message.messageData, PrimaryFlight):
                    self[message.timestamp] = message.messageData.dateTime
