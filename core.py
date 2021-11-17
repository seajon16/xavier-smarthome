# TODO things you should do after this push:
# TODO overall new idea: require plugins and commands inherit from a base plugin/command class
#   this might fix the stupidity involved where you have the single log_call wrapped with two lambdas
# TODO it really isn't clear how to add a required pin to the pin_mappings; change how Body works
#   maybe have another arg in Xavier that defines a required structure that the Body can then consume
#   honestly, you should just make pin_mappings not mandatory
# TODO some things might break if someone makes a folder for their plugins
#   basically figure out how to do absolute paths
#   this issue is skippable; might not be a problem; test it first
#   might want to add a global path in main using os then using join
#   or write a func in main that does this for you
#   https://stackoverflow.com/questions/25389095/python-get-path-of-root-project-structure
#   https://codereview.stackexchange.com/questions/20428/accessing-the-contents-of-a-projects-root-directory-in-python
#   if you do, you should use os.path.isfile instead of Path.is_file
# TODO what about modules?

# TODO things you need to do now
# DONE check the google docs for how to document static fields (required_pins, default_location_coords)
#   it doesn't, just makes them uppercase
# DONE get rid of any mentioning of the Pin enum
# DONE also might need to change wording wherever WeatherDay is used since you moved it
# TODO make sure this entire thing is bullet proof, write tests for exceptions
# TODO lol update tests, and i really want you to figure out how to mock stuff
# TODO search for TODO and FIXME

# TODO check tense
# TODO check for calling xavier core instead of xavier
# TODO check google's guidelines to see how they format mentioning args in docs, like command:21
# TODO document optional arguments as such (Command's constructor has example)
# TODO you seriously can't fix the stupid pygame thing?
#   it's because pygame has file loaded but gtts wants to edit it
# TODO read this https://docs.python-guide.org/writing/structure/
# TODO check prints for if you can use comma separation instead of .format()
# TODO and also check for using f'{lol}', only when you aren't subreferencing
#   lol c# made you want to do this all the time because it's so much better
# TODO check strings within parenthesis for if you have the parenthesis on new line
# TODO check what tenses you're using (ie first, third, past, present)
# TODO should ie be i.e.? yes
# TODO list(), dict() vs [], {}
# TODO update readme
# TODO ensure class names are always capitalized in documentation
# TODO replace \n +\n with \n\n (ignore .log files)

# Used to figure out how to respond to commands
import json
from body import Body
from util.logger import Logger
from command import Command, HeadedCommand, HeadlessCommand

# Used to import plugins
import inspect
from functools import wraps
from random import randint

# Used to report errors
from traceback import format_exc
from util import toolbox
from gtts.tts import gTTSError

# Used to listen for commands
# import snowboydecoder  TODO AHHH
from unittest.mock import Mock
snowboydecoder = Mock()
import signal


