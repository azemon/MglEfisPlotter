from MglEfisPlotter import *

datafile = 'notebooks/flight08/IEFISBB.DAT'

minTimestamp = 485957362

flights = createFlights(datafile, minTimestamp)

print('Flights:')
for i in range(0, len(flights)):
    print('{num:2d}: {flight}'.format(num=i, flight=flights[i]))

print()
p = Plot(flights[-1])
print('p =', p.flight)

p.plot2(['pAltitude', 'asi'])
p.show()

p.flight.saveCsv('/home/azemon/Desktop/export.csv', ['pAltitude', 'asi', 'vsi'])
