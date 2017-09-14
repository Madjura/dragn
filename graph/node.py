"""Nodes in the dragn graph system."""
from graph.edge import Edge


class Node(object):
    """Node of a graph."""

    def __init__(self, name: str, *, edges: [Edge] = None, color=None, width=None, label_size=None):
        """
        Constructor.
        :param name: The name / label of the node.
        :param edges: Optional. A list of Edge objects connected to this node.
        NOTE: There is no check to ensure the edges all originate from this node. It is thus possible to have a node
        hold edges that do not originate from or target the node itself.
        :param color: Optional. The color of the node.
        :param width: Optional. The width of the node.
        :param label_size: Optional. The size of the label.
        """
        self.name = name
        if edges is None:
            self.edges = []
        else:
            self.edges = edges
        self.color = color
        self.width = width
        self.label_size = label_size

    def add_edge_object(self, edge: Edge):
        """
        Adds an edge to this node.
        :param edge: The edge.
        :return:
        """
        self.edges.append(edge)
        
    def add_edge(self, target, value):
        """
        Adds an edge to this node.
        :param target: The target of the edge.
        :param value: The weight of this edge.
        :return:
        """
        self.edges.append(Edge(start=self, end=target, val=value))

    def get_edge(self, *, end: int = None):
        """
        Returns the edge from this node to the target node.
        :param end: The end node.
        :return: The edge from this node to the target node, or None if no such edge exists.
        """
        if end is None:
            return "End must be set"
        for edge in self.edges:
            if edge.end == end:
                return edge
        return None

    def __str__(self, *args, **kwargs):
        return "(Node: {} | # of edges: {})".format(self.name, len(self.edges))


class CytoNode(Node):
    """
    Special node that checks for duplicate edges when adding an edge.
    Required for use with Cytoscape.js.
    This is required because otherwise the "related to" and "close to" edges
    overlap.
    """

    def add_edge_object(self, edge: Edge):
        """
        Adds an edge to the node.
        This function checks whether a duplicate edge already exists. This
        can happen because a node can be "close to" and "related to" another
        node at the same time. In that case, there same edge exists twice.
        To handle this in Cytoscape.js, the duplicate edges are dyed magenta
        instead of red (related to) or blue (close to).
        :param edge: The edge that is being added.
        :return:
        """
        duplicate = self.get_edge(end=edge.end)
        if not duplicate:
            duplicate = edge.end.get_edge(end=self)
        if duplicate:
            if duplicate.color != edge.color:
                duplicate.color = "magenta"
        else:
            super().add_edge_object(edge)
