# Used to setup Xavier and the Weather Plugin
import json
from core import Xavier
from weatherpuller import WeatherPuller

# Used in example commands
from time import sleep
from datetime import datetime
import calendar
import requests
from util import toolbox


# Open universal settings file
with open('settings.json') as f:
    try:
        settings = json.load(f)  # TODO revert changes you made for testing
    except json.decoder.JSONDecodeError:
        raise json.decoder.JSONDecodeError(
            'Failed to load settings.json file. Make sure you assign values to '
            'the pin mappings.'
        )

# Use get for these two since they can be undefined
location_coords = settings.get('location_coords')
logfile = settings.get('logfile')
# Use indexing for pin mapping since we need it (may throw a KeyError)
try:
    pin_mapping = settings['pin_mapping']
except KeyError:
    raise KeyError('You must at least define pin_mapping')

xavier = Xavier(pin_mapping, logfile)
# Create an instance of the weather plugin
weather_plugin = WeatherPuller(xavier, location_coords)
# Add it to Xavier
xavier.add_plugin(weather_plugin)


# Add example commands to Xavier
## IOT ##
@xavier.add_command(0.5, sound='akuwhat')
def toggle_lamp():
    """Toggles lamp pin.

    Returns a string depicting the action.
    """
    xavier.toggle_pin('lamp')
    return 'Toggled lamp.'


@xavier.add_command(0.5, sound='akuwhat')
def blink_led():
    """Blink my thinking LED.

    Returns a string depicting the action.
    """
    # Decorator takes care of this
    sleep(2)
    return 'Blinked thinking LED.'


@xavier.add_command(0.5)
def neat():
    """That's pretty neat.

    Returns a string depicting the action.
    """
    xavier.play_sound('neat')
    return 'Played neat.'


@xavier.add_command(0.5)
def why():
    """Why?

    Returns a string depicting the action.
    """
    xavier.play_sound('why')
    return 'Played why.'


@xavier.add_command(0.5, sound='thicc')
def time():
    """Gives the time.

    Returns a string holding what was said.
    """
    now = datetime.now()
    to_say = now.strftime("%I %M with %S seconds.")
    xavier.say(to_say)
    return to_say


@xavier.add_command(0.5, sound='why')
def date():
    """Gives the date.

    Returns a string holding what was said.
    """
    now = datetime.now()
    # Find the weekday as a word
    weekday = calendar.day_name[now.weekday()]
    # Find the month as a word
    month = calendar.month_name[now.month]
    to_say = f'{weekday}, {month} {now.day}.'
    xavier.say(to_say)
    return to_say


@xavier.add_command(0.5)
def joke():
    """Tells a dad joke using https://icanhazdadjoke.com/.

    Returns a string holding what was said.
    """
    url = 'https://icanhazdadjoke.com/'
    headers = {'Accept': 'text/plain'}
    response = requests.get(url, headers=headers)
    # Replace non-ascii characters like odd/malformed apostrophes, tabs, and LF
    to_say = toolbox.repair_response(response.text)
    xavier.say(to_say)
    return to_say


# Control will be given to Xavier until it sees an interrupt signal
xavier.start(True)  # TODO you prolly don't want this arg
# Delete Xavier, closing the logger, mixer, and GPIO interface
del xavier
