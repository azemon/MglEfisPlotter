import matplotlib.pyplot as plt

from Flight import Flight
from MglDataFile import createFlights

def plot(flight: Flight, attr: str, label: str = None):
    data = flight.getData(attr)
    if label is None:
        label = attr
    plt.plot(data.keys(), data.values(), label=label)

def show():
    plt.legend(loc='best')
    plt.show()

datafile = 'data/IEFISBB.DAT'
minTimestamp = 0

flights = createFlights(datafile, minTimestamp)

for i in range(0, len(flights)):
    print(i, ':', flights[i])
