from typing import List

import matplotlib.pyplot as plt
from matplotlib import cycler

from Flight import Flight

class Plot(object):
    flight: Flight
    colors: cycler

    def __init__(self, flight: Flight):
        self.flight = flight
        self.colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

    def listAttributes(self):
        self.flight.listAttributes()

    def plot(self, attr: str, label: str = None):
        data = self.flight.getData(attr)
        if label is None:
            label = attr
        plt.plot(data.keys(), data.values(), label=label)
        plt.ylabel(label)

    def plot2(self, attr: List[str]):
        for i in range(0, len(attr)):
            if 0 == i:
                fig, axis0 = plt.subplots()
                axis = axis0
            else:
                axis = axis0.twinx()

            axis.set_ylabel(attr[i], color=self.colors[i])
            data = self.flight.getData(attr[i])
            axis.plot(data.keys(), data.values(), color=self.colors[i])

    def save(self, fname: str, *args, **kwargs):
        self._addDecorations()
        plt.savefig(fname, *args, **kwargs)

    def show(self):
        self._addDecorations()
        plt.show()

    def _addDecorations(self):
        plt.title(self.flight.title())
        plt.xlabel('Minutes')
