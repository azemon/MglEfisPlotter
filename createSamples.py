from MglEfisPlotter import *

datafile = 'data/IEFISBB.DAT'
minTimestamp = 429600874
maxTimestamp = 1000000000

flights = createFlights(datafile, minTimestamp, maxTimestamp)

p = Plot(flights[4])
p.plot('pAltitude')
p.save('samples/altitude.png')

p = Plot(flights[4])
p.plot2(['oilPressure1', 'oilTemperature1'])
p.save('samples/oil.png')

p = Plot(flights[4])
p.plot2(['asi', 'groundSpeed'])
p.save('samples/speed.png')
