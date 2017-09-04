import gzip
import os
import ujson
from _collections import defaultdict

from index.helpers import generate_relation_provenance_weights, \
    add_related_to, index_to_db
from knowledge_base.neomemstore import NeoMemStore
from util import paths
from pycallgraph.output.graphviz import GraphvizOutput
from pycallgraph.pycallgraph import PyCallGraph


def generate_relation_values(sources, relations: "memstore corpus", alias):
    relation2prov, index = generate_relation_provenance_weights(sources, relations)
    index_to_db(index)
    with gzip.open(
            os.path.join(paths.RELATION_PROVENANCES_PATH + alias,
                         "provenances.tsv.gz"), "w") as f_out:
        for relation, prov_weights in relation2prov.items():
            line = "\t".join([str(relation), str(prov_weights)])
            f_out.write(str.encode(line))
            f_out.write(str.encode("\n"))
        # replace None with f_out when done
        f = add_related_to(relations, relation2prov, f_out)
        merge = {**relation2prov, **f}
    p = os.path.join(paths.RELATION_PROVENANCES_PATH + alias, "r2p.json")
    with open(p, "w") as f:
        f.write(ujson.dumps(merge))
    # format is (spo): (prov, score)


def make_relation_weights(relation_dictionary, alias):
    term_lines = []
    for expression1, related_set in list(relation_dictionary.items()):
        for expression2, weight in related_set:
            term_lines.append("\t".join([str(x)
                                         for x in [expression1, expression2, weight]]))
    with gzip.open(os.path.join(paths.RELATION_WEIGHT_PATH + alias,
                                "relationsets.tsv.gz"), "wb") as f:
        f.write(("\n".join(term_lines)).encode())
    f.close()


def make_relation_list(relations, alias):
    """
    Creates a mapping of token: set of relations.
        Example:
            Paul: set( (house, close to), (ball, related to), ...)
    """

    relation_lines = []
    relation_dictionary = defaultdict(lambda: set())
    for (subject, predicate, objecT), weight in relations:
        relation_lines.append(
            "\t".join(
                [str(x) for x in [(subject, predicate, objecT), weight]]
            )
        )
        relation_dictionary[subject].add((objecT, weight))
        relation_dictionary[objecT].add((subject, weight))
    with gzip.open(
            os.path.join(paths.RELATIONS_PATH + alias, "relations.tsv.gz"), "wb") as f:
        f.write("\n".join(relation_lines).encode())
    f.close()
    return relation_dictionary

                
def index_step(alias):
    memstore = NeoMemStore()
    memstore.import_memstore(paths.MEMSTORE_PATH_EXPERIMENTAL + alias)
    relation_dictionary = make_relation_list(memstore.corpus.items(), alias)
    # make_pagerank(memstore.corpus.items())
    make_relation_weights(relation_dictionary, alias)
    generate_relation_values(memstore.relations, memstore.corpus, alias)


def with_graphvizoutput():
    graphviz = GraphvizOutput()
    graphviz.output_file = 'index_step.png'

    with PyCallGraph(output=graphviz):
        index_step()


if __name__ == "__main__":
    index_step(alias="/bible_full.txt")
    #with_graphvizoutput()