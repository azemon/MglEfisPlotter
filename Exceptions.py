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


class NoMoreMessages(Exception):
    def __init__(self, m=''):
        super().__init__('Not part of flight' + m)

class EndOfFile(Exception):
    pass

class EndOfPacket(Exception):
    pass
