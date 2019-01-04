# Xavier Smart Home #
Xavier is an easily expandable smart home designed for use on a Raspberry Pi written in Python.
At its core, it uses [Snowboy Hotword Detection](https://snowboy.kitt.ai) to quickly detect spoken commands and provide custom responses.

It currently ships with the following commands:
* Turn on/off a lamp
* Blink an LED
* Play sounds:
  * [Why?](https://www.youtube.com/watch?v=Xo2YkemM4kg)
  * [That's Pretty Neat](https://www.youtube.com/watch?v=Hm3JodBR-vs)
* Broadcast the weather for either today or tomorrow, using [this API](https://www.weather.gov/documentation/services-web-api)
* Tell the time
* Tell the date
* Tell a dad joke using [this API](https://icanhazdadjoke.com)

Adding a new command only requires recording a model for Snowboy to listen for and tagging the new command with a decorator, making customization easy.
Each command modified by the decorator is added to the smart home's list of commands automatically. \
It also modifies the command to provide the following functionality:
* Turns on/off a "thinking" LED to signal the smart home is processing the command
* Logs the command and its output whenever it is called
* Has a 10% chance to play a custom sound instead of normally processing the command


# Installation #
Xavier runs on Python 3, which can be installed using: \
`sudo apt-get install python3`

Xavier depends on Snowboy to run, which can be downloaded [here](http://docs.kitt.ai/snowboy/#downloads).

Xavier also requires pip-able packages.
Pip can be installed using: \
`sudo apt-get install pip3` \
And each of the following packages can be installed using: \
`sudo pip install [package name]`
* GPIO
* gTTS
* pyaudio
* pygame
* requests

Xavier needs certain values in the `settings.json` file:

The `pin_mapping` value should be a dictionary mapping strings to integers: the "thinking" (signals Xavier is processing a command) and "lamp" (to control a lamp using a relay) functions to their pin numbers.

The `location_coords` (optional) value should be a dictionary mapping strings to strings: the x and y coordinates to use in weather-pulling.
If it is not defined, the value will default to the coordinates of Blacksburg, VA.

The `logfile` (optional) value should be a string holding the file name to log command calls to.
If it is not defined, Xavier will log to the console.
Note: all written logs are stored in the `logs` directory.

Lastly, Snowboy needs models to run correctly.
Each `Body` method tagged with the `HomeCommand` decorator in `core.py` needs a corresponding `.pmdl` file in the `models` directory.
Follow [these instructions](http://docs.kitt.ai/snowboy/#api-v1-train) to accomplish this.
I recommend the bash script, as the python script is written for Python 2.
Each model name should be the same as the method it is associated with.
For example, the `time` method needs a `time.pmdl` file in the `models` directory.


# Basic Use #
Once the environment is set up, run the following command to start listening to commands: \
`python main.py`

Running `core.py` in this manner provides a console to test commands.


# File Structure #
### Each directory serves a purpose:

`logs`: Holds generated log files.

`models`: Holds models used by Snowboy.

`sounds`: Holds sounds used for the soundboard.
All sounds should have a sampling rate of 24000Hz.

`tests`: Holds unit tests.
To run a test, copy it and the `tests/resources` folder to the root directory.

### Each file serves a purpose:

`brain.py`: Holds the `Brain` class responsible for generating all spoken text.
Such responses respond directly to Snowboy.

`command.py`: Holds the `HomeCommand` decorator that records methods as commands and provides various modifications to the commands.

`core.py`: Holds the `Body` class, a container class responsible for running the smart home.
It handles all interaction with the real world, including speaking, listening, controlling lights, and responding to commands.

`enums.py`: Holds enumerators representing different options for commands.

`logger.py`: Holds the `Logger` class responsible for logging information to either a file in the `logs` directory or to the console.

`main.py`: Reads from the settings file, initializes a `Body` using these settings, then tells the `Body` to start listening for commands.

`toolbox.py`: Contains various miscellaneous helper functions for string formatting.

`settings.json`: Defines which pins on the Pi correspond to which functions, location coordinates to use when making weather broadcasts, and the name of the log file, if any, to use. \
The `pin_mapping` value should be a dictionary mapping strings to integers: the "thinking" (signals Xavier is processing a command) and "lamp" (to control a lamp using a relay) functions to their pin numbers. \
The `location_coords` (optional) value should be a dictionary mapping strings to strings: the x and y coordinates to use in weather-pulling. \
The `logfile` (optional) value should be a string to log command calls to.


# Customization #
The `HomeCommand` decorator makes it easy to add commands. \
To add a new command:
1. Create any necessary methods that generate spoken text in the `Brain` class in `brain.py`
2. Create a method in the `Body` class in `core.py` that handles real-world interactions (i.e. speaking, changing pin outputs)
    * Note: the `call_say` and `play_sound` helper methods in the `Body` may prove useful; see other commands for examples
3. Add the `@HomeCommand` decorator to the method in the `Body` class using one or two arguments (which are also explained in the `HomeCommand` documentation):
    * `sensitivity (float)`: sensitivity in detection for the command
    * `sound (str)`: sound, if any, (without path or extension) to potentially play instead of executing the command
      * Again, see other commands for examples

In addition, should you want to customize the smart home further, each class and method is well-documented.


# Testing #
To run a test, copy it and the `tests/resources` folder to the root directory.
There are currently no unit tests on the `Body`, since such real-world interactions are difficult to fully test (i.e. if spoken text is generated correctly).
Instead, there are tests for the `Brain` to ensure the generated text is correct.
However, these tests are relatively weak, since most responses are entirely dependent on built-in functions or API calls and are therefore very simple.
There are more thorough tests for the `Logger` and `toolbox`.


# Future Plans #
This is my current to do list:
* Add a brain for complex command parsing, likely using [the `SpeechRecognition` library](https://pypi.org/project/SpeechRecognition)
* Add a grocery list manager:
  * Add to a grocery list
  * Reorder the list to be in order of appearance in a given grocery store
  * Export the list via email
* Add a closet manager:
  * Keep track of what you have in your closet (i.e. what clothes you have available)
  * Remember what you previously wore during the week, and use this information along with the weather of the day to pick out an outfit for you
  * Record how many times you have worn something and suggest when to wash it
  * Remember what is in the laundry
* Add support for an LED RGB strip
* Add code for my web GUI
  * In addition to parsing spoken text, I also host a web server using [NGINX](https://www.nginx.com) to handle commands when out of speaking range, but I feel it is not ready for the public yet
  * This would likely be in a separate repository

I have been keeping track of my plans in my own workboard (similar to [Jira](https://www.atlassian.com/software/jira)).
I may upload my board if I add code for my web GUI (since I also use the board to keep track of my progress on the GUI, not just the Python code).
