from collections import OrderedDict

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

    def getData(self, element: str) -> OrderedDict:
        dataset = OrderedDict()
        for message in self.messages:
            if hasattr(message.messageData, element):
                dataset[self.timestampToMinutes(message.timestamp)] = message.messageData.__getattribute__(element)
        return dataset

    def listAttributes(self) -> List:
        attributes = []
        for message in self.messages:
            for attribute, value in message.messageData.__dict__.items():
                if isinstance(value, (int, float)) and 0 != value and attribute not in attributes:
                    attributes.append(attribute)
        attributes.sort()
        return attributes

    def timestampToMinutes(self, ts: int) -> float:
        return (ts - self.earliestTimestamp) / 60.0

    def __str__(self):
        t = 'Flight at {beginning}, {qty} messages'.format(
            beginning=self.timeStampMap[self.earliestTimestamp], qty=len(self.messages))
        return t
