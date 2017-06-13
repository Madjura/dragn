import gzip
import os
from _collections import defaultdict

from index.helpers import generate_relation_provenance_weights, \
    generate_relation_to_provenances, index_to_db
from knowledge_base.neomemstore import NeoMemStore
from util import paths
from pycallgraph.output.graphviz import GraphvizOutput
from pycallgraph.pycallgraph import PyCallGraph
from graph.node import Node
from graph.graph import Graph
from util.pagerank import PageRank


def generate_relation_values(sources, relations, alias):
    relation2prov, index = generate_relation_provenance_weights(sources)
    index_to_db(index)
    with gzip.open(
            os.path.join(paths.RELATION_PROVENANCES_PATH + alias,
                         "provenances.tsv.gz"), "w") as f_out:
        for relation, prov_weights in relation2prov.items():
            line = "\t".join([str(relation), str(prov_weights)])
            f_out.write(str.encode(line))
            f_out.write(str.encode("\n"))
        _missing, _processed = generate_relation_to_provenances(relations,
                                                                relation2prov,
                                                                f_out)
        print(_missing, _processed)
    f_out.close()


def make_expression_sets(relation_dictionary, alias):
    term_lines = []
    for expression1, related_set in list(relation_dictionary.items()):
        for expression2, weight in related_set:
            term_lines.append("\t".join([str(x)
                                         for x in [expression1, expression2, weight]]))
    with gzip.open(os.path.join(paths.EXPRESSION_SET_PATH_EXPERIMENTAL + alias,
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


def make_pagerank(relations):
    nodes = {}
    for (subject, predicate, objecT), weight in relations:
        if predicate == "close to":
            if not subject in nodes:
                nodes[subject] = Node(name=subject)
            if not objecT in nodes:
                nodes[objecT] = Node(name=objecT)
            edge = nodes[subject].get_edge(end=nodes[objecT])
            if edge and weight > edge.val:
                edge.val = weight
            elif not edge:
                nodes[subject].add_edge(nodes[objecT], weight)
    graph = Graph(nodes=list(nodes.values()))
    pagerank = PageRank(graph)
    pagerank.initial_matrix()
    pagerank.probability_matrix()
    vector = [0 for _ in range(len(nodes.values()))]
    vector[0] = 1
    result = pagerank.iterate_until_convergence(vector, iterations=100)
    foo = sorted(range(len(result.result)), key=lambda k: result.result[k], reverse=True)
    cut = foo[:100]
    pr = []
    for index in cut:
        pr.append((graph.nodes[index].name, result.result[index]))
    print(pr)
    
                
def index_step(alias):
    memstore = NeoMemStore()
    memstore.import_memstore(paths.MEMSTORE_PATH_EXPERIMENTAL + alias)
    relation_dictionary = make_relation_list(memstore.corpus.items(), alias)
    # make_pagerank(memstore.corpus.items())
    make_expression_sets(relation_dictionary, alias)
    generate_relation_values(memstore.relations, memstore.corpus, alias)


def index_step_old():
    """
    OLD STUFF IS GONE
    
    Prepares the data for querying.
    
    Detailed explanation:
        1) Load the memstore from knowledge_base_compute().
        2) Iterate over the corpus items.
            The format is:
                (token, relation, other_token), weight
        3) Create a file suids.tsv, mapping the tuple from 2) to its values.
        # TODO: this can be done better, that system sucks
        # originally used IDs but that is gone because its bad
            3.1) Add the expressions from 2) to a dictionary, mapping the tokens
                to the other token with their weight.
                The format is:
                    {token: ( (other_token, weight), (other_token2, weight2), ...)}
        4) Iterate over the dictionary from 3.1):
            4.1) Iterate over the set of related tokens from 4):
                4.1.1) Write the relations to a file expressionsets, in the 
                    format:
                        token, token2, weight
        5) Take the result of 3) and process it as follows:
            5.1) Iterate over memstore.relations.
                Format is:
                    {(token, relation, other_token, provenance): 
                        Closeness.closeness, ...}
            5.2) Extract the Closeness.closeness value (how related two tokens are)
            5.3) Map a tuple of (provenance, closeness) to the corresponding
                tuples (token, relation, other_token), as taken from 3).
        6) Iterate over the tuples from 5):
            6.1) Write to a file provenances, in the format:
                (token, related to, other_token), provenance, Closeness.closeness
        7) Write to the file from 6): (this is gen_sim_suid2puid_exp)
            7.1) Iterate over the result from 3) (suids).
                7.1.1) For each token, add to a dictionary:
                    {token: ( (relation, token2), (relation, token3) ), }
                7.1.2) If the relation is "related to", add to another
                    dictionary (sim_stmts):
                        (token, token2): ( (token, relation, token2), closeness )
                 7.1.3) Iterate over the dictionary from 7.1.2):
                     - get the key from the previous step ( (token, relation, token2), closeness )
                     - sim_stmts format: (token, token2):  (token, relation, token2), closeness <-- as string
                     - s2po format: token: (relation, token2)
                     - suids format: (token, relation, token2): tuple( string(token, relation, token2), closeness)
                     - suid2puid format: tuple(token, relation, token2): list[ tuple(prov, closeness), ... ]
                    -  puid2weight format: dictionary( provenance: list[weights] ) 
        
        STEP BY STEP for gem_sim_suid2puid_exp:
            - make a dictionary mapping tokens to their "relation tokens", s2po:
                token: set( (relation, token2), (relation, token2), ...)
            - if the relation is "related to", additionally:
                - add to a dictionary sim_stmts the following:
                    - (token, token2): set( (string(token, relation, token2), closeness), ... )
            - iterate over (token, token2) from sim_stmts and also get the relation value (closeness value, sim_w):
                - get the full relation (token, relation, token2) and closeness from stmts for token, token2
                - from s2po, get the (token, relation) tuples that appear in the mapping for both token and token2:
                assume this:
                    paul: set( (close to, ball), (close to, house) )
                    peter: set( (close to, ball, (close to, door) )
                this would get only (close to, ball)
                - use this tuple to get the full relation statement from suids:
                    suids[(token, relation, "ball")][0]
                    suids[(token2, relation, "ball"][0]
                    (this is a string)
                - from suid2puid get the tuples of (prov, closeness) 
                    for the suids from the previous step and add them to a list
                - iterate over that list and add the closeness to a dictionary 
                    of lists with the prov as key (puid2weight):
                    { prov: [closeness, closeness2, ...] }
                - for each prov in the dictionary:
                    - get the maximum closeness
                    - multiply that by the "relation value" (sim_w)
                    - write to provenances.tsv.gz, per line:
                        - the relation tuple as string (token, relation, token2)
                        - the prov from the dictionary
                        - the calculated value ("relation value" * sim_w)
                        
            PUID2WEIGHT EXPLANATION:
                - for each "related to" tuple, get token and token2
                - then get the ("related to", other_token) tuples from s2po
                    BUT ONLY THOSE THAT APPEAR IN THE SETS FOR BOTH TOKEN AND TOKEN2!
                    token = paul
                    token2 = peter
                    assume this (s2po):
                        paul: set( (related to, ball), (related to, house) )
                        peter: set( (related to, ball, (related to, door) )
                    the only tuple that it would find is (related to, ball)
                - then, do the following:
                    make tuples 
                    (token, relation, other_token)
                    and
                    (token2, relation, other_token)
                    and for those tokens, get the (prov, value) tuples from
                    suid2puid
                - add the (prov, value) tuples to a list
                - for prov, value in list:
                    append to puid2weight[prov] the value 
                    
                - iterate over each prov in puid2weight, get the maximum value
                    - multiply that value by the closeness of the current tuple that
                        is being processed
                        the tuple is from sim_stmts and in the format:
                            (token, related to, token2), closeness
                    - then, write to the file multiple lines, the lines are in 
                        the format:
                        string( (token, related to, token2) ),  prov, the calculated value
                - IN SHORT:
                    write to a file how "related to" two tokens are in a given provenance
    """


def with_graphvizoutput():
    graphviz = GraphvizOutput()
    graphviz.output_file = 'index_step.png'

    with PyCallGraph(output=graphviz):
        index_step()


if __name__ == "__main__":
    index_step()
    #with_graphvizoutput()