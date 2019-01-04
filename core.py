# What the Body needs to directly interact with the world
from RPi import GPIO
from pygame import mixer
from pygame.mixer import music
from gtts import gTTS

# What the Body needs to figure out how to respond to commands
from time import sleep
from brain import Brain
from logger import Logger
from command import HomeCommand
from enums import WeatherDay

# What the Body needs to start listening
import snowboydecoder
import signal


class Body:
    """Main class that controls Xavier.

    Handles all interactions with the real world. Uses its arguments to
    understand which pins it will use, create a Brain to handle requests,
    and create a Logger to record commands. When it is initialized, it will not
    listen or respond to commands until its start method is called. Once its
    start method is invoked, control will stay within the object.

    Args:
        pin_mapping (dict): Mapping of which pins relate to which functions.
        location_coords (dict): Coordinates used in finding weather with keys
            x and y. Default location is Blacksburg, VA.
        logfile (str): Name of the file to log to WITH extension. Creates it if
            it doesn't exist. Appends to it if it already exists. If no file is
            specified, the logger will log to the console.
    """

    def __init__(self, pin_mapping, location_coords=None, logfile=None):
        # Remember what pin numbers relate to which operations
        self.thinking = pin_mapping['thinking']
        self.lamp = pin_mapping['lamp']

        # Create the additional objects I need
        self.brain = Brain(location_coords)
        self.logger = Logger(logfile)

        # Set up the sound player (mixer) only if it hasn't been initialized yet
        if not mixer.get_init():
            # Set the frequency to 24000Hz, since that's what gTTS uses
            mixer.pre_init(24000)
            mixer.init()
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        # Set up the pins I need to use
        used_pins = list(pin_mapping.values())
        GPIO.setup(used_pins, GPIO.OUT)

        # Will be used later to determine if my event loop should end
        # Starts as False, since I am just initializing; I am not listening yet
        self.is_running = False

    def __del__(self):
        """Close my logger and the mixer."""
        del self.logger
        mixer.quit()

    @staticmethod
    def get_commands():
        """Returns a dict mapping all commands to their sensitivities."""
        # Ask the decorator for what it recorded
        return HomeCommand.get_commands()

    def start(self):
        """Begin listening to spoken commands.

        Note: Control will stay within this object.
        """
        # Grab my callback methods, find the appropriate models, and set up the
        # 	sensitivities for each
        callbacks = []
        models = []
        sensitivities = []
        command_mapping = Body.get_commands()
        for command, sensitivity in command_mapping.items():
            callbacks.append(lambda: command(self))
            models.append('models/{}.pmdl'.format(command.__name__))
            sensitivities.append(sensitivity)

        # If I see an interrupt, then I need to stop running
        signal.signal(signal.SIGINT, self.stop)

        detectors = snowboydecoder.HotwordDetector(
            models, sensitivity=sensitivities
        )

        # Designate me as a running instance
        self.is_running = True

        detectors.start(detected_callback=callbacks,
                        # If I should no longer be running, then interrupt me
                        interrupt_check=lambda: not self.is_running,
                        sleep_time=.03)

        detectors.terminate()

    def stop(self):
        """Stop listening to spoken commands."""
        # By setting my is_running field to False, I signal to snowboy's event
        #   loop that it must terminate
        self.is_running = False

    # Helpers #
    def set_thinking(self, value):
        """Sets the thinking pin to the given value.

        Used by the HomeCommand decorator.

        Args:
            value (bool): To set the pin to.
        """
        GPIO.output(self.thinking, value)

    @staticmethod
    def play_sound(desire):
        """Given the name of an mp3 (no extension/dir), plays the sound.

        Args:
            desire (str): MP3 to play with no extension/dir.

        Returns:
            str: The action I just performed.
        """
        # Ensure the mixer has been initialized
        if not mixer.get_init():
            return 'Mixer has not been initialized yet; create a new instance.'
        music.load('sounds/{}.mp3'.format(desire))
        music.play()
        while music.get_busy():
            continue
        return "Played {}.".format(desire)

    def __say(self, desire):
        """Given a string of text, speak it.

        Args:
            desire (str): Text to speak.
        """
        tts = gTTS(desire, 'en-uk')
        tts.save('sounds/temp_voice.mp3')
        self.play_sound('temp_voice')
        # Load a different, constant sound to prevent IO errors
        music.load('sounds/akuwhat.mp3')

    def call_say(self, func, *args, **kwargs):
        """Call the method, then say and return its output.

        Args:
            func (callable): Method to execute.
            args (list): Args to call the method with.
            kwargs (dict): Keyword args to call the method with.

        Returns:
            str: The call's output.
        """
        to_say = func(*args, **kwargs)
        self.__say(to_say)
        return to_say

    # Error Reporters #
    def report_warn(self, command_name, exception_name):
        """Proclaim I just encountered a recoverable exception.

        Used by the HomeCommand decorator.

        Args:
            command_name (str): Name of the command that threw the exception.
            exception_name (str): Name of the thrown exception.
                Should have any necessary spaces between words
                (ie ConnectionError is instead Connection Error).
        """
        to_say = 'Command {} just threw an exception of type {}.'.format(
            command_name, exception_name
        )
        self.__say(to_say)

    def report_error(self, command_name, exception_name):
        """Proclaim I just encountered an unrecoverable exception.

        Used by the HomeCommand decorator.

        Args:
            command_name (str): Name of the command that threw the exception.
            exception_name (str): Name of the thrown exception.
                Should have any necessary spaces between words
                (ie ConnectionError is instead Connection Error).
        """
        self.report_warn(command_name, exception_name)
        self.__say('I cannot recover from this exception.')

    # Command #
    ## IOT ##
    @HomeCommand(0.5, 'akuwhat')
    def toggle_lamp(self):
        """Toggles lamp pin.

        Returns a string depicting the action.
        """
        GPIO.output(self.lamp, not GPIO.input(self.lamp))
        return "Toggled lamp."

    @HomeCommand(0.5, 'akuwhat')
    def blink_led(self):
        """Blink my thinking LED.

        Returns a string depicting the action.
        """
        # Decorator takes care of this
        sleep(2)
        return 'Blinked thinking LED.'

    ## Soundboard ##
    @HomeCommand(0.5)
    def neat(self):
        """That's pretty neat.

        Returns a string depicting the action.
        """
        return self.play_sound('neat')

    @HomeCommand(0.5)
    def why(self):
        """Why?

        Returns a string depicting the action.
        """
        return self.play_sound('why')

    ## Misc ##
    @HomeCommand(0.5, 'thicc')
    def weather_today_full(self):
        """Gives today's broadcast.

        Returns a string holding what was said.
        """
        return self.call_say(
            self.brain.get_full_broadcast, WeatherDay.TODAY
        )

    @HomeCommand(0.5, 'thicc')
    def weather_tomorrow_full(self):
        """Gives tomorrow's broadcast.

        Returns a string holding what was said.
        """
        return self.call_say(
            self.brain.get_full_broadcast, WeatherDay.TOMORROW
        )

    @HomeCommand(0.5, 'thicc')
    def weather_today_brief(self):
        """Gives a brief broadcast for today.

        Returns a string holding what was said.
        """
        return self.call_say(
            self.brain.get_brief_broadcast, WeatherDay.TODAY
        )

    @HomeCommand(0.5, 'thicc')
    def weather_tomorrow_brief(self):
        """Gives a brief broadcast for tomorrow.

        Returns a string holding what was said.
        """
        return self.call_say(
            self.brain.get_brief_broadcast, WeatherDay.TOMORROW
        )

    @HomeCommand(0.5, 'thicc')
    def time(self):
        """Gives the time.

        Returns a string holding what was said.
        """
        return self.call_say(self.brain.get_time)

    @HomeCommand(0.5, 'why')
    def date(self):
        """Gives the date.

        Returns a string holding what was said.
        """
        return self.call_say(self.brain.get_date)

    @HomeCommand(0.5)
    def joke(self):
        """Tells a dad joke.

        Returns a string holding what was said.
        """
        return self.call_say(self.brain.get_joke)


# Console for testing
if __name__ == "__main__":
    mapping = {'thinking': 10, 'lamp': 11}
    body = Body(mapping, logfile='coretesting.log')
    commands = {func.__name__: func for func in Body.get_commands()}

    print('Console for testing purposes')
    while True:
        cmd = input('Enter/list/exit: ')
        if cmd in commands:
            commands[cmd](body)
        elif cmd == 'list':
            for opt in commands:
                print(opt)
        elif cmd == 'exit':
            break
        else:
            print('Invalid command')

    del body
