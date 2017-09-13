"""index_step of the dragn pipeline. Generates and writes files containing the results of the processing."""
import gzip
import os
import ujson
from _collections import defaultdict

from index.helpers import generate_relation_provenance_weights, \
    add_related_to, index_to_db
from knowledge_base.neomemstore import NeoMemStore
from util import paths


def generate_relation_values(relations, corpus, alias):
    """
    Generates the file containing the mapping of SPO-triple to (provenance, score).
    :param relations: The existing relations.
    :param corpus: The corpus of the memstore created in knowledge_base_compute.
    :param alias: The Alias of the texts that were processed.
    :return:
    """
    relation2prov, index = generate_relation_provenance_weights(relations, corpus)
    index_to_db(index)
    f = add_related_to(corpus, relation2prov)
    merge = {**relation2prov, **f}
    p = os.path.join(paths.RELATION_PROVENANCES_PATH + alias, "r2p.json")
    # format is (spo): (prov, score)
    with open(p, "w") as f:
        f.write(ujson.dumps(merge))


def make_relation_weights(relation_dictionary, alias):
    """
    Writes the shortform of relations between tokens to a file. The format is:
    token\ttoken2\score
    :param relation_dictionary: A dictionary mapping a token to its relations.
    :param alias: The Alias of the texts that were processed.
    :return:
    """
    term_lines = []
    for token1, related_set in list(relation_dictionary.items()):
        for token2, score in related_set:
            term_lines.append("\t".join([str(x) for x in [token1, token2, score]]))
    with gzip.open(os.path.join(paths.RELATION_WEIGHT_PATH + alias, "relationsets.tsv.gz"), "wb") as f:
        f.write(("\n".join(term_lines)).encode())


def make_relation_list(relations, alias):
    """
    Creates a mapping of token: set of relations.
    Example:
        Paul: set( (house, close to), (ball, related to), ...)
    :param relations: The relations calculated in knowledge_base_compute.
    :param alias: The Alias of the texts that were processed.
    :return: A dictionary mapping tokens to their relation partners and scores.
    """
    relation_lines = []
    relation_dictionary = defaultdict(lambda: set())
    for (subject, predicate, objecT), weight in relations:
        relation_lines.append("\t".join([str(x) for x in [(subject, predicate, objecT), weight]]))
        relation_dictionary[subject].add((objecT, weight))
        relation_dictionary[objecT].add((subject, weight))
    with gzip.open(
            os.path.join(paths.RELATIONS_PATH + alias, "relations.tsv.gz"), "wb") as f:
        f.write("\n".join(relation_lines).encode())
    return relation_dictionary

                
def index_step(alias):
    """
    Performs the index_step step of the dragn pipeline.
    :param alias: The Alias of the texts that were processed.
    :return:
    """
    memstore = NeoMemStore()
    memstore.import_memstore(paths.MEMSTORE_PATH_EXPERIMENTAL + alias)
    relation_dictionary = make_relation_list(memstore.corpus.items(), alias)
    # make_pagerank(memstore.corpus.items())
    make_relation_weights(relation_dictionary, alias)
    generate_relation_values(memstore.relations, memstore.corpus, alias)


if __name__ == "__main__":
    index_step(alias="/bible_full.txt")
    # with_graphvizoutput()
