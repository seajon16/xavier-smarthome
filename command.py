from pathlib import Path
from inspect import signature
from abc import ABC, abstractmethod
from gtts.tts import gTTSError
from pygame import error as pygame_error


class Command(ABC):
    """Holds information on a given command.

    Args:
        name (str): Name of the command.
        func (callable): Function/method the command runs.
        sensitivity (float): Sensitivity used in hotword detection.
        exceptions (tuple, optional): Exceptions that this Command can recover
            from. Cannot include gTTSError, as Xavier handles these exceptions
            differently to properly report TTS failures. Also cannot include
            pygame.error, since most of Xavier's core functionality depends on
            its ability to speak and play sounds.
        sound (str, optional): Name of an mp3 (no extension) to have a 10%
            chance to play intead of running the normal callback.

    Raises:
        TypeError: If exceptions contained gTTSError or pygame.error.
        FileNotFoundError: If sound is defined but does not refer to an
            existing sound in the sounds directory.
    """

    # Exceptions that cannot be caught
    FORBIDDEN_EXCEPTIONS = {
        gTTSError,
        pygame_error
    }

    def __init__(self, name, func, sensitivity, exceptions=tuple(), sound=None):
        self.name = name
        self.func = func
        self.sensitivity = sensitivity
        for ex in exceptions:
            if ex in self.FORBIDDEN_EXCEPTIONS:
                raise TypeError(
                    f'You cannot ignore {type(ex).__name__} exceptions; they '
                    'are required for Xavier to fully run and cannot be ignored'
                )
        self.exceptions = exceptions

        # Ensure I'll be able to load the sound later
        if sound:
            sound_path = Path('sounds/{}.mp3'.format(sound))
            if not sound_path.is_file():
                raise FileNotFoundError(
                    'Error initializing {}: {} does not exist'.format(
                        name, sound_path
                    )
                )
        self.sound = sound

    @abstractmethod
    def __call__(self):
        """Run my decorated callback, requiring a plugin if needed.

        Returns:
            str: The command's output.
        """
        pass

    def decorate(self, xavier):
        """Decorate my callback using a given Xavier object."""
        self.decorated_func = xavier.decorate_command(self)


class HeadedCommand(Command):
    """Holds a command that needs a plugin reference to run."""

    def __call__(self, plugin):
        """Run my decorated callback using the plugin object I came from.

        Returns:
            str: The command's output.
        """
        return self.decorated_func(plugin)


class HeadlessCommand(Command):
    """Holds a command that does not need a plugin reference to run."""

    def __call__(self):
        """Run my decorated callback and return its output.

        Returns:
            str: The command's output.
        """
        return self.decorated_func()


def mark_command(sensitivity, *exceptions, name=None, sound=None):
    """Decorator to designate a callback as a command.

    Used when declaring commands in a plugin class. Has the same args.
    """
    def decorator(func):
        # If it requires its plugin to run, then it's a normal method
        #   Otherwise, it's a static method that does not need its plugin to run
        command_type = \
            HeadedCommand if signature(func).parameters else HeadlessCommand
        return command_type(
            name or func.__name__,
            func,
            sensitivity,
            exceptions,
            sound
        )
    return decorator
