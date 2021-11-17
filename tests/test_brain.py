import unittest
from brain import Brain
from util.enums import WeatherDay


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
        response = self.brain.get_joke()
        # Check for the fancy apostrophe
        self.assertNotIn('\u2019', response)
        # Check for the default unknown character
        self.assertNotIn('\u00C2', response)
        # Check for another problematic character
        self.assertNotIn('\u0080', response)
        # Check for newlines
        self.assertNotIn('\n', response)
        # Check for tabs
        self.assertNotIn('\t', response)

    def test_full_broadcast(self):
        """Tests the get_full_broadcast method.

        Does this by assuring the bare minimum in a result is present.
        """
        response = self.brain.get_full_broadcast(WeatherDay.TODAY)
        # Added when addressing the time the response refers to
        self.assertIn(',', response)
        # Added when adding a temperature
        self.assertIn("it's", response)
        self.assertIn('with a temperature of', response)


if __name__ == '__main__':
    unittest.main()
