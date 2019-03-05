import matplotlib.pyplot as plt

from Flight import Flight
from MglDataFile import createFlights

def printFlights(flights):
    print('Flights:')
    for i in range(0, len(flights)):
        print('{num:2d}: {flight!s}'.format(num=i, flight=flights[i]))


def plot(flight: Flight, attr: str, label: str = None):
    data = flight.getData(attr)
    if label is None:
        label = attr
    plt.plot(data.keys(), data.values(), label=label)

def show():
    plt.legend(loc='best')
    plt.show()


datafile = 'data/IEFISBB.DAT'
minTimestamp = 429600874
maxTimestamp = 1000000000

flights = createFlights(datafile, minTimestamp, maxTimestamp)
printFlights(flights)
