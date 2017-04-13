import json
class Graph(object):
    '''
    Simple graph with nodes and edges.
    '''

    def __init__(self, nodes: ["Node"] = None):
        '''
        Constructor
        '''
        
        if nodes is not None:
            self.nodes = nodes
        else:
            self.nodes = []
            
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
        
            Returns:
                An RFC4627 compliant JSON string for use with Cytoscape.js.
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
                    "width": node.width,
                    "color": node.color,
                    "label-size": node.label_size
                    },
                "position": {
                    "x": 1,
                    "y": 1
                },
                "grabbable": True,
                "classes": "node-class"
                })
            for j, edge in enumerate(node.edges):
                edges.append({
                    "group": "edges",
                    "data": {
                        "id": "e{}-{}".format(i,j),
                        "source": edge.start.name,
                        "target": edge.end.name,
                        "color": edge.color
                        }
                    })
        return json.dumps(nodes + edges)