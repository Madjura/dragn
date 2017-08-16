from query.queryresult import QueryResult
from pycallgraph.output.graphviz import GraphvizOutput
from pycallgraph.pycallgraph import PyCallGraph


def query(user_query=None, alias=None):
    if user_query is None:
        user_query = []
    result = QueryResult(alias=alias)
    result.query = user_query
    result.populate_dictionaries()
    return result


def with_graphvizoutput():
    graphviz = GraphvizOutput()
    graphviz.output_file = 'querystep.png'
    with PyCallGraph(output=graphviz):
        query(["cult", "fish", "water", "fear"])


if __name__ == "__main__":
    query(["cult", "fish", "water", "fear"])
    #with_graphvizoutput()