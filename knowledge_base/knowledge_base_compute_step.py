from util import paths
import pickle
from knowledge_base.analyser import Analyser

# STEP 3
memstore = pickle.load(open(paths.MEMSTORE_PATH + "/" + "memstore", "rb"))
original_size = len(memstore.corpus)
memstore.lexicon.update("related_to")
rel_id = memstore.lexicon["related_to"]
memstore.computePerspective("LAxLIRA")

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
            sim_dict[(t1, rel_id, t2)] = s
            # storing the computed values to the corpus
for key, value in sim_dict.items():
    memstore.corpus[key] = value
    
pickle.dump(memstore, open(paths.MEMSTORE_PATH + "/" + "memstore_comp", "wb"))