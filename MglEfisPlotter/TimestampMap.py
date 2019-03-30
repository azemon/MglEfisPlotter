from .Flight import *

class TimestampMap(dict):
    """
    map timestamps from the MGL iEFIS records to datetime values, using the real time clock (RTC) from the
    PrimaryFlight records
    """
    lastValue = None
    minKey = 99999999

    def __getitem__(self, item):
        if item < self.minKey:
            raise KeyError
        if item in self.keys():
            foundValue = super().__getitem__(item)
            if foundValue is None:
                return self.__getitem__(item - 1)
            self.lastValue = foundValue
        return self.lastValue

    def __setitem__(self, key, value):
        if key < self.minKey:
            self.minKey = key
        return super().__setitem__(key, value)

    def buildFromFlights(self, flights: List[Flight]) -> None:
        for flight in flights:
            for message in flight.messages:
                if isinstance(message.messageData, PrimaryFlight):
                    self[message.timestamp] = message.messageData.dateTime
