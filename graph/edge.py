class Edge(object):
    '''
    Edges of a graph.
    '''
    
    def __init__(self, start: int = None, end: int = None, val: int = 0, color=None):
        '''
        Constructor
        '''
        
        # Check if start and end are set
        if any(x is None for x in [start, end]):
            return "Start and end are required"
        self.start = start
        self.end = end
        self.val = val
        self.color = color