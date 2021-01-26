import json
import os

from unittest import TestCase, mock
from climacell.api import Client, Measurement, Response, Error
from climacell.fields import (
    FIELD_TEMP, FIELD_DEW_POINT, FIELD_HUMIDITY,
    FIELD_WIND_SPEED, FIELD_WIND_GUST, FIELD_WIND_DIRECTION,
    FIELD_SUNRISE, FIELD_SUNSET,
)
from climacell.utils import join_fields


ERROR_FILE = os.path.dirname(__file__) + '/data/error_example.json'
HOURLY_FILE = os.path.dirname(__file__) + '/data/hourly_example.json'
NOWCAST_FILE = os.path.dirname(__file__) + '/data/nowcast_example.json'


class MockResponse:
    def __init__(self, data, status_code):
        self.data = data
        self.status_code = status_code

    def json(self):
        return self.data


def mock_requests_get(*args, **kwargs):
    base_url = 'https://api.climacell.co/v3'

    if args[0] is None:
        return MockResponse(None, 404)
    elif args[0] == base_url + '/weather/forecast/hourly':
        file = HOURLY_FILE
    elif args[0] == base_url + '/weather/nowcast':
        file = NOWCAST_FILE

    with open(file) as json_file:
        data = json.load(json_file)

    return MockResponse(data, 200)


class TestMeasurement(TestCase):
    def test_measurement__str__(self):
        m = Measurement('temp', 13.04, 'C', '2021-01-14T21:00:00.000Z')
        self.assertEqual('temp: 13.04 C at 2021-01-14 21:00:00+00:00', str(m))

        m = Measurement('temp', 13.04, None, '2021-01-14T21:00:00.000Z')
        self.assertEqual('temp: 13.04 at 2021-01-14 21:00:00+00:00', str(m))


class TestResponse(TestCase):
    def test_get_measurements_error(self):
        with open(ERROR_FILE) as f:
            data = json.load(f)
        mock_response = MockResponse(data, 400)
        response = Response(mock_response, [FIELD_TEMP, FIELD_DEW_POINT, FIELD_HUMIDITY])

        self.assertTrue(response.has_error)
        error = response.get_measurements()
        self.assertTrue(isinstance(error, Error))


class TestError(TestCase):
    def test_error(self):
        with open(ERROR_FILE) as f:
            data = json.load(f)

        error = Error(data)

        self.assertEqual(400, error.status_code)
        self.assertEqual('Message body content not allowed.', error.message)
        self.assertEqual('BadRequest', error.code)

    def test_error_str(self):
        with open(ERROR_FILE) as f:
            data = json.load(f)

        error = Error(data)
        expected_str = 'BadRequest (400): Message body content not allowed.'
        self.assertEqual(expected_str, str(error))


