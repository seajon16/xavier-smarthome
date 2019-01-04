import requests
from datetime import datetime
import calendar
from enums import WeatherDay
import toolbox


class Brain:
    """Core brain that builds all response strings for simple commands.

    Handles involved API calls.

    Args:
        location_coords (dict): Coordinates used in finding weather with keys
            x and y. Default location is Blacksburg, VA.
    """

    def __init__(self, location_coords=None):
        default_location_coords = {'x': '37.232191', 'y': '-80.423165'}
        self.location_coords = location_coords or default_location_coords

    # Helper #
    def __request_weather(self, day):
        """Returns the appropriate weather period depending on day.

        Uses https://api.weather.gov/.

        Args:
            day (WeatherDay enum): Which day (today or tomorrow) to return
                the period for.

        Returns:
            dict: The weather period for the given day.
        """
        weather_periods = requests.get(
            'https://api.weather.gov/points/{x},{y}/forecast'
            .format(**self.location_coords)
        ).json()['properties']['periods']
        # If I need today, then I just want the first period
        index = 0
        # If I need tomorrow, find tomorrow's period
        if day == WeatherDay.TOMORROW:
            for i in range(4):
                # If day is in the name, then I found tomorrow's first period
                if 'day' in weather_periods[i]['name']:
                    index = i
                    break
        return weather_periods[index]

    # Response Builders #
    # Note: These methods return strings to be said by a body
    def get_full_broadcast(self, day):
        """Return a full forecast for a given day as a string.

        Inspired by Dave McKee.

        Args:
            day (WeatherDay enum): Which day (today or tomorrow) to report.

        Returns:
            str: The full weather forecast like it was given by Dave McKee.
        """
        # Get the raw weather object (period) for the given day
        weather_obj = self.__request_weather(day)
        to_say = weather_obj['name'] + ', '

        # Handles different temperatures
        temperature = weather_obj['temperature']
        if temperature > 80:
            to_say += "it's rather steamy"
        elif temperature > 70:
            to_say += "it's warm"
        elif temperature > 55:
            to_say += "it's comfy"
        elif temperature > 35:
            to_say += "it's cool"
        elif temperature > 20:
            to_say += "it's pretty cold outside"
        else:
            to_say += "it's pretty darn cold"
        to_say += ' with a temperature of {}!'.format(temperature)

        # Customizes depending on the sky's appearance
        forecast = weather_obj['shortForecast']
        if 'Clear' in forecast:
            to_say += " It's a nice day, too!"
        elif 'Cloudy' in forecast:
            to_say += " It's a lame, cloudy day, too!"

        # Tags on if it's windy
        # The windSpeed value can be a range, so this uses the upper limit
        if int(weather_obj['windSpeed'].rstrip(' mph').split(" to ")[-1]) >= 20:
            to_say += " AND it's windy!"

        # Tags on an additional comment if it's cold
        if temperature <= 35:
            to_say += ' Be sure to dress for the weather!'

        return to_say

    def get_brief_broadcast(self, day):
        """Return a brief forecast for a given day as a string.

        Useful for determining rain chances.

        Args:
            day (WeatherDay enum): Which day (today or tomorrow) to report.

        Returns:
            str: The brief forecast taken directly from the API.
        """
        # Get the raw weather object (period) for the given day
        weather_obj = self.__request_weather(day)
        return weather_obj['shortForecast']

    @staticmethod
    def get_time():
        """Returns a string representing the time."""
        now = datetime.now()
        return now.strftime("%I %M with %S seconds.")

    @staticmethod
    def get_date():
        """Returns a string representing the date."""
        now = datetime.now()
        # Find the weekday as a word
        weekday = calendar.day_name[now.weekday()]
        # Find the month as a word
        month = calendar.month_name[now.month]
        return '{}, {} {}.'.format(weekday, month, now.day)

    @staticmethod
    def get_joke():
        """Returns a dad joke as a string using https://icanhazdadjoke.com/."""
        url = 'https://icanhazdadjoke.com/'
        headers = {'Accept': 'text/plain'}
        response = requests.get(url, headers=headers)
        # Replace non-ascii characters, namely odd/malformed apostrophes
        result = toolbox.repair_response(response.text)
        # Replace CR, LF, and tab characters with spaces
        return result.replace('\r\n', ' ').replace('\n', ' ').replace('\t', ' ')
