class DuplicateEdgeError(Exception):
    """
    Exception used to indicate the same edge is being added twice to a graph.
    """

    pass


class MissingSourceEndError(Exception):
    """
    Exception used to indicate an edge is missing either the target or source.
    """

    pass
