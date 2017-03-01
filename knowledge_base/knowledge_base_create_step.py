from knowledge_base.memstore import MemStore
from util import paths
import pickle

# STEP 2
memstore = MemStore()
closenesses = pickle.load(open(paths.CLOSENESS_PATH + "/closeness.tsv", "rb"))
memstore.incorporate(closenesses)
memstore.computeCorpus()
memstore.normaliseCorpus()
pickle.dump(memstore, open(paths.MEMSTORE_PATH + "/" + "memstore", "wb"))