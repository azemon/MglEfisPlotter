from Message import *


class Flight(object):
    earliestTimestamp: int
    latestTimestamp: int

    messages: List[Message]

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

    def print(self, timeStampMap: Dict[int, datetime.datetime]):
        print('Flight {beginning} to {ending} with {count} messages'.format(
            beginning=timeStampMap[self.earliestTimestamp], ending=timeStampMap[self.latestTimestamp],
            count=len(self.messages)))

    def __str__(self):
        return 'Flight from {earliest} with {count} messages'.format(earliest=self.earliestTimestamp,
                                                                     count=len(self.messages))
