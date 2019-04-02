from collections import OrderedDict
from typing import List

import matplotlib.pyplot as plt
from matplotlib import cycler
import pandas as pd

from .Config import Config
from .Flight import Flight


class Plot(object):
    """
    wrapper for plotting with matplotlib pyplot
    """

    flight: Flight
    colors: cycler

    def __init__(self, flight: Flight):
        self.flight = flight
        self.colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    
    def data(self, attr: str) -> OrderedDict:
        return self.flight.getPlotData(attr)

    def listAttributes(self) -> None:
        self.flight.listAttributes()

    def plot(self, attr: str, label: str = None, **kwargs) -> 'Plot':
        """
        plot one attribute
        :param attr:
        :param label:
        :param **kwargs: xlim, ylim
        :return:
        """
        plt.figure(figsize=Config.plotDimensions, dpi=Config.plotDPI, constrained_layout=True)
        data = self.data(attr)
        if self._isScalar(data[0]):
            df = pd.DataFrame(data.values(), columns=[attr])
            df = df.rolling(Config.rollingWindow, min_periods=1).mean()
            y = df[attr]
        else:
            y = data.values()
        if label is None:
            label = attr
        plt.plot(data.keys(), y)
        plt.ylabel(label, fontsize=Config.plotFontSize)
            
        values = list(data.values())
        if isinstance(values[0], list):
            self._addLegend(len(values))

        if 'xlim' in kwargs.keys():
            plt.xlim(kwargs['xlim'])
            del kwargs['xlim']
        if 'ylim' in kwargs.keys():
            plt.ylim(kwargs['ylim'])
            del kwargs['ylim']
        if 0 < len(kwargs.keys()):
            raise Exception('Unknown keyword argument: ' + list(kwargs.keys())[0])
        
        return self

    def plot2(self, attr: List[str], labels: List[str] = None, **kwargs) -> 'Plot':
        """
        Plot several attributes
        :param attr: List of attributes
        :param labels: List of labels
        :param **kwargs: xlim, ylim
        :return:
        """
        if labels is None:
            labels = attr

        for i in range(0, len(attr)):
            if 0 == i:
                fig, axis0 = plt.subplots(figsize=Config.plotDimensions, dpi=Config.plotDPI, constrained_layout=True)
                axis = axis0
                axis0.set_xlabel('Minutes')
                if 'xlim' in kwargs.keys():
                    plt.xlim(kwargs['xlim'])
                    del kwargs['xlim']
                if 'ylim' in kwargs.keys():
                    plt.ylim(kwargs['ylim'])
                    del kwargs['ylim']
            else:
                axis = axis0.twinx()
                offset = 1 + ((i - 1) * 0.1)
                axis.spines['right'].set_position(('axes', offset))

            axis.set_ylabel(labels[i], color=self.colors[i], fontsize=Config.plotFontSize)
            data = self.data(attr[i])
            if self._isScalar(data[0]):
                df = pd.DataFrame(data.values())
                df = df.rolling(Config.rollingWindow, min_periods=1).mean()
                y = df.values.tolist()
            else:
                y = data.values()
            axis.plot(data.keys(), y, color=self.colors[i])

        if 0 < len(kwargs.keys()):
            raise Exception('Unknown keyword argument: ' + list(kwargs.keys())[0])
        
        return self

    def _isScalar(self, n) -> bool:
        return not hasattr(n, '__len__')
    
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
        plt.xlabel('Minutes', fontsize=Config.plotFontSize)
    
    def _addLegend(self, qty: int):
        labels = ['#{}'.format(n) for n in range(1, qty+1)]
        plt.legend(labels, loc='best')
