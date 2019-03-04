import matplotlib.pyplot as plt

from MglDataFile import createFlights

datafile = 'data/IEFISBB.DAT'
minTimestamp = 0

flights = createFlights(datafile, minTimestamp)

for i in range(0, len(flights)):
    print(i, ':', flights[i])
