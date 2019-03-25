from collections import OrderedDict

from .Config import *
from .Message import *


class Flight(object):
    """
    Data from one flight, beginning at earliestTimestamp and ending at latestTimestamp
    """

    earliestTimestamp: int
    latestTimestamp: int

    messages: List[Message]
    timeStampMap: Dict

    NEWFLIGHTDELTA = Config.NewFlightDelta

    def __init__(self, message: Message):
        self.earliestTimestamp = message.timestamp
        self.latestTimestamp = message.timestamp
        self.messages = [message]

    def addMessage(self, message: Message) -> None:
        """
        add an EFIS message to a flight
        :param message:
        :return:
        :raise: NotPartOfFlightException when the message's timestamp is > NEWFLIGHTDELTA after the flight's latestTimestamp
        """
        if self.earliestTimestamp > message.timestamp:
            raise NotPartOfFlightException(
                'too early: {early} > {message}'.format(early=self.earliestTimestamp, message=message.timestamp))

        if message.timestamp > (self.latestTimestamp + self.NEWFLIGHTDELTA):
            raise NotPartOfFlightException(
                'too late: {message} > ({latest} + {delta})'.format(message=message.timestamp, latest=self.latestTimestamp, delta=self.NEWFLIGHTDELTA))

        self.messages.append(message)
        self.latestTimestamp = message.timestamp

    def getData(self, element: str) -> OrderedDict:
        """
        returns an OrderedDict of (minutes, datum) for use with Plot.
        Minutes starts at 0 at the beginning of the flight.
        Minutes is a float and there may be multiple data with the same minute value.
        :param element:
        :return:
        """
        dataset = OrderedDict()
        for message in self.messages:
            if hasattr(message.messageData, element):
                dataset[self.timestampToMinutes(message.timestamp)] = message.messageData.__getattribute__(element)
        return dataset

    def listAttributes(self) -> None:
        """
        prints a list of datum element names which can be used with getData() and listData()
        :return:
        """
        attributes = []
        for message in self.messages:
            for attribute, value in message.messageData.__dict__.items():
                if isinstance(value, (int, float)) and 0 != value and attribute not in attributes:
                    attributes.append(attribute)
        attributes.sort()
        for a in attributes:
            print(a)
    
    def listData(self, element: str) -> Dict[str, List]:
        """
        returns a Dict of lists of {minutes, timestamp, datum} for use in a pandas DataFrame.
        Minutes starts at 0 at the beginning of the flight.
        There may be multiple data with the same minute and timestamp values.
        :param element:
        :return:
        """
        minutes = []
        timestamp = []
        data = []
        for message in self.messages:
            if hasattr(message.messageData, element):
                minutes.append(self.timestampToMinutes(message.timestamp))
                timestamp.append(message.timestamp)
                data.append(message.messageData.__getattribute__(element))
        return {
            'minutes': minutes,
            'timestamp': timestamp,
            element: data,
        }

    def timestampToMinutes(self, ts: int) -> float:
        return (ts - self.earliestTimestamp) / 60.0

    def timestampToSeconds(self, ts: int) -> int:
        return ts - self.earliestTimestamp

    def title(self) -> str:
        """
        :return: a short title for use on graphs and reports
        """
        return 'Flight at {beginning}'.format(beginning=self._earliestDateString())

    def _earliestDateString(self) -> str:
        """
        return the earliest datetime as a string.
        usually that is the earliest timestamp but occasionally there was no RTC value for the timestamp,
        when that happens, find something else
        :return:
        """
        ds = self.timeStampMap[self.earliestTimestamp]
        if ds is not None:
            return ds

        earliest = min(list(self.timeStampMap.keys()))
        return self.timeStampMap[earliest]

    def _latestDateString(self) -> str:
        """
        return the latest datetime as a string.
        usually that is the latest timestamp but occasionally there was no RTC value for the timestamp,
        when that happens, find something else
        :return:
        """
        ds = self.timeStampMap[self.latestTimestamp]
        if ds is not None:
            return ds

        latest = max(list(self.timeStampMap.keys()))
        return self.timeStampMap[latest]

    def __str__(self):
        t = 'Flight at {beginning} to {ending}, {qty:5d} messages, timestamps {begin:,d} to {end:,d}'.format(
            beginning=self._earliestDateString(),
            ending=self._latestDateString(),
            qty=len(self.messages),
            begin=self.earliestTimestamp,
            end=self.latestTimestamp,
        )
        return t
