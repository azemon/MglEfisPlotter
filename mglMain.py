import matplotlib.pyplot as plt

from MglDataFile import createFlights

datafile = 'data/IEFISBB.DAT'
minTimestamp = 479912852

flights = createFlights(datafile, minTimestamp)
flight = flights[0]

altitude = flight.getData('pAltitude')
asi = flight.getData('asi')
rpm = flight.getData('rpm')

fig, axis1 = plt.subplots()

axis1.plot(altitude.keys(), altitude.values(), label='Altitide')

axis1.plot(rpm.keys(), rpm.values(), label='RPM')

axis2 = axis1.twinx()
axis2.plot(asi.keys(), asi.values(), label='Airspeed', color='green')

axis1.set_xlabel('Minutes')
axis1.set_ylabel('Altitude (Feet) & RPM')
axis2.set_ylabel('Airspeed (Knots)', color='green')

fig.legend(loc='upper right')

plt.title(str(flight))
plt.show()
