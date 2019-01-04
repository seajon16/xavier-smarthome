import unittest
from unittest.mock import patch
import re
import os
from io import StringIO
from logger import Logger


class TestLogger(unittest.TestCase):
    """Runs tests on the Logger."""

    # Helpers #
    @staticmethod
    def scrub_string(text):
        """Replaces any timestamp in text with 'TIME'."""
        return re.sub(r'\d*-\d*-\d* \d*:\d*:\d*\.\d*', 'TIME', text)

    @staticmethod
    def scrub_file(filename):
        """Replaces timestamps with 'TIME'.

        Deletes the original file.

        Args:
            filename (str): Name of the file to scrub.

        Returns:
            str: The name of the new file.
        """
        # Build new filename
        name, extension = filename.split('.', 1)
        outname = name + "_scrubbed." + extension

        intext = TestLogger.read_file(filename)
        with open(outname, 'w') as outstream:
            # Use helper to scrub the text
            outtext = TestLogger.scrub_string(intext)
            outstream.write(outtext)

        # Delete the original file
        os.remove(filename)
        return outname

    @staticmethod
    def read_file(filename):
        """Returns the text from a given file.

        Args:
            filename (str): Name of the file.
        """
        with open(filename, 'r') as stream:
            text = stream.read()
        return text

    @staticmethod
    def run_logs(logger):
        """Runs a number of mock logs on the given Logger instance."""
        logger.log_info('neat', 'Played neat.')
        logger.log_info('why', 'Played why.')
        logger.log_info('date', 'Monday, December 17.')
        logger.log_info('toggle_lamp', 'Toggled lamp.')
        stacktrace = \
            'This is a stacktrace.\n' \
            '    This stacktrace has been formatted to test indenting,\n' \
            '        as each line should be indented another four spaces.\n' \
            'Hopefully, this stacktrace looks correct.\n'
        logger.log_warn('joke', stacktrace)
        logger.log_error('time', stacktrace)

    # Tests #
    def test_logger_file(self):
        """Tests the Logger's ability to log to a file."""
        # Set up environment
        _outfile = 'logger_file_output.log'
        _expected_file = 'resources/logger_file_expected.log'
        _logger = Logger(_outfile)

        # Run test
        TestLogger.run_logs(_logger)
        del _logger

        # Scrub (replace times with fakes) and compare results
        _expected = TestLogger.read_file(_expected_file)
        # Note 'logs/' is added to the outfile's path, since the logger stores
        #   all logs to the logs folder
        _scrubbed_name = TestLogger.scrub_file('logs/' + _outfile)
        _actual = TestLogger.read_file(_scrubbed_name)
        self.assertEqual(_expected, _actual)

        # Cleanup
        os.remove(_scrubbed_name)

    @patch('sys.stdout', new_callable=StringIO)
    def test_logger_console(self, mock_stdout):
        """Tests the Logger's ability to log to the console.

        Uses the patch decorator to mock out stdout to check console output.
        """
        # Set up environment
        _expected_file = 'resources/logger_console_expected.log'
        _logger = Logger()

        # Run test
        self.run_logs(_logger)
        del _logger

        # Scrub (replace times with fakes) and compare results
        _expected = TestLogger.read_file(_expected_file)
        _actual = TestLogger.scrub_string(mock_stdout.getvalue())
        self.assertEqual(_expected, _actual)


if __name__ == '__main__':
    unittest.main()
