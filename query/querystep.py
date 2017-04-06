import gzip
import os
from util import paths
from query.fuzzyset import FuzzySet
from query.termsets import load_tuid2relt
from query.memstorequeryresult import MemStoreQueryResult
from knowledge_base.neomemstore import NeoMemStore
from _collections import defaultdict
import pprint

def get_provenances(relation_dictionary, sources):
    provenance_dictionary = defaultdict(lambda: [])
    for expression, related_to, other_expression, provenance in sources:
        weight = sources[(expression, related_to, other_expression, provenance)]
        provenance_dictionary[(expression, related_to, other_expression)].append((provenance, weight))
    return provenance_dictionary

def experimental_query(query=["cthulhu", "cult", "shoggoth", "dark", "shape", "battle", "disable"]):
    memstore = NeoMemStore()
    memstore.import_memstore(paths.MEMSTORE_PATH_EXPERIMENTAL)
    relation_dictionary = defaultdict(lambda: defaultdict(lambda: []))
    result_set = FuzzySet()
    for (expression, related_to, other_expression), weight in list(memstore.corpus.items()):
        relation_dictionary[expression][related_to].append((other_expression, weight))
        relation_dictionary[other_expression][related_to].append((expression, weight))
        
    for term in query:
        result_set |= FuzzySet(relation_dictionary[term]["close to"] + relation_dictionary[term]["related to"])   
        
    pprint.pprint(relation_dictionary["feeling"])
    provenances = get_provenances(relation_dictionary, memstore.sources)
    result = MemStoreQueryResult(query[0], result_set, query)
    result.populate_dictionaries_exp(provenances, relation_dictionary)
    result.generate_visualisations_exp(relation_dictionary)
    ent_base = os.path.join(paths.EXPRESSION_SET_PATH_EXPERIMENTAL,'ent_net')
    result.visualization_dictionary['STMTS'].write_png(ent_base+'.png',\
                                                       prog=result.visualization_parameters['PROG'])
    #import pprint
    #pprint.pprint(sorted(relation_dictionary["cult"]["close to"], key=lambda x: x[1]))
    
def png_query():
    QUERY = ["feel", "feeling"]
    res_set = FuzzySet()
    with gzip.open(os.path.join(paths.EXPRESSION_SET_PATH_EXPERIMENTAL, "expressionsets.tsv.gz"), "rb") as f:
        lines = f.read().decode()
         
        # format: <expression> [(<expression2>, weight), <expression3>, weight), ...]
        tuid2relt = load_tuid2relt(lines)
        for term in QUERY:
            print(tuid2relt["feeling"])
            res_set = res_set | FuzzySet([x for x in tuid2relt[term]])
        # MISSING: the searcher stuff to find similar stuff
        # example: "feel" -> "felt" etc
    f.close()
    print(QUERY[0])
    result = MemStoreQueryResult(QUERY[0], res_set, QUERY)
    result.populate_dictionaries()
    result.generate_visualisations()
    ent_base = os.path.join(paths.EXPRESSION_SET_PATH_EXPERIMENTAL,'ent_net')
    print("QUERY RES:",result)
    print("VIS DICT", result.visualization_dictionary)
    print("ENT BASE", ent_base)
     
    #==========================================================================
    # from networkx.drawing.nx_pydot import from_pydot
    # G = from_pydot(result.visualization_dictionary['STMTS'])
    # import matplotlib.pyplot as plt
    # import networkx as nx
    # nx.draw_circular(G)
    # plt.show()
    #==========================================================================
     
    from io import BytesIO
     
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg
    png_str = result.visualization_dictionary["STMTS"].create_png(prog="dot")
    sio = BytesIO()
    sio.write(png_str)
    sio.seek(0)
    img = mpimg.imread(sio)
     
    # plot the image
    imgplot = plt.imshow(img, aspect='equal')
    #plt.show(block=False)
     
    result.visualization_dictionary['STMTS'].write_png(ent_base+'.png',\
    prog=result.visualization_parameters['PROG'])
    print(result.pretty_print())
    
if __name__ == "__main__":
    #experimental_query(["feel", "feeling"])
    png_query()
 
    
"""
NOTES:
def generate_prvhtm(self,usrn,maxa,terms): in svr_gt makes minimal paragraph examples
his system supports multiple query terms, but it doesnt get them from the form


"""