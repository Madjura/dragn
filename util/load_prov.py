#  -*- coding: utf-8 -*-

from util import paths

def load_prov(name):
    """
    Loads the content of a file in the PARAGRAPH_CONTENT_PATH directory.
    
        Args:
            name: The name of the file.
        Returns:
            The content of the file, or None if no such file can be found.
    """
    try:
        with (open(paths.PARAGRAPH_CONTENT_PATH + "/" + name, "r", encoding="utf8")) as text:
            content = text.read()
        return content
    except FileNotFoundError:
        return None