class Xavier:
    """Main class that controls Xavier.

    Uses its arguments to understand which pins it will use, create a Body to
    handle real-world interaction, and create a Logger to record commands. When
    it is initialized, it will not listen or respond to commands until its start
    method is called. Once its start method is invoked, control will stay
    within the object.

    Args:
        pin_mapping (dict, optional): Mapping of which pins relate to which
            functions. Will be ignored if a settingsfile is defined. If a
            settingsfile is not defined, this argument must be defined with a
            valid pin mapping.
        logfile (str, optional): Name of the file to log to WITH extension.
            Creates it if it doesn't exist. Appends to it if it already exists.
            If no file is specified, the logger will log to the console.
        settingsfile (str, optional): Name of the file to read settings from
            WITH extension. If no file is specified, uses the other arguments
            instead.

    Raises:
        FileNotFoundError: If a settingsfile was defined but was not found.
        KeyError: If a settingsfile was defined but did not have a pin_mapping
            key.
        NameError: If neither settingsfile or pin_mapping were defined.
        TypeError: If at least one pin_mapping value was not an integer.
    """

    def __init__(self, pin_mapping=None, logfile=None, settingsfile=None):
        # If a settingsfile was defined, read from it
        if settingsfile:
            with open(settingsfile) as f:
                settings = json.load(f)
            # Use get since it can be undefined
            logfile = settings.get('logfile')
            pin_mapping = settings.get('pin_mapping')
            # However, pin_mapping cannot be undefined
            if not pin_mapping:
                raise KeyError('You must at least define pin_mapping')
        # Otherwise, make sure they at least defined pin_mapping
        else:
            if not pin_mapping:
                raise NameError(
                    'You must at least define pin_mapping if you do not '
                    'provide a settings file'
                )

        # Set up helper classes
        # May throw a TypeError if pin_mapping is invalid
        self.body = Body(pin_mapping)
        self.logger = Logger(logfile)
        # Holds commands added via add_plugin method
        self.plugins = dict()
        # Holds commands added via command decorator
        self.direct_commands = list()
        # Holds names of commands to prevent adding duplicate commands
        self.command_names = set()
        # Will be used later to determine if my event loop should end
        # Starts as False, since I am just initializing; I am not listening yet
        self.is_running = False

    def __del__(self):
        """Stop listening and close my Body and Logger."""
        self.stop()
        # TODO lol might need a signal from detectors to tell me this is safe
        del self.body
        del self.logger

    # Snowboy/Listening #
    def start(self, run_in_console=False):
        """Begin listening to spoken/typed commands.

        Note: Control will stay within this object.

        Params:
            run_in_console (bool, optional): Whether or not to give a prompt for
                the user to type in commands instead of listening to vocal ones.
                Defaults to false.
        """
        # If I was told to only take commands from the console
        if run_in_console:
            mapping = self.__assemble_command_mapping()

            print('Opening console...')
            # Designate me as a running instance
            self.is_running = True
            while True:
                cmd = input('Enter/list/exit: ')
                cmd_ptr = mapping.get(cmd)
                if cmd_ptr:
                    cmd_ptr()
                elif cmd == 'list':
                    for opt in mapping:
                        print(opt)
                elif cmd == 'exit':
                    break
                else:
                    print('Invalid command')

            self.is_running = False

        # If I was told to have snowboy take commands
        else:
            callbacks, models, sensitivities = self.__assemble_snowboy_params()    
            # If I see an interrupt, then I need to stop running
            signal.signal(signal.SIGINT, self.stop)
            detectors = snowboydecoder.HotwordDetector(
                models, sensitivity=sensitivities
            )

            print('Beginning to listen...')
            # Designate me as a running instance
            self.is_running = True
            detectors.start(
                detected_callback=callbacks,
                # If I should no longer be running, then interrupt me
                interrupt_check=self.is_stopped,  # FIXME this might not work
                sleep_time=.03
            )

            detectors.terminate()

    def __assemble_command_mapping(self):
        """Helper to create a mapping of every Command name to its callback.

        These callbacks are wrapped with any necessary plugin objects.
        """
        mapping = dict()
        # For each plugin (holding HeadedCommands), add its commands to my dict
        for plugin, commands in self.plugins.items():
            for command in commands:
                mapping[command.name] = (
                    # Wrap the call to send information to the logger
                    lambda command=command: self.__log_call(
                        command,
                        # Call the command by passing its plugin object
                        lambda command=command, plugin=plugin: command(plugin)
                    )
                )

        # For each directly added command, add it to my dict
        for command in self.direct_commands:
            mapping[command.name] = (
                # Wrap the call to send information to the logger
                lambda command=command: self.__log_call(
                    command,
                    # Call just the command, since it doesn't use a plugin
                    command
                )
            )

        return mapping

    def __assemble_snowboy_params(self):
        """Build the callbacks, models, and sensitivities for snowboy."""
        callbacks = list()
        models = list()
        sensitivities = list()
        # For each plugin (holding HeadedCommands), add its commands to my lists
        for plugin, commands in self.plugins.items():
            for command in commands:
                callbacks.append(
                    # Wrap the call to send information to the logger
                    lambda command=command: self.__log_call(
                        command,
                        # Call the command by passing its plugin object
                        lambda command=command, plugin=plugin: command(plugin)
                    )
                )
                models.append('models/{}.pmdl'.format(command.name))
                sensitivities.append(command.sensitivity)

        # For each directly added command, add it to my lists
        for command in self.direct_commands:
            callbacks.append(
                # Wrap the call to send information to the logger
                lambda command=command: self.__log_call(
                    command,
                    # Call just the command, since it doesn't use a plugin
                    command
                )
            )
            models.append('models/{}.pmdl'.format(command.name))
            sensitivities.append(command.sensitivity)

        return callbacks, models, sensitivities

    def stop(self):
        """Stop listening to spoken commands."""
        # By setting my is_running field to False, I signal to snowboy's event
        #   loop that it must terminate
        self.is_running = False

    def is_stopped(self):
        """Returns if I've been told to shut down."""
        return not self.is_running

    def __log_call(self, command, callback):
        """Helper method to perform a call on the given command.

        Catches recoverable exceptions and logs the results.

        Args:
            command (Command): Command to run. Used for information gathering.
            callback (callable): Actual callable to run. Must be wrapped with
                the command's plugin object if it needs it.
        """
        try:
            result = callback()

        # Catch and report recoverable errors
        except command.exceptions as e:
            self.logger.log_warn(command.name, format_exc())
            # Proclaim the command failed and will kill me
            # Add necessary spaces in the exception name to say it properly
            formatted_exception_name = toolbox.split_caps(type(e).__name__)
            # Proclaim the command failed but will not kill me
            self.__report_warn(command.name, formatted_exception_name)

        # If I couldn't connect to GTTS, log the error before raising it
        except gTTSError:
            self.logger.log_error(command.name, format_exc())
            # I do not have to proclaim the command failed, as the Body will
            #   have done that already
            # TODO the body says "shutting down" though
            #   the body shouldn't care about/know that
            #   well, it does raise the exception, so in its eyes it's gonna die
            del self
            raise

        # For all unexpected errors, log the error before raising it
        except Exception as e:
            self.logger.log_error(command.name, format_exc())
            # Proclaim the command failed and will kill me
            # Add necessary spaces in the exception name to say it properly
            formatted_exception_name = toolbox.split_caps(type(e).__name__)
            self.__report_error(command.name, formatted_exception_name)
            # Lastly, delete me to close the Body and Logger before allowing
            #   the exception to kill the program
            del self
            raise

        # If the call succeeded, log its success
        else:
            self.logger.log_info(command.name, result)

    def decorate_command(self, command):
        """Decorates a given command, adding additional functionality.

        Returns a modified version of the command's callback. Adds a 10% chance
        to play the command's sound if it has one, and turns on/off my thinking
        LED.

        Args:
            command (Command): Command to modify.

        Returns:
            callable: The Command's modified callable.
        """
        if isinstance(command, HeadedCommand):
            if command.sound:
                @wraps(command.func)
                def wrapper(plugin):
                    self.body.set_pin('thinking', True)
                    if randint(0, 9):
                        result = command.func(plugin)
                    else:
                        self.body.play_sound(command.sound)
                        result = 'Played {}.'.format(command.sound)
                    self.body.set_pin('thinking', False)
                    return result
            else:
                @wraps(command.func)
                def wrapper(plugin):
                    self.body.set_pin('thinking', True)
                    result = command.func(plugin)
                    self.body.set_pin('thinking', False)
                    return result

        else:
            if command.sound:
                @wraps(command.func)
                def wrapper():
                    self.body.set_pin('thinking', True)
                    if randint(0, 9):
                        result = command.func()
                    else:
                        self.body.play_sound(command.sound)
                        result = 'Played {}.'.format(command.sound)
                    self.body.set_pin('thinking', False)
                    return result
            else:
                @wraps(command.func)
                def wrapper():
                    self.body.set_pin('thinking', True)
                    result = command.func()
                    self.body.set_pin('thinking', False)
                    return result

        return wrapper

    # Error Reporters #
    def __report_warn(self, command_name, exception_name):
        """Proclaim I just encountered a recoverable exception.

        Used by the __log_call method.

        Args:
            command_name (str): Name of the command that threw the exception.
            exception_name (str): Name of the thrown exception.
                Should have any necessary spaces between words
                (i.e. ConnectionError is instead Connection Error).
        """
        to_say = 'Command {} just threw an exception of type {}.'.format(
            command_name, exception_name
        )
        self.say(to_say)

    def __report_error(self, command_name, exception_name):
        """Proclaim I just encountered an unrecoverable exception.

        Used by the __log_call method.

        Args:
            command_name (str): Name of the command that threw the exception.
            exception_name (str): Name of the thrown exception.
                Should have any necessary spaces between words
                (i.e. ConnectionError is instead Connection Error).
        """
        to_say = 'Command {} just threw an exception of type {}.'.format(
            command_name, exception_name
        ) + ' I cannot recover from this exception.'
        self.say(to_say)

    # Main Interfaces #
    def say(self, text):
        """Given a string of text, speak it using my body.

        Args:
            text (str): Text to speak.
        """
        self.body.say(text)

    def toggle_pin(self, pin):
        """Toggle given pin using my body."""
        self.body.toggle_pin(pin)

    def play_sound(self, sound):
        """Play given sound using my body."""
        self.body.play_sound(sound)

    def add_plugin(self, plugin):
        """Add a plugin, loading its Commands.

        A Command is designated by the command decorator (command.mark_command).
        If I'm already listening (ie start() has already been called),
        restart me to begin listening to the new commands.

        Returns:
            bool: If the plugin was successfully added. False if no Command
                objects were found in the plugin, the pluggin was already added,
                or the plugin contained a Command that had the name of another,
                already added Command.
        """
        # Make sure the plugin wasn't already added
        if self.plugins.get(plugin):
            return False

        plugin_commands = list()
        new_direct_commands = list()

        members = inspect.getmembers(plugin)
        for _, member in members:
            # Remember every Command
            if isinstance(member, Command):
                # But make sure it isn't a duplicate
                if member.name in self.command_names:
                    return False
                # Decorate it
                member.decorate(self)
                # Add it to plugins if it needs its plugin reference
                if isinstance(member, HeadedCommand):
                    plugin_commands.append(member)
                # Otherwise, just add it as a direct command
                else:
                    new_direct_commands.append(member)

        # Complain if I didn't find a single command
        if not (plugin_commands or new_direct_commands):
            return False

        # Now that I've confirmed the plugin can entirely be added, add it
        # If I found at least one HeadedCommand, add them to my plugins
        if plugin_commands:
            self.plugins[plugin] = plugin_commands
            self.command_names.update(
                [command.name for command in plugin_commands]
            )
        # If I found at least one direct command, add them to my list
        if new_direct_commands:
            # TODO since you already have to iterate, should you just use append
            self.direct_commands += new_direct_commands
            self.command_names.update(
                [command.name for command in new_direct_commands]
            )

        return True

    def add_command(self, sensitivity, *exceptions, name=None, sound=None):
        """Register an individual command using the given arguments."""
        def decorator(func):
            # Transform it into a command with the necessary information
            command = HeadlessCommand(
                name or func.__name__,
                func,
                sensitivity,
                exceptions,
                sound
            )
            # Decorate it
            command.decorate(self)
            # Record it
            self.direct_commands.append(command)
            return command
        return decorator
