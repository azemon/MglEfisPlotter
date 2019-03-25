class Config(object):
    units = {
        'airspeed': 'knots', # 'knots' or 'kph'
        'barometer': 'hg', # 'hg' or 'millibars'
        'fuel': 'gallons', # 'gallons' or 'liters'
        'manifoldPressure': 'hg', # 'hg' or 'millibars'
        'oilPressure': 'psi', # 'psi' or 'millibars'
        'temperature': 'f', # 'f' or 'c'
    }

    # set each themocouple value to one of 'cht' or 'egt' or None (capitalized and without quotation marks)
    # the values that you set here must match the configuration of your RDAC
    thermocouples = {
        1: 'cht',
        2: 'egt',
        3: 'cht',
        4: 'egt',
        5: 'cht',
        6: 'egt',
        7: 'cht',
        8: 'egt',
        9: None,
        10: None,
        11: None,
        12: None,
    }

    # iEFIS seems to add about 260 seconds to the timestamp at the top of the hour
    NewFlightDelta = 300
