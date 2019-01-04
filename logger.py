from datetime import datetime


class Logger:
    """Logs command results either to a file or to the console.

    Each reported command is logged with a log level, date, and time.
    There are three different log levels:
        * INFO: Command was successfully run. Records the command's name and its
            output.
        * WARN: Command was not successfully run, but the thrown exception was
            recoverable. Records the command's name and the exception's
            stacktrace.
        * ERROR: Command was not successfully run, and the thrown exception was
            not recoverable. Records the command's name and the exception's
            stacktrace.
    When an instance is initialized or deleted, it records the date and time.
    When an instance is deleted, it reports how many commands it recorded in its
    lifetime and closes its output stream, if it made one.

    Args:
        filename (str): Name of the file to log to WITH extension. Creates it if
            it doesn't exist. Appends to it if it already exists. All log files
            are written to the "logs" directory. Logs to the console if no file
            is specified.
    """

    def __init__(self, filename=None):
        # If I was given a filename, create a stream to the file
        if filename:
            # Hold the output stream
            self.outstream = open('logs/' + filename, 'a')
            # Hold the callable to log with
            self.writer = self.outstream.write
        # Otherwise, just log to console
        else:
            # We do not need a new output stream
            self.outstream = None
            # Hold the callable to log with
            self.writer = print

        # Remembers how many commands have been run since I've started
        self.num_commands = 0

        # Write beginning log information
        to_write = '\n-----------------\n' \
            'Logger initialized on {}.\n'.format(datetime.now())
        self.writer(to_write)

    def __del__(self):
        """Append ending statement and close the file, if I opened one."""
        to_write = 'Logger closed on {}, ran {} commands.\n'.format(
            datetime.now(), self.num_commands
        ) + '-----------------\n'
        self.writer(to_write)
        if self.outstream:
            self.outstream.close()

    # Helper #
    @staticmethod
    def __format_issue(command, stacktrace):
        """Helper method to format an error.

        Given a command's name and the stacktrace of the exception it threw,
        formats the two into a proper message. Accomplishes this by adding four
        spaces before each line of the stacktrace.
        """
        return 'Command {} threw an exception:\n{}'.format(
            command, stacktrace
        ).replace('\n', '\n    ') + '\n'

    # Log Levels #
    def log_info(self, command, output):
        """Log a successful command and its generated output."""
        to_write = '[INFO : {}] Ran {} command, output: {}\n'.format(
            datetime.now(), command, output
        )
        self.writer(to_write)
        self.num_commands += 1

    def log_warn(self, command, stacktrace):
        """Log an unsuccessful command and its exception's stacktrace.

        For use when the exception was recoverable.
        """
        to_write = '[WARN : {}] {}'.format(
            datetime.now(), self.__format_issue(command, stacktrace)
        )
        self.writer(to_write)

    def log_error(self, command, stacktrace):
        """Log an unsuccessful command and its exception's stacktrace.

        For use when the exception was not recoverable.
        """
        to_write = '[ERROR: {}] {}'.format(
            datetime.now(), self.__format_issue(command, stacktrace)
        )
        self.writer(to_write)
