from util import paths
import pickle
from knowledge_base.neomemstore import NeoMemStore
 
#==============================================================================
# #STEP 2  
# ## OLD AND WORKING
#   
# from knowledge_base.memstore import MemStore
# memstore = MemStore()
# closenesses = pickle.load(open(paths.CLOSENESS_PATH + "/closeness.p", "rb"))
# memstore.incorporate(closenesses) ### FINISHED, 3 march
# memstore.computeCorpus() ### 3 march, should be good2go
# memstore.normaliseCorpus() ### 3 march, does just computations - should be unbreakable
# memstore.exp(paths.MEMSTORE_PATH + "/")
# print(len(memstore.corpus)) ### 18030
# print(memstore.sources)
# pickle.dump(memstore, open(paths.MEMSTORE_PATH + "/" + "memstore.p", "wb"))
# print("SOURCES - ", memstore.sources)
#==============================================================================

  
## NEW AND EXPERIMENTAL
## CHECKED: 13 march - WORKS
memstore = NeoMemStore()
closenesses = pickle.load(open(paths.CLOSENESS_PATH + "/closeness.p", "rb"))
memstore.incorporate(closenesses) ### FINISHED, 3 march
memstore.computeCorpus() ### 3 march, should be good2go
memstore.normaliseCorpus() ### 3 march, does just computations - should be unbreakable
memstore.export(paths.MEMSTORE_PATH_EXPERIMENTAL + "/")
print(len(memstore.corpus)) ### 1791 - investigate why diferent
print(memstore.sources)
pickle.dump(memstore, open(paths.MEMSTORE_PATH_EXPERIMENTAL + "/" + "memstore.p", "wb"))
