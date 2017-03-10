from knowledge_base.memstore import MemStore
from util import paths
import pickle

# STEP 2
memstore = MemStore()
closenesses = pickle.load(open(paths.CLOSENESS_PATH + "/closeness.p", "rb"))
memstore.incorporate(closenesses) ### FINISHED, 3 march
memstore.computeCorpus() ### 3 march, should be good2go
memstore.normaliseCorpus() ### 3 march, does just computations - should be unbreakable
memstore.exp(paths.MEMSTORE_PATH + "/")
print(len(memstore.corpus)) ### 18030
pickle.dump(memstore, open(paths.MEMSTORE_PATH + "/" + "memstore.p", "wb"))
print("SOURCES - ", memstore.sources)