class NotPartOfFlightException(Exception):
    def __init__(self, m=''):
        super().__init__('Not part of flight' + m)


class NotAMessage(Exception):
    def __init__(self, m=''):
        super().__init__('Not a message' + m)


class CrcMismatch(NotAMessage):
    totalBytes: int

    def __init__(self, totalBytes: int, m=''):
        self.totalBytes = totalBytes
        super().__init__('CRC Mismatch' + m)


class WrongLength(NotAMessage):
    actual: int
    expected: int

    def __init__(self, actual: int, expected: int, m=''):
        self.actual = actual
        self.expected = expected
        super().__init__('Wrong buffer length' + m)


class NoMoreMessages(Exception):
    def __init__(self, m=''):
        super().__init__('Not part of flight' + m)


class EndOfFile(Exception):
    pass


class EndOfRecord(Exception):
    pass
