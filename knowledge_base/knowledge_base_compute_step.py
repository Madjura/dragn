from util import paths
from knowledge_base.analyser import Analyser
from knowledge_base.neomemstore import NeoMemStore
import re
 
def knowledge_base_compute():
    #STEP 3
    ### NEW AND EXPERIMENTAL
    
    
    memstore = NeoMemStore()
    memstore.import_memstore(paths.MEMSTORE_PATH_EXPERIMENTAL)
    #memstore.update_lexicon("related to") ### this seems useless?
    memstore.computePerspective("LAxLIRA")
    analyser = Analyser(memstore, "LAxLIRA", compute=False, trace=True)
    SIM_LIM = 10
    
    tokens = [x for x in memstore.sorted() if not re.search(".*_[0-9]+$|related to|close to", x)]
    sim_dict = {}
    for i, token1 in enumerate(tokens):
        print(i , " out of ", len(tokens))
        sims2src = {}
        for token2, s in analyser.similarTo(token1, top=SIM_LIM, sims2src=sims2src):
            if not ((token1, "related to", token2) in sim_dict or (token2, "related to", token2) in sim_dict):
                sim_dict[(token1, "related to", token2)] = s
    
    for key, value in sim_dict.items():
        print("MEMSTORE.CORPUS[<KEY>] = <VALUE> --- KEY: ", key, " --- VALUE: ", value)
        memstore.corpus[key] = value ### purge memstore before doing this?
    memstore.export(paths.MEMSTORE_PATH_EXPERIMENTAL + "/")


if __name__ == "__main__":
    knowledge_base_compute()
    ### checked april3, looks fine
    ### analyser needs analizing