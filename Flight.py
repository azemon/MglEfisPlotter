from Message import *


class Flight(object):
    earliestTimestamp: int
    latestTimestamp: int

    messages: List[Message]
    timeStampMap: Dict

    NEWFLIGHTDELTA = 60

    def __init__(self, message: Message):
        self.earliestTimestamp = message.timestamp
        self.latestTimestamp = message.timestamp
        self.messages = [message]

    def addMessage(self, message: Message):
        if message.timestamp > (self.latestTimestamp + self.NEWFLIGHTDELTA):
            raise NotPartOfFlightException()
        self.messages.append(message)
        self.latestTimestamp = message.timestamp

    def getAltitudeData(self) -> Dict:
        dataset = {}
        for message in self.messages:
            if isinstance(message.messageData, PrimaryFlight):
                dataset[message.timestamp] = message.messageData.pAltitude
        return dataset

    def getRpmData(self) -> Dict:
        dataset = {}
        for message in self.messages:
            if isinstance(message.messageData, EngineData):
                dataset[message.timestamp] = message.messageData.rpm
        return dataset

    def getAsi(self) -> Dict:
        dataset = {}
        for message in self.messages:
            if isinstance(message.messageData, PrimaryFlight):
                dataset[message.timestamp] = message.messageData.asi
        return dataset

    def __str__(self):
        t = 'Flight {beginning} to {ending}'.format(
            beginning=self.timeStampMap[self.earliestTimestamp], ending=self.timeStampMap[self.latestTimestamp])
        return t

    def x__str__(self):
        return 'Flight from {earliest} with {count} messages'.format(earliest=self.earliestTimestamp,
                                                                     count=len(self.messages))
