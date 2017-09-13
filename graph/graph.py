"""Graphs in the dragn graph system."""
import json


class Graph(object):
    """Simple graph with nodes and edges."""
    def __init__(self, *, nodes: ["Node"] = None, clean=True):
        """
        Constructor.
        :param nodes: Optional. A list of nodes that make up the graph.
        :param clean: Optional. Default: True. Whether nodes with no connected edges are to be deleted.
        """
        if nodes is not None:
            self.nodes = nodes
        else:
            self.nodes = []
        if clean:
            for index in range(len(nodes)):
                backindex = len(nodes) - index - 1
                node = nodes[backindex]
                if not node.edges:
                    del nodes[backindex]

    def __str__(self, *args, **kwargs):
        out = ""
        for node in self.nodes:
            out += "Node: {}\n".format(node.name)
            for edge in node.edges:
                out += "--- Edge from {} to {}\n".format(edge.start, edge.end)
        return out

    def to_json(self):
        """
        Converts the graph into RFC4627 compliant JSON. 
        The resulting JSON string is intended to be used with 
        Cytoscape.js 3.0.0 (http://js.cytoscape.org/) and can be loaded into
        it to display the graph.
        :return An RFC4627 compliant JSON string for use with Cytoscape.js.
        """
        # separate lists required to have the nodes before the edges,
        # needed for cytoscape, the edges need the id of the node
        nodes = []
        edges = []
        for i, node in enumerate(self.nodes):
            nodes.append({
                "group": "nodes",
                "data": {
                    "id": node.name,
                    "font-size": 20,
                    "size": node.label_size * 3,
                    "width": node.width,
                    "color": node.color
                },
                "position": {
                    "x": i,
                    "y": i
                },
                "grabbable": True,
                "classes": "node-class"
            })
            for j, edge in enumerate(node.edges):
                edges.append({
                    "group": "edges",
                    "data": {
                        "id": "e{}-{}".format(i, j),
                        "source": edge.start.name,
                        "target": edge.end.name,
                        "color": edge.color
                    }
                })
        return json.dumps(nodes + edges)
