import requests
from command import mark_command


class WeatherDay:
    """Enum to represent different options for weather pulling.

    Weather puller can pull either today's weather or tomorrow's.
    This Enum represents these options.
    """
    TODAY = 1
    TOMORROW = 2


class WeatherPuller:
    """Uses weather.gov to report the weather.

    Args:
        xavier (Xavier): Xavier object to use to speak.
        location_coords (dict, optional): Coordinates used in finding weather with keys
            x and y. Default location is Blacksburg, VA, defined via the static
            field default_location_coords.
    """

    default_location_coords = {'x': '37.232191', 'y': '-80.423165'}

    def __init__(self, xavier, location_coords=None):
        self.xavier = xavier
        self.location_coords = location_coords or self.default_location_coords

    # Helper #
    def __request_weather(self, day):
        """Returns the appropriate weather period depending on day.

        Uses https://api.weather.gov/.

        Args:
            day (WeatherDay enum): Which day (today or tomorrow) to return
                the period for.

        Returns:
            dict: The weather period for the given day.

        Raises:
            requests.exceptions.ConnectionError: If a connection to the API
                could not be made. This exception should not cause Xavier to
                shut down.
        """
        weather_periods = requests.get(
            'https://api.weather.gov/points/{x},{y}/forecast'.format(
                **self.location_coords
            )
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
    # Note: These methods return strings to be said by an Xavier object
    def __get_full_broadcast(self, day):
        """Return a full forecast for a given day as a string.

        Inspired by Dave McKee. API is subject to change and may cause
        unexpected errors.

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
        to_say += f' with a temperature of {temperature}!'

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

    def __get_brief_broadcast(self, day):
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

    @mark_command(0.5, requests.exceptions.ConnectionError, sound='thicc')
    def weather_today_full(self):
        """Gives today's broadcast.

        Returns a string holding what was said.
        """
        to_say = self.__get_full_broadcast(WeatherDay.TODAY)
        self.xavier.say(to_say)
        return to_say

    @mark_command(0.5, requests.exceptions.ConnectionError, sound='thicc')
    def weather_tomorrow_full(self):
        """Gives tomorrow's broadcast.

        Returns a string holding what was said.
        """
        to_say = self.__get_full_broadcast(WeatherDay.TOMORROW)
        self.xavier.say(to_say)
        return to_say

    @mark_command(0.5, requests.exceptions.ConnectionError, sound='thicc')
    def weather_today_brief(self):
        """Gives a brief broadcast for today.

        Returns a string holding what was said.
        """
        to_say = self.__get_brief_broadcast(WeatherDay.TODAY)
        self.xavier.say(to_say)
        return to_say

    @mark_command(0.5, requests.exceptions.ConnectionError, sound='thicc')
    def weather_tomorrow_brief(self):
        """Gives a brief broadcast for tomorrow.

        Returns a string holding what was said.
        """
        to_say = self.__get_brief_broadcast(WeatherDay.TOMORROW)
        self.xavier.say(to_say)
        return to_say
