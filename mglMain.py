import matplotlib.pyplot as plt

from MglDataFile import createFlights

def timestampToMinutes(offset, seconds):
    return [(s - offset) / 60.0 for s in seconds]

datafile = 'data/IEFISBB.DAT'
minTimestamp = 479912852

flights = createFlights(datafile, minTimestamp)
flight = flights[0]

altitude = flight.getAltitudeData()
asi = flight.getAsi()
rpm = flight.getRpmData()

fig, axis1 = plt.subplots()

minutes = timestampToMinutes(minTimestamp, altitude.keys())
axis1.plot(minutes, altitude.values(), label='Altitide')

minutes = timestampToMinutes(minTimestamp, rpm.keys())
axis1.plot(minutes, rpm.values(), label='RPM')

minutes = timestampToMinutes(minTimestamp, asi.keys())
axis2 = axis1.twinx()
axis2.plot(minutes, asi.values(), label='Airspeed', color='green')

axis1.set_xlabel('Minutes')
axis1.set_ylabel('Altitude (Feet) & RPM')
axis2.set_ylabel('Airspeed (Knots)', color='green')

# fig.legend(loc='upper right')

plt.title(str(flight))
plt.show()
