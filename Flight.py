from collections import OrderedDict

from Message import *


class Flight(object):
    earliestTimestamp: int
    latestTimestamp: int

    messages: List[Message]
    timeStampMap: Dict

    NEWFLIGHTDELTA = 300

    def __init__(self, message: Message):
        self.earliestTimestamp = message.timestamp
        self.latestTimestamp = message.timestamp
        self.messages = [message]

    def addMessage(self, message: Message):
        if self.earliestTimestamp > message.timestamp:
            raise NotPartOfFlightException(
                'too early: {early} > {message}'.format(early=self.earliestTimestamp, message=message.timestamp))
        if message.timestamp > (self.latestTimestamp + self.NEWFLIGHTDELTA):
            raise NotPartOfFlightException(
                'too late: {message} > ({latest} + {delta})'.format(message=message.timestamp, latest=self.latestTimestamp, delta=self.NEWFLIGHTDELTA))
        self.messages.append(message)
        self.latestTimestamp = message.timestamp

    def getData(self, element: str) -> OrderedDict:
        dataset = OrderedDict()
        for message in self.messages:
            if hasattr(message.messageData, element):
                dataset[self.timestampToMinutes(message.timestamp)] = message.messageData.__getattribute__(element)
        return dataset

    def listAttributes(self):
        attributes = []
        for message in self.messages:
            for attribute, value in message.messageData.__dict__.items():
                if isinstance(value, (int, float)) and 0 != value and attribute not in attributes:
                    attributes.append(attribute)
        attributes.sort()
        for a in attributes:
            print(a)

    def timestampToMinutes(self, ts: int) -> float:
        return (ts - self.earliestTimestamp) / 60.0

    def __str__(self):
        t = 'Flight from {beginning} to {ending}, {qty:5d} messages, {begin:,} - {end:,}'.format(
            beginning=self.timeStampMap[self.earliestTimestamp],
            ending=self.timeStampMap[self.latestTimestamp],
            qty=len(self.messages),
            begin=self.earliestTimestamp,
            end=self.latestTimestamp,
        )
        return t
