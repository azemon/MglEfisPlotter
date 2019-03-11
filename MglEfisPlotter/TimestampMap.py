from .Flight import *

class TimestampMap(dict):
    """
    map timestamps from the MGL iEFIS records to datetime values, using the real time clock (RTC) from the
    PrimaryFlight records
    """
    lastValue = None

    def __getitem__(self, item):
        if item in self.keys():
            self.lastValue = super().__getitem__(item)
        return self.lastValue

    def buildFromFlights(self, flights: List[Flight]) -> None:
        for flight in flights:
            for message in flight.messages:
                if isinstance(message.messageData, PrimaryFlight):
                    self[message.timestamp] = message.messageData.dateTime
