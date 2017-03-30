import gzip
import os
from util import paths
from query.fuzzyset import FuzzySet
from query.termsets import load_tuid2relt
from query.memstorequeryresult import MemStoreQueryResult

if __name__ == "__main__":
    QUERY = ["cthulhu", "cult"]
    res_set = FuzzySet()
    with gzip.open(os.path.join(paths.EXPRESSION_SET_PATH_EXPERIMENTAL, "expressionsets.tsv.gz"), "rb") as f:
        lines = f.read().decode()
        tuid2relt = load_tuid2relt(lines)
        for term in QUERY:
            res_set = res_set | FuzzySet([x for x in tuid2relt[term]])
        # MISSING: the searcher stuff to find similar stuff
        # example: "feel" -> "felt" etc
    f.close()
    
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
    
"""
NOTES:
def generate_prvhtm(self,usrn,maxa,terms): in svr_gt makes minimal paragraph examples
his system supports multiple query terms, but it doesnt get them from the form


"""