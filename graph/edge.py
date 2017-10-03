"""Edges/Vertices in the dragn graph system."""
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
from graph.exceptions import MissingSourceEndError


class Edge(object):
    """Edges of a graph."""

    def __init__(self,
                 *,
                 start=None,
                 end=None,
                 val=0,
                 color=None):
        """
        Constructor
        
            Args:
                start: The source of the edge.
                end: The target of the edge.
                color: Optional. The color of the edge.
        """

        # Check if start and end are set
        if any(x is None for x in [start, end]):
            raise (MissingSourceEndError("Start and end are required"))
        self.start = start
        self.end = end
        self.val = val
        self.color = color
