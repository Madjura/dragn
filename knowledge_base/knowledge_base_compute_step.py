from util import paths
from knowledge_base.analyser import Analyser
from knowledge_base.neomemstore import NeoMemStore
import pprint

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
    memstore.computePerspective("LAxLIRA")
    analyser = Analyser(memstore, "LAxLIRA", trace=True)
    
    tokens = [x for x in memstore.sorted(ignored=".*_[0-9]+$|related to|close to")]
    
    similarity_dictionary = {}
    foo = {}
    similar = None
    similar2similar = None
    for i, token1 in enumerate(tokens):
        print(i , " out of ", len(tokens))
        similar = analyser.similar_to(token1, top=top)
        for token2, weight in similar:
            relation1 = (token1, "related to", token2)
            relation2 = (token2, "related to", token1)
            if not any(r in similarity_dictionary for r in [relation1, relation2]):
                similarity_dictionary[(token1, "related to", token2)] = weight
    for key, value in similarity_dictionary.items():
        memstore.corpus[key] = value
    
    print("DONE WITH FIRST LOOP")
    ### problem here is: similar is updated each iteration
    ### mostly useless to do this here
    ### better to do it in index/querystep
    ### get the top N for query
    ### for those top N, get the top relations too
    ### then add them as a "bonus" with different color?
    ### for each node after initial query, add the top 5 edges
    ### then add the top 5 from those maybe? and so on
    ### based on user input
    for token1, _weight in similar:
        similar2similar = analyser.similar_to(token1, top=top)
        for token2, weight in similar2similar:
            r1 = (token1, "related to", token2)
            r2 = (token2, "related to", token1)
            if not any (r in foo for r in [r1, r2]):
                foo[(token1, "related to", token2)] = weight
    pprint.pprint(foo)
    memstore.export(paths.MEMSTORE_PATH_EXPERIMENTAL + "/")


if __name__ == "__main__":
    knowledge_base_compute()
    ### checked april3, looks fine