class TimestampMap(dict):
    lastValue = None

    def __getitem__(self, item):
        if item in self.keys():
            self.lastValue = super().__getitem__(item)
        return self.lastValue
