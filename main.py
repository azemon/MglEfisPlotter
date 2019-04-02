from MglEfisPlotter import *

datafile = 'data/IEFISBB.DAT'

flights = createFlights(datafile)

print('Flights:')
for i in range(0, len(flights)):
    print('{num:2d}: {flight}'.format(num=i, flight=flights[i]))

print()
p = Plot(flights[3])
print('p =', p.flight)

p.plot('rpm')
p.show()

p.plot('cht')
p.show()

p.plot('egt')
p.show()

p.plot('oat')
p.show()

p.plot2(['pAltitude', 'asi'])
p.show()

p.flight.saveCsv('csvtest.csv', ['pAltitude', 'vsi'])

p.flight.saveCsv('csvtestall.csv')