class TestClient(TestCase):
    @mock.patch('climacell.api.requests.get', side_effect=mock_requests_get)
    def test_hourly(self, mock_get):
        client = Client('apikey')
        lat = 52.446023244274045
        lon = 4.819207798979252
        fields = [FIELD_TEMP, FIELD_DEW_POINT, FIELD_HUMIDITY]

        response = client.hourly(lat=lat, lon=lon, fields=fields)
        measurements = response.get_measurements()

        expected_params = {
            'lat': 52.446023244274045,
            'lon': 4.819207798979252,
            'start_time': 'now',
            'unit_system': 'si',
            'fields': join_fields([FIELD_TEMP, FIELD_DEW_POINT, FIELD_HUMIDITY]),
        }

        mock_get.assert_called_with(
            'https://api.climacell.co/v3/weather/forecast/hourly',
            params=expected_params,
            headers={'apikey': 'apikey'}
        )

        self.assertEqual(6, len(measurements))

    def test_hourly_invalid_start_time(self):
        client = Client('apikey')
        lat = 52.446023244274045
        lon = 4.819207798979252
        fields = [FIELD_TEMP, FIELD_DEW_POINT, FIELD_HUMIDITY]
        start_time = 'yesterday'

        self.assertRaises(
            ValueError, client.hourly, lat, lon, fields, start_time
        )

    def test_hourly_invalid_end_time(self):
        client = Client('apikey')
        lat = 52.446023244274045
        lon = 4.819207798979252
        fields = [FIELD_TEMP, FIELD_DEW_POINT, FIELD_HUMIDITY]
        start_time = 'now'
        end_time = 'tomorrow'

        self.assertRaises(
            ValueError, client.hourly, lat, lon, fields, start_time, end_time
        )

    @mock.patch('climacell.api.requests.get', side_effect=mock_requests_get)
    def test_hourly_valid_end_time(self, mock_get):
        client = Client('apikey')
        lat = 52.446023244274045
        lon = 4.819207798979252
        fields = [FIELD_TEMP, FIELD_DEW_POINT, FIELD_HUMIDITY]
        start_time = 'now'
        end_time = '2021-01-14T21:00:00.000Z'

        response = client.hourly(lat, lon, fields, start_time, end_time)
        self.assertFalse(response.has_error)

        expected_params = {
            'lat': 52.446023244274045,
            'lon': 4.819207798979252,
            'start_time': 'now',
            'unit_system': 'si',
            'fields': join_fields([FIELD_TEMP, FIELD_DEW_POINT, FIELD_HUMIDITY]),
            'end_time': '2021-01-14T21:00:00.000Z',
        }

        mock_get.assert_called_with(
            'https://api.climacell.co/v3/weather/forecast/hourly',
            params=expected_params,
            headers={'apikey': 'apikey'}
        )

    @mock.patch('climacell.api.requests.get', side_effect=mock_requests_get)
    def test_nowcast(self, mock_get):
        client = Client('apikey')
        lat = 52.446023244274045
        lon = 4.819207798979252
        timestep = 30
        fields = [
            FIELD_TEMP,
            FIELD_DEW_POINT,
            FIELD_HUMIDITY,
            FIELD_WIND_SPEED,
            FIELD_WIND_GUST,
            FIELD_WIND_DIRECTION,
            FIELD_SUNRISE,
            FIELD_SUNSET,
        ]

        response = client.nowcast(lat=lat, lon=lon, fields=fields, timestep=timestep)
        measurements = response.get_measurements()

        expected_params = {
            'lat': 52.446023244274045,
            'lon': 4.819207798979252,
            'timestep': 30,
            'start_time': 'now',
            'unit_system': 'si',
            'fields': join_fields(fields),
        }

        mock_get.assert_called_with(
            'https://api.climacell.co/v3/weather/nowcast',
            params=expected_params,
            headers={'apikey': 'apikey'}
        )
        # 13 timesteps, 8 measurements per timestep
        self.assertEqual(13 * 8, len(measurements))

    @mock.patch('climacell.api.requests.get', side_effect=mock_requests_get)
    def test_nowcast_valid_end_time(self, mock_get):
        client = Client('apikey')
        lat = 52.446023244274045
        lon = 4.819207798979252
        timestep = 30
        fields = [FIELD_TEMP]
        start_time = 'now'
        end_time = '2021-01-14T21:00:00.000Z'

        response = client.nowcast(
            lat=lat, lon=lon, fields=fields, timestep=timestep,
            start_time=start_time, end_time=end_time
        )

        self.assertFalse(response.has_error)

        expected_params = {
            'lat': 52.446023244274045,
            'lon': 4.819207798979252,
            'timestep': 30,
            'start_time': 'now',
            'unit_system': 'si',
            'fields': join_fields(fields),
            'end_time': end_time
        }

        mock_get.assert_called_with(
            'https://api.climacell.co/v3/weather/nowcast',
            params=expected_params,
            headers={'apikey': 'apikey'}
        )

    def test_nowcast_invalid_start_time(self):
        client = Client('apikey')
        lat = 52.446023244274045
        lon = 4.819207798979252
        timestep = 30
        fields = [FIELD_TEMP]
        start_time = 'yesterday'

        self.assertRaises(
            ValueError, client.nowcast, lat, lon, fields, timestep, start_time
        )

    def test_nowcast_invalid_end_time(self):
        client = Client('apikey')
        lat = 52.446023244274045
        lon = 4.819207798979252
        timestep = 30
        fields = [FIELD_TEMP]
        start_time = 'now'
        end_time = 'tomorrow'

        self.assertRaises(
            ValueError, client.nowcast, lat, lon, fields,
            timestep, start_time, end_time
        )
