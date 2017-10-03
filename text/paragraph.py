"""Object representation of a Paragraph in a text."""
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
from text.sentence import Sentence


class Paragraph(object):
    """Object representation of a paragraph."""

    def __init__(self, paragraph_id: int, sentences: [Sentence], text=None):
        """
        Constructor.
        :param paragraph_id: The ID of the paragraph in the text. Should be 0-indexed position.
        :param sentences: A list of Sentence objects of sentences contained in this paragraph.
        :param text: Optional. The text this paragraph belongs to.
        """
        self.paragraph_id = paragraph_id
        self.sentences = sentences
        self.text = text
