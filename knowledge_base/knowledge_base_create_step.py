from util import paths
import pickle
from knowledge_base.neomemstore import NeoMemStore
  

def knowledge_base_create():
    memstore = NeoMemStore()
    closenesses = pickle.load(open(paths.CLOSENESS_PATH + "/closeness.p", "rb"))
    memstore.incorporate(closenesses) ### FINISHED, 3 march
    memstore.computeCorpus() ### 3 march, should be good2go
    memstore.normaliseCorpus() ### 3 march, does just computations - should be unbreakable
    memstore.export(paths.MEMSTORE_PATH_EXPERIMENTAL + "/")
    print(len(memstore.corpus)) ### 1791 - investigate why diferent
    pickle.dump(memstore, open(paths.MEMSTORE_PATH_EXPERIMENTAL + "/" + "memstore.p", "wb"))

if __name__ == "__main__":
    knowledge_base_create()
    ## CHECKED: 13 march - WORKS
    # april3: looks fine, lexicon seems suspicious - holds "Token close to Token2" stuff - unsure if that makes sense?
    
    ### prints: 67361