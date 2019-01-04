import re


def split_caps(orig_str):
    """Adds a space before each capital letter.

    Example:
        >>> split_caps('ConnectionError')
        'Connection Error'
        >>> split_caps('KeyError')
        'Key Error'

    Args:
        orig_str (str): String to split.

    Returns:
        str: The reformatted string.
    """
    return re.sub(r'(\w)([A-Z])', r'\1 \2', orig_str)


def repair_response(orig_str):
    """Fixes odd/malformed apostrophes from web requests.

    Certain responses from websites (ie https://icanhazdadjoke.com) can return
    non-ascii characters that are typically problematic apostrophes
    (ie 0x2019, 0x00C2). This function replaces these characters with normal
    apostrophes (') to repair the string.

    Args:
        orig_str (str): Response string to repair.

    Returns:
        str: Response string with all non-ascii characters replaced with
            apostrophes (').
    """
    return re.sub(r'[^\x00-\x7f]+', "'", orig_str)
