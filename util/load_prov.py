#  -*- coding: utf-8 -*-
"""Helper function to load content of paragraphs."""
import os

from util import paths


def load_prov(name):
    """
    Loads the contents of a paragraph by name.
    :param name: The name of the paragraph.
    :raises FileNotFoundError: If no such file can be found.
    :return: The content of that paragraph.
    """
    try:
        path = os.path.join(paths.PARAGRAPH_CONTENT_PATH, name)
        with (open(path, "r", encoding="utf8")) as text:
            content = text.read()
        return content
    except FileNotFoundError:
        return None
