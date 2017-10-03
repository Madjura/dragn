#  -*- coding: utf-8 -*-
"""Helper function to load content of paragraphs."""
__copyright__ = """
Copyright (C) 2017 Thomas Huber <huber150@stud.uni-passau.de, madjura@gmail.com>
All rights reserved.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
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
