from query.queryresult import QueryResult
from pycallgraph.output.graphviz import GraphvizOutput
from pycallgraph.pycallgraph import PyCallGraph


def query(query=None):
    if query is None:
        query = []
    foo = QueryResult()
    foo.query = query
    foo.populate_dictionaries()
    return foo


def with_graphvizoutput():
    graphviz = GraphvizOutput()
    graphviz.output_file = 'querystep.png'
    with PyCallGraph(output=graphviz):
        query(["cult", "fish", "water", "fear"])


if __name__ == "__main__":
    #query(["ron", "dumbledore"])
    with_graphvizoutput()