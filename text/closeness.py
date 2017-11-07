"""Object representation of the weighted distance between two tokens in a text."""
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


class Closeness(object):
    """
    Object representation to describe how close/relevant two terms are to each
    other.
    """

    def __init__(self, term, close_to, closeness, paragraph_id=-1):
        """
        Constructor.
        :param term: A token from a text.
        :param close_to: A token the first token is close to.
        :param closeness: The weighted distance between the two.
        :param paragraph_id: Optional. The ID of the paragraph they appear in.
        """
        self.term = term
        self.close_to = close_to
        self.paragraph_id = paragraph_id
        self.closeness = closeness

    def __str__(self):
        """
        :return: String representation of this Closeness object for better understandability.
        """
        return "Term: " + self.term + "\nClose to:" + self.close_to + "\nParagraph id:" + str(
            self.paragraph_id) + "\nCloseness:" + str(self.closeness)

    def __eq__(self, other):
        if self.term == other.term and self.close_to == other.close_to and self.closeness == other.closeness:
            return True
        return False