from extract.extract_step import extract_step, make_folders
from index.index_step import index_step
from knowledge_base.knowledge_base_compute_step import knowledge_base_compute
from knowledge_base.knowledge_base_create_step import knowledge_base_create
from pycallgraph.output.graphviz import GraphvizOutput
from pycallgraph.pycallgraph import PyCallGraph
from query import querystep


def all_steps(query=None, texts=None, language="english", alias=None):
    alias_object = alias
    alias = "/" + alias.identifier
    print("MAKING FOLDERS")
    make_folders(alias=alias)
    print("FOLDERS DONE, EXTRACT STEP")
    extract_step(texts=texts, language=language, alias=alias)
    print("EXTRACT STEP DONE, KB CREATE")
    knowledge_base_create(alias=alias)
    print("KB CREATE DONE, KB COMPUTE")
    knowledge_base_compute(alias=alias)
    print("KB COMPUTE DONE, INDEX")
    index_step(alias=alias)
    print("INDEX DONE")
    alias_object.processed = True
    alias_object.save()
    if query:
        querystep.query(query)

def with_graphvizoutput():
    graphviz = GraphvizOutput()
    graphviz.output_file = "allstep.png"
    with PyCallGraph(output=graphviz):
        all_steps(["cult", "fish", "water", "fear"])


class FakeAlias(object):
    def __init__(self, identifier):
        self.identifier = identifier


if __name__ == "__main__":
    alias = FakeAlias("test.txt")
    all_steps(texts=["test.txt"], alias=alias)
    #with_graphvizoutput()