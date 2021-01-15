def calculate_okta(percentage):
    """
    Calculate okta based on the provided percentage
    :param percentage: percentage between 0 and 100
    :type percentage: float
    :return: an integer between 0 and 8
    :rtype: int
    """
    if percentage == 0:
        return 0
    elif 0 < percentage < 18.75:
        return 1
    elif 18.75 <= percentage < 31.25:
        return 2
    elif 31.25 <= percentage < 43.75:
        return 3
    elif 43.75 <= percentage < 56.25:
        return 4
    elif 56.25 <= percentage < 68.75:
        return 5
    elif 68.75 <= percentage < 81.25:
        return 6
    elif 81.25 <= percentage < 100:
        return 7
    elif percentage == 100:
        return 8
    else:
        raise ValueError('percentage is not between 0-100')


def ms_to_knots(ms):
    """
    Convert meters per second (m/s) to knots
    :param ms: meters per second (m/s)
    :type ms: float
    :return: knots
    :rtype: float
    """
    return ms * 1.94384449


def mph_to_knots(mph):
    """
    Convert miles per hour (mph) to knots
    :param mph: miles per hour (mph)
    :type mph: float
    :return: knots
    :rtype: float
    """
    return mph * 0.868976242


def mph_to_ms(mph):
    """
    Convert miles per hour to meters per second
    :param mph: miles per hour (mph)
    :type mph: float
    :return: meters per second
    :rtype: float
    """
    return mph * 0.44704


def ms_to_mph(ms):
    """
    Convert miles per hour to meters per second
    :param ms: meters per second (ms)
    :type ms: float
    :return: miles per hour
    :rtype: float
    """
    return ms / 0.44704


def __get_wind_adjustment(wind_speed):
    """
    Calculate the wind adjustment value by wind speed
    :param float wind_speed:
    :return:
    """
    if wind_speed < 0:
        raise ValueError('wind speed cannot be negative')
    if 0 <= wind_speed <= 12:
        wind = 1
    elif 13 <= wind_speed <= 25:
        wind = 2
    else:
        wind = 0

    return wind


def __get_cloud_adjustment(okta):
    """
    Calculate the cloud adjustment value by okta
    :param int okta: okta value between 0 and 8
    :return:
    """
    if 0 <= okta < 2:
        cloud = 1
    elif 2 <= okta < 4:
        cloud = 2
    elif 4 <= okta < 6:
        cloud = 3
    elif okta >= 6:
        cloud = 4
    elif okta < 0 or okta > 8:
        raise ValueError('Okta has to be between 0 and 8')

    return cloud


def __calculate_adjustment(okta, wind_speed):
    """
    Calculate adjustment needed for fog probability using okta and wind speed.
    Source: http://www.skystef.be/calculator-fog.htm
    :param okta: okta
    :type okta: int
    :param wind_speed: wind speed
    :type wind_speed: float
    :return:
    :rtype: float
    """
    wind = __get_wind_adjustment(wind_speed)
    cloud = __get_cloud_adjustment(okta)

    if wind == 0:
        return 0.5

    if wind == 1 and cloud == 1:
        return 0
    elif wind == 1 and cloud == 2:
        return 0
    elif wind == 1 and cloud == 3:
        return 1
    elif wind == 1 and cloud == 4:
        return 1.5

    if wind == 2 and cloud == 1:
        return -1.5
    elif wind == 2 and cloud == 2:
        return 0
    elif wind == 2 and cloud == 3:
        return 0.5
    elif wind == 2 and cloud == 4:
        return 0.5


def calculate_fog_temperature(temperature, dew_point, okta, wind_speed):
    """
    Calculate the fog temperature needed for fog probability
    Source: http://www.skystef.be/calculator-fog.htm

    :param temperature: temperature in celsius
    :type temperature: float
    :param dew_point: dew point in celsius
    :type dew_point: float
    :param okta: okta
    :type okta: int
    :param wind_speed: wind speed
    :type wind_speed: float
    :return: fog temperature in celsius
    :rtype: float
    """
    adjustment = __calculate_adjustment(okta, wind_speed)
    return (0.044 * temperature) + (0.844 * dew_point) - 0.55 + adjustment


def calculate_fog_probability(min_temperature, fog_temperature):
    """
    Calculate fog probability using Craddock & Pritchard method.
    Provide forecasted minimum temperature and calculate fog temperature.

    ≥ +1	        Widespread fog
    = 0.5	        Risk for fog at end of night
    = 0	            Fog patches around sunrise
    -0.5 to -1.5    Fog patches on favorable spots
    ≤ -2            No fog

    Source: http://www.skystef.be/calculator-fog.htm

    :param min_temperature: forecasted minimum temperature in celsius
    :type min_temperature: float
    :param fog_temperature: calculated fog temperature in celsius
    :type fog_temperature: float
    :return: fog probability on a scale of 1 to 5 where 5 has wide spread fog
    :rtype: int
    """
    difference = fog_temperature - min_temperature

    if difference >= 1:
        return 5
    elif .5 <= difference < 1:
        return 4
    elif -.5 <= difference < .5:
        return 3
    elif -1.5 < difference < -.5:
        return 2
    else:
        return 1
