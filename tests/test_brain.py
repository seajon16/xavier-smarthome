import unittest
from brain import Brain
from enums import WeatherDay


class TestBrain(unittest.TestCase):
    """Runs tests on the response-makers in the Brain.

    Methods get_time and get_date are straightforward and entirely use built-in
    functions, therefore they are not tested here.
    Similarly, get_brief_broadcast reads directly from the weather API, so it is
    not tested here either.
    """

    def setUp(self):
        """Create a new Brain for each test."""
        self.brain = Brain()

    def test_joke(self):
        """Tests the get_joke method.

        The get_joke method pulls a joke from an external API, however it also
        ensures damaged characters do not end up in the result string.
        Therefore, this test ensures common problematic characters are not in
        the output string.
        """
        _response = self.brain.get_joke()
        # Check for the fancy apostrophe
        self.assertNotIn('\u2019', _response)
        # Check for the default unknown character
        self.assertNotIn('\u00C2', _response)
        # Check for another problematic character
        self.assertNotIn('\u0080', _response)
        # Check for newlines
        self.assertNotIn('\n', _response)
        # Check for tabs
        self.assertNotIn('\t', _response)

    def test_full_broadcast(self):
        """Tests the get_full_broadcast method.

        Does this by assuring the bare minimum in a result is present.
        """
        _response = self.brain.get_full_broadcast(WeatherDay.TODAY)
        # Added when addressing the time the response refers to
        self.assertIn(',', _response)
        # Added when adding a temperature
        self.assertIn("it's", _response)
        self.assertIn('with a temperature of', _response)


if __name__ == '__main__':
    unittest.main()
