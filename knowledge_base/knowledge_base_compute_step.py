from util import paths
import pickle
from knowledge_base.analyser import Analyser
from knowledge_base.memstore import MemStore

# STEP 3
# TODO: MAKE THIS WORK WITH STRINGS INSTEAD OF INTS
# breaks with memstore.p instead of memstore
memstore = MemStore(trace=True)
memstore.imp(paths.MEMSTORE_PATH)
original_size = len(memstore.corpus)
print("ORIGINAL SIZE: ", original_size)
memstore.lexicon.update("related to")
rel_id = memstore.lexicon["related to"]
print("RELATED_TO ID IN LEXICON: ", rel_id)
memstore.computePerspective('LAxLIRA')

#==============================================================================
# memstore = pickle.load(open(paths.MEMSTORE_PATH + "/" + "memstore.p", "rb"))
# original_size = len(memstore.corpus)
# memstore.lexicon.update("related_to")
# rel_id = memstore.lexicon["related_to"]
# memstore.computePerspective("LAxLIRA") ### complicated, mathematical
#==============================================================================

## does not work with trace=False - TODO: investigate why
analyser = Analyser(memstore, "LAxLIRA", compute=False, trace=True)

SIM_LIM = 10
term_ids = memstore.lexicon.sorted(limit=0, \
         ignored=[".*_[0-9]+$", "close_to", "related_to", "close to"])
sim_dict = {}
i = 0
for t1 in term_ids:
    i += 1
    print("  ...", i, "out of", len(term_ids))
    # getting a fresh similarity statement provenance index
    sims2src = {}
    # computing the similarities for the given term
    for t2, s in analyser.similarTo(t1, top=SIM_LIM, sims2src=sims2src):
        if not ((t1, rel_id, t2) in sim_dict or (t2, rel_id, t1) in sim_dict):
            # adding if a symmetric one was not added before
            ###sim_dict[(t1, rel_id, t2)] = s
            sim_dict[(t1, "related_to", t2)] = s
            # storing the computed values to the corpus
for key, value in sim_dict.items():
    print("MEMSTORE.CORPUS[<KEY>] = <VALUE> --- KEY: ", key, " --- VALUE: ", value)
    memstore.corpus[key] = value

memstore.exp(paths.MEMSTORE_PATH + "/")
### CHANGED TO .p EXTENSION
pickle.dump(memstore, open(paths.MEMSTORE_PATH + "/" + "memstore_comp.p", "wb"))