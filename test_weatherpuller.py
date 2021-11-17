import unittest
from unittest.mock import Mock, patch

from requests import Response
from weatherpuller import WeatherPuller, WeatherDay
from core import Xavier


class TestWeatherPuller(unittest.TestCase):

    dummy_api_response = {
        'properties': {
            'periods' : [
                {
                    'name': 'Today',
                    'temperature': 50,
                    'shortForecast': 'Clear 50 degrees',
                    'windSpeed': '24 mph'
                },
                {
                    'name': 'Tonight',
                    'temperature': 35,
                    'shortForecast': 'Cloudy 35 degrees',
                    'windSpeed': '10 mph'
                },
                {
                    'name': 'Tomorrow',
                    'temperature': 60,
                    'shortForecast': 'Rainy 60 degrees',
                    'windSpeed': '30 mph'
                },
                {
                    'name': 'Wednesday',
                    'temperature': 50,
                    'shortForecast': 'Clear 50 degrees',
                    'windSpeed': '5 mph'
                }
            ]
        }
    }

    def setUp(self):
        self.mock_response = Mock(Response)
        self.mock_response.json = Mock(return_value=TestWeatherPuller.dummy_api_response)
        self.mock_xavier = Mock(Xavier)
        self.puller = WeatherPuller(self.mock_xavier)

    @patch('requests.get')
    def test_weather_today_full(self, mock_get):
        mock_get.return_value = self.mock_response
        self.puller.weather_today_full.decorate(self.mock_xavier)
        self.puller.weather_today_full(self.puller)

        mock_get.assert_called_once_with(
            'https://api.weather.gov/points/37.232191,-80.423165/forecast'
        )
        self.mock_xavier.say.assert_called_once_with(
            "Today, it's cool with a temperature of 50! It's a nice day, too! "
            "AND it's windy!"
        )


if __name__ == "__main__":
    unittest.main()
