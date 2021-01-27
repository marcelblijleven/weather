import requests

from climacell.utils import join_fields, check_datetime_str, parse_datetime_str


class Client:
    def __init__(self, api_key):
        self.base_url = "https://api.climacell.co/v3"
        self.api_key = api_key

    def _do_request(self, endpoint, params):
        """
        Execute the request with the provided parameters
        :param string endpoint: endpoint to call
        :param dict params: parameters to add to request
        :return: request result
        """

        headers = {
            'apikey': self.api_key
        }

        return requests.get(self.base_url + endpoint, params=params, headers=headers)

    def _forecast(self, endpoint, lat, lon, fields, start_time, end_time, units):
        """
        Get a forecast response

        :param float lat: location latitude
        :param float lon: location longitude
        :param list[str] fields: requested data fields
        :param str start_time: ISO 8601 or 'now'
        :param str end_time: ISO 8601 or None
        :param str units: si or us
        :return: returns an hourly forecast response
        :rtype: Response
        """
        params = {
            'lat': lat,
            'lon': lon,
            'start_time': start_time,
            'unit_system': units,
            'fields': join_fields(fields),
        }

        if start_time != 'now' and not check_datetime_str(start_time):
            raise ValueError('Invalid start time provided')

        if end_time is not None:
            if not check_datetime_str(end_time):
                raise ValueError('Invalid end time provided')
            else:
                params['end_time'] = end_time

        response = self._do_request(endpoint, params)
        return Response(response, fields)

    def hourly(self, lat, lon, fields, start_time='now', end_time=None, units='si'):
        """
        Get the hourly forecast with a maximum of 108 hours out

        :param float lat: location latitude
        :param float lon: location longitude
        :param list[str] fields: requested data fields
        :param str start_time: ISO 8601 or 'now'
        :param str end_time: ISO 8601 or None
        :param str units: si or us
        :return: returns an hourly forecast response
        :rtype: Response
        """
        endpoint = '/weather/forecast/hourly'
        return self._forecast(endpoint, lat, lon, fields, start_time, end_time, units)

    def nowcast(self, lat, lon, fields, timestep, start_time='now', end_time=None, units='si'):
        """
        Get the nowcast forecast with a maximum of 360 minutes out

        :param float lat:
        :param float lon:
        :param list[str] fields:
        :param int timestep:
        :param str start_time:
        :param str end_time:
        :param str units:
        :return: returns a nowcast forecast response
        :rtype: Response
        """
        params = {
            'lat': lat,
            'lon': lon,
            'timestep': timestep,
            'start_time': start_time,
            'unit_system': units,
            'fields': join_fields(fields),
        }

        if start_time != 'now' and not check_datetime_str(start_time):
            raise ValueError('Invalid start time provided')

        if end_time is not None:
            if not check_datetime_str(end_time):
                raise ValueError('Invalid end time provided')
            else:
                params['end_time'] = end_time

        endpoint = '/weather/nowcast'
        response = self._do_request(endpoint, params)
        return Response(response, fields)

    def daily(self, lat, lon, fields, start_time='now', end_time=None, units='si'):
        """
        Get the nowcast forecast with a maximum of 15 days out

        :param float lat:
        :param float lon:
        :param list[str] fields:
        :param str start_time:
        :param str end_time:
        :param str units:
        :return: returns a daily forecast response
        :rtype: Response
        """
        endpoint = '/weather/forecast/daily'
        return self._forecast(endpoint, lat, lon, fields, start_time, end_time, units)


class Error:
    def __init__(self, response_json):
        self.json = response_json
        self.message = response_json['message']
        self.code = response_json['errorCode']
        self.status_code = response_json['statusCode']

    def __str__(self):
        return f'{self.code} ({self.status_code}): {self.message}'


class Response:
    def __init__(self, response, fields):
        """
        :param requests.Response response:
        :param list[str] fields:
        """
        self.response = response
        self.fields = fields
        self.json = response.json()
        self.status_code = response.status_code

    def get_measurements(self):
        if self.has_error:
            return Error(self.response.json())

        measurements = []

        for item in self.json:
            for field in self.fields:
                if isinstance(item[field], list):
                    # This is a daily forecast, with a min and max observed value
                    # Todo: better handling of different types of responses
                    min_measurement = item[field][0]
                    max_measurement = item[field][1]
                    min_value = min_measurement['min']['value']
                    max_value = max_measurement['max']['value']
                    min_unit = min_measurement['min'].get('units', None)
                    max_unit = max_measurement['max'].get('units', None)
                    min_observation_time = min_measurement['observation_time']
                    max_observation_time = max_measurement['observation_time']
                    measurements.append(Measurement(field + '_min', min_value, min_unit, min_observation_time))
                    measurements.append(Measurement(field + '_max', max_value, max_unit, max_observation_time))
                else:
                    # Regular measurement
                    value = item[field]['value']

                    try:
                        units = item[field]['units']
                    except KeyError:
                        units = None

                    observation_time = item['observation_time']['value']
                    measurements.append(Measurement(field, value, units, observation_time))

        return measurements

    @property
    def has_error(self):
        return self.status_code != 200


class Measurement:
    def __init__(self, field, value, unit, observation_time):
        self.field = field
        self.value = value
        self.unit = unit
        self.observation_time = parse_datetime_str(observation_time)

    def __str__(self):
        if self.unit is not None:
            return f'{self.field}: {self.value} {self.unit} at {self.observation_time}'

        return f'{self.field}: {self.value} at {self.observation_time}'
