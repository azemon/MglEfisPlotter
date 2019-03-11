from collections import OrderedDict
from typing import List

import matplotlib.pyplot as plt
from matplotlib import cycler

from .Flight import Flight


class Plot(object):
    """
    wrapper for plotting with matplotlib pyplot
    """

    flight: Flight
    colors: cycler
        
    dpi = 100
    figsize = (12, 8)
    fontsize = 12
    
    def __init__(self, flight: Flight):
        self.flight = flight
        self.colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    
    def data(self, attr: str) -> OrderedDict:
        return self.flight.getData(attr)

    def listAttributes(self) -> None:
        self.flight.listAttributes()

    def plot(self, attr: str, label: str = None) -> None:
        """
        plot one attribute
        :param attr:
        :param label:
        :return:
        """
        plt.figure(figsize=self.figsize, dpi=self.dpi)
        data = self.data(attr)
        if label is None:
            label = attr
        plt.plot(data.keys(), data.values())
        plt.ylabel(label, fontsize=self.fontsize)
            
        values = list(data.values())
        if isinstance(values[0], list):
            self._addLegend(len(values))

    def plot2(self, attr: List[str]) -> None:
        """
        Plot several attributes
        :param attr: List of attributes
        :return:
        """
        for i in range(0, len(attr)):
            if 0 == i:
                fig, axis0 = plt.subplots(figsize=self.figsize, dpi=self.dpi)
                axis = axis0
                axis0.set_xlabel('Minutes')
            else:
                axis = axis0.twinx()
                offset = 1 + ((i - 1) * 0.15)
                axis.spines['right'].set_position(('axes', offset))

            axis.set_ylabel(attr[i], color=self.colors[i], fontsize=self.fontsize)
            data = self.data(attr[i])
            axis.plot(data.keys(), data.values(), color=self.colors[i])
    
    def save(self, fname: str, *args, **kwargs) -> None:
        """
        save the figure that has been plotted
        :param fname:
        :param args:
        :param kwargs:
        :return:
        """
        self._addDecorations()
        plt.savefig(fname, *args, **kwargs)

    def show(self) -> None:
        """
        show (display on the sreen) the figure that has been plotted
        :return:
        """
        self._addDecorations()
        plt.show()

    def _addDecorations(self) -> None:
        plt.title(self.flight.title())
        plt.xlabel('Minutes', fontsize=self.fontsize)
    
    def _addLegend(self, qty: int):
        labels = ['#{}'.format(n) for n in range(1, qty+1)]
        plt.legend(labels, loc='best')
