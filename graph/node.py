from graph.edge import Edge

class Node(object):
    '''
    Node of a graph.
    '''

    def __init__(self, name: str, edges: [Edge] = None):
        '''
        Constructor
        '''
        
        self.name = name
        if edges is None:
            self.edges = []
        else:
            self.edges = edges
        
    def add_edge(self, end: int = None, val: int = 0):
        """
        Adds an edge to this node.
            
            Args:
                end: The end node.
                val: The value of the edge. Default: 0.
        """
        
        if end is None:
            return "End must be set"
        
        self.edges.append(Edge(self, end, val))
        
    def add_edge_object(self, edge: Edge):
        self.edges.append(edge)
        
    def get_edge(self, end: int = None):
        """
        Returns the edge from this node to the target node.
        
            Args:
                end: The end node.
            Returns:
                The edge from this node to the target node, or None if no such
                edge exists.
        """
        
        if end is None:
            return "End must be set"
        
        for edge in self.edges:
            if edge.end == end:
                return edge
        return None
    
    def __str__(self, *args, **kwargs):
        return "(Node: {} | # of edges: {})".format(self.name, len(self.edges))