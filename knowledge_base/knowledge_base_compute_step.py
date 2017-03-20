from util import paths
import pickle
from knowledge_base.analyser import Analyser
from knowledge_base.memstore import MemStore
from knowledge_base.neomemstore import NeoMemStore
import re
 
#STEP 3
### NEW AND EXPERIMENTAL
memstore = NeoMemStore()
memstore.import_memstore(paths.MEMSTORE_PATH_EXPERIMENTAL)
memstore.update_lexicon("related to")
rel_id = "related to"
memstore.computePerspective("LAxLIRA")
a = memstore.lexicon
analyser = Analyser(memstore, "LAxLIRA", compute=False, trace=True)
SIM_LIM = 10

terms = [x for x in memstore.sorted() if not re.search(".*_[0-9]+$|related to|close to", x)]
sim_dict = {}
for i, t1 in enumerate(terms):
    print(i , " out of ", len(terms))
    sims2src = {}
    for t2, s in analyser.similarTo(t1, top=SIM_LIM, sims2src=sims2src):
        if not ((t1, rel_id, t2) in sim_dict or (t2, rel_id, t2) in sim_dict):
            sim_dict[(t1, rel_id, t2)] = s
for key, value in sim_dict.items():
    print("MEMSTORE.CORPUS[<KEY>] = <VALUE> --- KEY: ", key, " --- VALUE: ", value)
    memstore.corpus[key] = value ### purge memstore before doing this?
memstore.export(paths.MEMSTORE_PATH_EXPERIMENTAL + "/")

 
# OLD BUT WORKS
memstore = MemStore(trace=True)
memstore.imp(paths.MEMSTORE_PATH)
print(memstore.lexicon["look"])
original_size = len(memstore.corpus)
print("ORIGINAL SIZE: ", original_size)
memstore.lexicon.update("related to")
rel_id = memstore.lexicon["related to"]
print("RELATED_TO ID IN LEXICON: ", rel_id)
memstore.computePerspective('LAxLIRA')
 
## does not work with trace=False - TODO: investigate why
analyser = Analyser(memstore, "LAxLIRA", compute=False, trace=True)
 
SIM_LIM = 10
term_ids = memstore.lexicon.sorted(limit=0, \
         ignored=[".*_[0-9]+$", "close to", "related to"])
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
            sim_dict[(t1, "related to", t2)] = s
            # storing the computed values to the corpus
for key, value in sim_dict.items():
    print("MEMSTORE.CORPUS[<KEY>] = <VALUE> --- KEY: ", key, " --- VALUE: ", value)
    memstore.corpus[key] = value
 
memstore.exp(paths.MEMSTORE_PATH + "/")
### CHANGED TO .p EXTENSION
pickle.dump(memstore, open(paths.MEMSTORE_PATH + "/" + "memstore_comp.p", "wb"))
