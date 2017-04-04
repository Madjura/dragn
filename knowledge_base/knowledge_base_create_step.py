from util import paths
import pickle
from knowledge_base.neomemstore import NeoMemStore
  

def knowledge_base_create():
    """
    NeoMemStore is built in this step, based on the texts from the text_extract step.
    After this step, NeoMemStore holds normalised "closeness values":
        <expression> close to <other expression>: normalised value
    For details regarding the normalisation, see the compute_corpus() and
    normalise_corpus() methods.
    """
    
    memstore = NeoMemStore()
    closenesses = pickle.load(open(paths.CLOSENESS_PATH + "/closeness.p", "rb"))
    memstore.incorporate(closenesses) ### FINISHED, 3 march
    memstore.compute_corpus() ### 3 march, should be good2go
    memstore.normalise_corpus() ### 3 march, does just computations - should be unbreakable
    memstore.export(paths.MEMSTORE_PATH_EXPERIMENTAL + "/")

if __name__ == "__main__":
    knowledge_base_create()
    ## CHECKED: 13 march - WORKS
    ### prints: 67361 for study in temperament + call of cthulhu