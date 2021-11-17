import unittest
from util import toolbox


class TestToolbox(unittest.TestCase):
    """Runs tests on the toolbox functions."""

    def test_split_caps(self):
        """Tests the split_caps function."""
        _in1 = 'CamelCase'
        _out1 = 'Camel Case'
        self.assertEqual(_out1, toolbox.split_caps(_in1))

        _in2 = 'hopefulAttemptat Success'
        _out2 = 'hopeful Attemptat Success'
        self.assertEqual(_out2, toolbox.split_caps(_in2))

    def test_repair_response(self):
        """Tests the repair_response function."""
        _in1 = 'This\u2019ll be changed, I\u00C2m hoping.'
        _out1 = "This'll be changed, I'm hoping."
        self.assertEqual(_out1, toolbox.repair_response(_in1))

        _in2 = 'Bob\u0080\u0092s pet duck is very active.'
        _out2 = "Bob's pet duck is very active."
        self.assertEqual(_out2, toolbox.repair_response(_in2))


if __name__ == '__main__':
    unittest.main()
