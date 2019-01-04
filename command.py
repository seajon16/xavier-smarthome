from functools import wraps
from pathlib import Path
from random import randint
import requests.exceptions
from traceback import format_exc
import toolbox


class HomeCommand:
    """Decorator that organizes snowboy commands.

    Used by the Body to do the following:
        * Turns on/off thinking LED of the given body.
        * Records the method and its sensitivity to be used at runtime.
        * Logs the method call.
        * If given a sound, allows a 10% chance to play the sound instead of
            running the command.
    Can only be used within a body object.

    Args:
        sensitivity (float): Sensitivity in detection for this command.
        sound (str): Sound, if any, (without path or extension) to potentially
            play instead of executing this command.
    """

    # Stores commands mapped to their sensitivities
    commands = dict()

    def __init__(self, sensitivity, sound=None):
        self.sensitivity = sensitivity
        self.sound = sound

    def __call__(self, func):
        """The real decorator.

        Performs the modifications stated in the class doc.

        Args:
            func (callable): Command to modify and record.

        Returns:
            callable: The modified and recorded callable.
        """
        # If I was given a potential sound
        if self.sound:
            # Ensure I'll be able to load the sound first
            sound_path = Path('sounds/{}.mp3'.format(self.sound))
            if not sound_path.is_file():
                raise FileNotFoundError(
                    'Error initializing {}: {} does not exist'.format(
                        func.__name__, sound_path
                    )
                )

            @wraps(func)
            def wrapper(body, *args, **kwargs):
                body.set_thinking(True)
                if randint(0, 9):
                    self.__safe_call(func, body, *args, **kwargs)
                else:
                    result = body.play_sound(self.sound)
                    body.logger.log_info(func.__name__, result)
                body.set_thinking(False)

        # Otherwise, just add the LED effect
        else:
            @wraps(func)
            def wrapper(body, *args, **kwargs):
                body.set_thinking(True)
                self.__safe_call(func, body, *args, **kwargs)
                body.set_thinking(False)

        # Record the modified command and its sensitivity
        HomeCommand.commands[wrapper] = self.sensitivity
        return wrapper

    @staticmethod
    def __safe_call(func, body, *args, **kwargs):
        """Helper method to perform a safe call using the given method.

        Catches recoverable exceptions and logs the results.

        Args:
            func (callable): Method to call.
            body (Body): Body to use to make the call.
            args (list): Positional arguments to use in the call.
            kwargs (dict): Keyword arguments to use in the call.
        """
        try:
            result = func(body, *args, **kwargs)

        # Catch and report recoverable errors
        except requests.exceptions.ConnectionError:
            body.logger.log_warn(func.__name__, format_exc())
            # Proclaim the command failed but will not kill me
            body.report_warn(func.__name__, 'Connection Error')

        # For all unexpected errors, log the error before raising it
        except Exception as e:
            body.logger.log_error(func.__name__, format_exc())
            # Proclaim the command failed and will kill me
            # Add necessary spaces in the exception name to say it properly
            formatted_exception_name = toolbox.split_caps(type(e).__name__)
            body.report_error(func.__name__, formatted_exception_name)
            # Lastly, delete the body to close its logger before allowing
            #   the exception to kill the program
            del body
            raise

        # If the call succeeded, log its success
        else:
            body.logger.log_info(func.__name__, result)

    @classmethod
    def get_commands(cls):
        """Returns all commands I have seen mapped to their sensitivities."""
        return cls.commands
