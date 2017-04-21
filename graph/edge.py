from graph.exceptions import MissingSourceEndError


class Edge(object):
    """
    Edges of a graph.
    """
    
    def __init__(self, start: int = None, end: int = None, val: int = 0,
                 color=None):
        """
        Constructor
        
            Args:
                start: The source of the edge.
                end: The target of the edge.
                value: Optional. The edge weight.
                color: Optional. The color of the edge. 
        """
        
        # Check if start and end are set
        if any(x is None for x in [start, end]):
            raise(MissingSourceEndError("Start and end are required"))
        self.start = start
        self.end = end
        self.val = val
        self.color = color