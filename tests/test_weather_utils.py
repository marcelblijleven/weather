from unittest import TestCase

from weather_utils import (
    calculate_okta, ms_to_knots, mph_to_knots,
    mph_to_ms, ms_to_mph, calculate_fog_probability, calculate_fog_temperature,
)


class TestWeatherUtils(TestCase):
    def test_calculate_okta(self):
        self.assertEqual(0, calculate_okta(0.00))
        self.assertEqual(1, calculate_okta(18.74))
        self.assertEqual(2, calculate_okta(18.75))
        self.assertEqual(2, calculate_okta(31.24))
        self.assertEqual(3, calculate_okta(31.25))
        self.assertEqual(3, calculate_okta(43.74))
        self.assertEqual(4, calculate_okta(43.75))
        self.assertEqual(4, calculate_okta(56.24))
        self.assertEqual(5, calculate_okta(56.25))
        self.assertEqual(5, calculate_okta(68.74))
        self.assertEqual(6, calculate_okta(68.75))
        self.assertEqual(6, calculate_okta(81.24))
        self.assertEqual(7, calculate_okta(81.25))
        self.assertEqual(7, calculate_okta(99.99))
        self.assertEqual(8, calculate_okta(100))

        self.assertRaises(ValueError, calculate_okta, -0.01)
        self.assertRaises(ValueError, calculate_okta, 100.01)

    def test_ms_to_knots(self):
        self.assertEqual(1.94384449, ms_to_knots(1))
        self.assertEqual(3.88768898, ms_to_knots(2))

    def test_mph_to_knots(self):
        self.assertEqual(0.868976242, mph_to_knots(1))
        self.assertEqual(1.737952484, mph_to_knots(2))

    def test_mph_to_ms(self):
        self.assertEqual(0.44704, mph_to_ms(1))
        self.assertEqual(0.89408, mph_to_ms(2))

    def test_ms_to_mph(self):
        self.assertEqual(2.2369362920544025, ms_to_mph(1))
        self.assertEqual(4.473872584108805, ms_to_mph(2))

    def test_calculate_fog_temperature(self):
        temperature = 15
        dew_point = 10
        okta = 0
        wind_speed = 0
        self.assertEqual(8.549999999999999, calculate_fog_temperature(
            temperature, dew_point, okta, wind_speed
        ), msg="Test case 1 failed")

        temperature = 10
        dew_point = 10
        okta = 3
        wind_speed = 14
        self.assertEqual(8.329999999999998, calculate_fog_temperature(
            temperature, dew_point, okta, wind_speed
        ), msg="Test case 2 failed")

        temperature = 10
        dew_point = 10
        okta = 5
        wind_speed = 14
        self.assertEqual(8.829999999999998, calculate_fog_temperature(
            temperature, dew_point, okta, wind_speed
        ), msg="Test case 3 failed")

        temperature = 10
        dew_point = 10
        okta = 6
        wind_speed = 1
        self.assertEqual(9.829999999999998, calculate_fog_temperature(
            temperature, dew_point, okta, wind_speed
        ), msg="Test case 4 failed")

        temperature = 10
        dew_point = 10
        okta = 6
        wind_speed = 26
        self.assertEqual(8.829999999999998, calculate_fog_temperature(
            temperature, dew_point, okta, wind_speed
        ), msg="Test case 5 failed")

        temperature = 10
        dew_point = 10
        okta = 1
        wind_speed = 24
        self.assertEqual(6.829999999999998, calculate_fog_temperature(
            temperature, dew_point, okta, wind_speed
        ), msg="Test case 6 failed")

        temperature = 10
        dew_point = 10
        okta = 5
        wind_speed = 24
        self.assertEqual(8.829999999999998, calculate_fog_temperature(
            temperature, dew_point, okta, wind_speed
        ), msg="Test case 7 failed")

        temperature = 10
        dew_point = 15
        okta = 7
        wind_speed = 24
        self.assertEqual(13.049999999999999, calculate_fog_temperature(
            temperature, dew_point, okta, wind_speed
        ), msg="Test case 8 failed")

        temperature = 10
        dew_point = 15
        okta = 3
        wind_speed = 1
        self.assertEqual(12.549999999999999, calculate_fog_temperature(
            temperature, dew_point, okta, wind_speed
        ), msg="Test case 9 failed")

        temperature = 10
        dew_point = 15
        okta = 5
        wind_speed = 11
        self.assertEqual(13.549999999999999, calculate_fog_temperature(
            temperature, dew_point, okta, wind_speed
        ), msg="Test case 10 failed")

        temperature = 10
        dew_point = 15
        okta = -1
        wind_speed = 11
        self.assertEqual(13.049999999999999, calculate_fog_temperature(
            temperature, dew_point, okta, wind_speed
        ), msg="Test case 11 failed")

        temperature = 10
        dew_point = 15
        okta = 5
        wind_speed = -1
        self.assertRaises(
            ValueError, calculate_fog_temperature, temperature,
            dew_point, okta, wind_speed)

    def test_calculate_fog_probability(self):
        min_temperature = 0
        fog_temperature = 0
        want = 3
        self.assertEqual(
            want, calculate_fog_probability(min_temperature, fog_temperature),
            msg=f'Test case 1 failed'
        )

        min_temperature = 10
        fog_temperature = 0
        want = 1
        self.assertEqual(
            want, calculate_fog_probability(min_temperature, fog_temperature),
            msg=f'Test case 2 failed'
        )

        min_temperature = 0
        fog_temperature = 10
        want = 5
        self.assertEqual(
            want, calculate_fog_probability(min_temperature, fog_temperature),
            msg=f'Test case 3 failed'
        )

        min_temperature = 10
        fog_temperature = 9.5
        want = 3
        self.assertEqual(
            want, calculate_fog_probability(min_temperature, fog_temperature),
            msg=f'Test case 4 failed'
        )

        min_temperature = 10
        fog_temperature = 10.99
        want = 4
        self.assertEqual(
            want, calculate_fog_probability(min_temperature, fog_temperature),
            msg=f'Test case 5 failed'
        )

        min_temperature = 11.6
        fog_temperature = 11
        want = 2
        self.assertEqual(
            want, calculate_fog_probability(min_temperature, fog_temperature),
            msg=f'Test case 6 failed'
        )

        min_temperature = 12.6
        fog_temperature = 11
        want = 1
        self.assertEqual(
            want, calculate_fog_probability(min_temperature, fog_temperature),
            msg=f'Test case 7 failed'
        )
