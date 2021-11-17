import re


def split_caps(orig_str):
    """Adds a space before each non-leading capital letter.

    Examples:
        >>> split_caps('ConnectionError')
        'Connection Error'
        >>> split_caps('FileNotFoundError')
        'File Not Found Error'
        >>> split_caps('gTTSError')
        'g T T S Error'

    Args:
        orig_str (str): String to split.

    Returns:
        str: The reformatted string.
    """
    return re.sub(r'(?<=\S)([A-Z]*?)([A-Z])', r'\1 \2', orig_str)


def repair_response(orig_str):
    """Fixes odd/malformed web requests.

    Certain responses from websites (i.e. https://icanhazdadjoke.com) can return
    non-ascii characters that are typically problematic apostrophes
    (i.e. 0x2019, 0x00C2). This function replaces these characters with normal
    apostrophes (') to repair the string. They can also contain tabs or
    newlines. This function replaces them with spaces.

    Args:
        orig_str (str): Response string to repair.

    Returns:
        str: Response string with all non-ascii characters replaced with
            apostrophes (') and all newlines and tabs replaced with spaces.
    """
    fixed_apostrophes = re.sub(r'[^\x00-\x7f]+', "'", orig_str)
    return re.sub(r'\r\n|\n|\t', ' ', fixed_apostrophes)
