from MglEfisPlotter import *

def printFlights(flights):
    print('Flights:')
    for i in range(0, len(flights)):
        print('{num:2d}: {flight}'.format(num=i, flight=flights[i]))


datafile = 'data/IEFISBB.DAT'
minTimestamp = 429600874
maxTimestamp = 1000000000

flights = createFlights(datafile, minTimestamp, maxTimestamp)

printFlights(flights)

print()
p = Plot(flights[3])
print('p =', p.flight)

p.plot('rpm')
p.show()
