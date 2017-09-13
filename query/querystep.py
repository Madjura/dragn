"""dragn queries."""
from query.queryresult import QueryResult
from pycallgraph.output.graphviz import GraphvizOutput
from pycallgraph.pycallgraph import PyCallGraph


def query(user_query=None, alias=None, lesser_edges=True):
    """
    Performs a query over texts as specified by the Alias.
    :param user_query: The query of the user.
    :param alias: The Alias of the texts.
    :param lesser_edges: Whether relations between nodes that are not in the query are to be considered.
    :return: A QueryResult object with the query performed.
    """
    if user_query is None:
        user_query = []
    result = QueryResult(alias=alias, lesser_edges=lesser_edges)
    result.query = user_query
    result.populate_dictionaries()
    return result


def with_graphvizoutput():
    """
    Runs query_step with GraphvizOutput, producing a call graph of all functions.
    :return:
    """
    graphviz = GraphvizOutput()
    graphviz.output_file = 'querystep.png'
    with PyCallGraph(output=graphviz):
        query(["cult", "fish", "water", "fear"])


if __name__ == "__main__":
    query(["cult", "fish", "water", "fear"])
    # with_graphvizoutput()
