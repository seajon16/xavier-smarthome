import unittest
from core import Body
from command import HomeCommand


class TestCommand(unittest.TestCase):
    """Runs tests on HomeCommand."""

    def test_command_recording(self):
        """Tests the decorator's ability to record each command.

        May fail if changes are made to the default version of this project.
        """
        _pin_mapping = {"thinking": 10, "lamp": 11}
        _result = HomeCommand.get_commands()
        self.assertIn(Body.joke, _result)
        self.assertEqual(_result[Body.joke], 0.5)
        self.assertIn(Body.weather_tomorrow_brief, _result)
        self.assertEqual(_result[Body.weather_tomorrow_brief], 0.5)


if __name__ == '__main__':
    unittest.main()
