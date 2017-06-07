from knowledge_base.analyser import Analyser
from knowledge_base.neomemstore import NeoMemStore
from util import paths
from pycallgraph.output.graphviz import GraphvizOutput
from pycallgraph.pycallgraph import PyCallGraph


def knowledge_base_compute(top=100):
    """
    In this step, expressions related to other expressions are identified and 
    stored in the NeoMemStore.
    The format is:
        <expression> related to <other expression>: Value
    This uses the Analyser class to perform the calculations and produce that format.
    
    Detailed explanation:
        1) The memstore from the previous step (knowledge_base_create()) 
            is loaded.
        2) The perspective is computed:
            2.1) The corpus is converted to a matrix.
            2.2) The format is:
                token (close to, other_token) -> weight
        3) The Analyser is created. This is used to calculate the "related to"
            relations.
        4) The top memstore lexicon elements are calculated:
            4.1) The lexicon is sorted by frequency values, descending.
            4.2) Frequencies of tokens that are relation statements (close to,
                related to) or provenances are ignored.
            4.3) The average of the remaining frequencies is calculated.
            4.4) All the tokens with above-average frequency are returned in
                a list.
        5) The top elements from 4) are iterated over:
            5.1) For each token, the tokens that are similar are calculated.
                5.1.1) The basis for this are the sparse-representation of the
                    matrix from 2) and the "inverse" of that that is calculated
                    in the same step.
                    The format of the sparse is:
                        {token: {(relation, token): weight, ...} }
                    The format of the inverse is:
                        (relation, token: [tokens]
                5.1.2) The row from the sparse matrix for the token is
                    collected.
                    Example:
                        sparse[Paul] = 
                            {(close to, ball): 0.8, (close to, roof): 0.7, ...}
                5.1.3) The length of the row is calculated:
                    sqrt(sum(weights)^2)
                5.1.4) The possibly related tokens are collected from the 
                    inverse and iterated over.
                    5.1.4.1) The row for the token is collected from the sparse.
                    5.1.4.2) For each expression ((close to, token)), check
                        if it also appears in the row from 5.1.2).
                    5.1.4.3) If it does, multiply the values from the rows
                        and keep them in a variable and add the statements 
                        to a list.
                    5.1.4.4) Add the square of the compared row to a variable.
                    5.1.4.5) After 5.1.4.2), take the square root of the value
                        from 5.1.4.4) to get the length.
                    5.1.4.6) If sum of the products from 5.1.4.3) divided by
                        the length from the previous step multiplied by the sum
                        is above the threshhold, add that value and the current
                        token/expression to a list of results:
                            [(value, token from 5.1.4))]
                        This is used to indicate how closely related the token 
                        from 5.1) and the current one are.
                5.1.5) Sort the list from 5.1.4.6) by values, descending, and
                    return a list of tuples of the relation value and the token,
                    relative to the one from step 5.1).
            5.2) For each "related to" relation from 5.1.5), add that 
                relation to a dictionary:
                    (token, "related to", other_token): value
            5.3) Finally, add the "related to" relations to the corpus of
                the memstore.
        6) Write the memstore, now containing the "related to" relations,
            to the disk.
    """
    memstore = NeoMemStore()
    memstore.import_memstore(paths.MEMSTORE_PATH_EXPERIMENTAL)
    matrix = memstore.corpus.matricise(0)
    analyser = Analyser(memstore, matrix=matrix, trace=True)

    tokens = [x for x in memstore.sorted(ignored=".*_[0-9]+$|related to|close to")]
    similarity_dictionary = {}
    for i, subject in enumerate(tokens):
        print(i, " out of ", len(tokens))
        similar = analyser.similar_to(subject, top=top)
        for objecT, weight in similar:
            triple1 = (subject, "related to", objecT)
            triple2 = (objecT, "related to", subject)
            if not any(triple in similarity_dictionary for triple in [triple1, triple2]):
                similarity_dictionary[(subject, "related to", objecT)] = weight
    for key, value in similarity_dictionary.items():
        memstore.corpus[key] = value
    memstore.export(paths.MEMSTORE_PATH_EXPERIMENTAL + "/")


def with_graphviz_output():
    graphviz = GraphvizOutput()
    graphviz.output_file = 'knowledge_base_compute.png'

    with PyCallGraph(output=graphviz):
        knowledge_base_compute()

if __name__ == "__main__":
    #with_graphviz_output()
    knowledge_base_compute()
