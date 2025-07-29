"""Foos module for dailylog-lib."""


def banner(text: str, **kwargs: bool | int | str) -> str:
    """
    Creates a banner line with the given text in the center.

    Parameters:
    - `text`: str, the text to be centered.
    - `width`: int, the width of the banner line, defaults to 60.
    - `char`: str, the character to be used, defaults to "-".
    - `action`: Optional bool, if True, use "started" as the action if False, use "exiting", defaults to None.

    Returns:
        str, the formatted banner line.
    """
    half = int(int(kwargs.get("width", 60)) / 2)
    char = str(kwargs.get("char", "-"))
    if len(char) > 1:
        char = char[0]
    if "action" in kwargs:
        action = "started" if bool(kwargs.get("action")) else "exiting"
        return "{0} {1} {2} {0}".format(char * half, text, action)
    return "{0} {1} {0}".format(char * half, text)
