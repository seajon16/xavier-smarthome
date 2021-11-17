from unittest.mock import Mock
#from RPi import GPIO  TODO AHHH
GPIO = Mock()
from pygame import mixer
from pygame.mixer import music
from gtts import gTTS
from gtts.tts import gTTSError


class Body:
    """Handles all interactions with the real world

    Uses its argumment to understand which pins it will use, setting up GPIO.
    Manages the pygame mixer that handles all speech/music.

    Args:
        pin_mapping (dict): Mapping of which pins relate to which functions.

    Raises:
        KeyError: If pin_mapping does not define all required keys. Default
            required keys are 'thinking' and 'lamp', defined in the
            REQUIRED_KEYS static field.
        TypeError: If any values in pin_mapping are not integers.
    """

    # Pin mappings that must be defined
    REQUIRED_KEYS = ['thinking', 'lamp']

    def __init__(self, pin_mapping):
        # Check for existence of required pins
        if not all(key in pin_mapping for key in REQUIRED_KEYS):
            raise KeyError(
                'pin_mapping does not define all the required keys: '
                + ', '.join(REQUIRED_KEYS)
            )

        # Extract the pins I need to use
        try:
            used_pins = [int(pin) for pin in pin_mapping.values()]
        except ValueError:
            raise TypeError(
                'Error reading pin_mapping: Not all values are ints'
            )

        self.pin_mapping = pin_mapping

        # Set up the sound player (mixer) only if it hasn't been initialized yet
        if not mixer.get_init():
            # Set the frequency to 24000Hz, since that's what gTTS uses
            mixer.pre_init(24000)
            mixer.init()
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)  # TODO research this
        GPIO.setup(used_pins, GPIO.OUT)

    def __del__(self):
        """Turn off all pins, close the mixer, and clean up GPIO."""
        for pin_num in self.pin_mapping.values():
            GPIO.output(pin_num, False)
        mixer.quit()
        GPIO.cleanup()

    # Main Interfaces #
    def set_pin(self, pin_name, value):
        """Sets the given pin name to the given boolean value.

        Args:
            pin_name (str): To set.
            value (bool): To set the pin to.
        """
        GPIO.output(self.pin_mapping[pin_name], value)

    def toggle_pin(self, pin_name):
        """Toggles the given pin name.

        Args:
            pin_name (str): To toggle.
        """
        pin_num = self.pin_mapping[pin_name]
        GPIO.output(pin_num, not GPIO.input(pin_num))

    @staticmethod
    def play_sound(sound):
        """Given the name of an mp3 (no extension/dir), plays the sound.

        Static since the mixer's initialization is global and is not attached to
        an instance.

        Args:
            sound (str): MP3 to play with no extension/dir.
        """
        # Ensure the mixer has been initialized
        if not mixer.get_init():
            raise RuntimeError(
                'Mixer has not been initialized yet; create a new instance.'
            )
        music.load(f'sounds/{sound}.mp3')
        music.play()
        while music.get_busy():
            continue

    @staticmethod
    def say(text):
        """Given a string of text, speak it.

        If I could not connect to GTTS, I will speak a custom, pre-recorded
        error message, then raise a gTTSError.
        Static since the mixer's initialization is global and is not attached to
        an instance.

        Args:
            text (str): Text to speak.

        Raises:
            gTTSError: If GTTS couldn't connect.
        """
        try:
            tts = gTTS(text, 'en-uk')
            tts.save('sounds/temp_voice.mp3')
            Body.play_sound('temp_voice')
            # Load a different, constant sound to prevent IO errors
            music.load('sounds/gtts_failure.mp3')

        # If GTTS couldn't connect, give a custom message before raising it
        except gTTSError:
            # Use the default gtts_failure voice file to proclaim I failed
            Body.play_sound('gtts_failure')
            raise


# Console for testing purposes
if __name__ == "__main__":
    body = Body({'thinking': 20, 'lamp': 21})
    mapping = {
        'play_sound': body.play_sound,
        'say': body.say
    }
    while True:
        cmd = input('Enter/list/exit: ')
        pieces = cmd.split(maxsplit=1)
        cmd_ptr = mapping.get(pieces[0])
        if cmd_ptr:
            if len(pieces) == 2:
                cmd_ptr(pieces[1])
            else:
                print('Command needs an argument')
        elif cmd == 'list':
            for opt in mapping:
                print(opt)
        elif cmd == 'exit':
            break
        else:
            print('Invalid command')

    del body
