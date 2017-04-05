from util import paths
from knowledge_base.analyser import Analyser
from knowledge_base.neomemstore import NeoMemStore
import re
 
def knowledge_base_compute():
    """
    In this step, expressions related to other expressions are identified and 
    stored in the NeoMemStore.
    The format is:
        <expression> related to <other expression>: Value
    This uses the Analyser class to perform the calculations and produce that format.
    """
    
    #STEP 3
    ### NEW AND EXPERIMENTAL
    memstore = NeoMemStore()
    memstore.import_memstore(paths.MEMSTORE_PATH_EXPERIMENTAL)
    memstore.computePerspective("LAxLIRA")
    analyser = Analyser(memstore, "LAxLIRA", compute=False, trace=True)
    SIM_LIM = 10
    
    tokens = [x for x in memstore.sorted() if not re.search(".*_[0-9]+$|related to|close to", x)]
    
    # holds similarity statements - <expression> related to <expression2>: value
    similarity_dictionary = {}
    ###top_value = (0, 0, 0)
    for i, token1 in enumerate(tokens):
        print(i , " out of ", len(tokens))
        sims2src = {}
        similar = analyser.similar_to(token1, top=SIM_LIM, sims2src=sims2src)
        for token2, s in similar:
            if not ((token1, "related to", token2) in similarity_dictionary or (token2, "related to", token1) in similarity_dictionary): ### fix here april4, token1 was token2 in second block
                similarity_dictionary[(token1, "related to", token2)] = s
            #==================================================================
            # if s > top_value[0]:
            #     top_value = (s, token1, token2)
            #==================================================================
    for key, value in similarity_dictionary.items():
        memstore.corpus[key] = value
    memstore.export(paths.MEMSTORE_PATH_EXPERIMENTAL + "/")


if __name__ == "__main__":
    knowledge_base_compute()
    ### checked april3, looks fine