import gzip
import os
import uuid
from util import paths
from query.fuzzyset import FuzzySet
from query.termsets import load_tuid2relt
from query.memstorequeryresult import MemStoreQueryResult


def query(query=[], queryname=None, max_nodes=25, max_edges=50):
    if not queryname:
        queryname = str(uuid.uuid4())
    if not query:
        return # empty query
    result_set = FuzzySet()
    with gzip.open(os.path.join(paths.EXPRESSION_SET_PATH_EXPERIMENTAL, "expressionsets.tsv.gz"), "rb") as f:
        lines = f.read().decode()
         
        # format: <expression> [(<expression2>, weight), <expression3>, weight), ...]
        tuid2relt = load_tuid2relt(lines)
        for term in query:
            result_set = result_set | FuzzySet([x for x in tuid2relt[term]])
    f.close()
    
    result = MemStoreQueryResult(queryname, result_set, query)
    result.populate_dictionaries()
    graph = result.generate_visualisations(max_n=max_nodes, max_e=max_edges)
    ent_base = os.path.join(paths.EXPRESSION_SET_PATH_EXPERIMENTAL, ",".join(x for x in query))
    result.visualization_dictionary['PROVS'].write_png(ent_base+'.png',\
                                                       prog=result.visualization_parameters['PROG'])
    return graph
    
def png_query():
    QUERY = ["feel", "feeling"]
    res_set = FuzzySet()
    with gzip.open(os.path.join(paths.EXPRESSION_SET_PATH_EXPERIMENTAL, "expressionsets.tsv.gz"), "rb") as f:
        lines = f.read().decode()
         
        # format: <expression> [(<expression2>, weight), <expression3>, weight), ...]
        tuid2relt = load_tuid2relt(lines)
        for term in QUERY:
            res_set = res_set | FuzzySet([x for x in tuid2relt[term]])
        # MISSING: the searcher stuff to find similar stuff
        # example: "feel" -> "felt" etc
    f.close()
    result = MemStoreQueryResult(QUERY[0], res_set, QUERY)
    result.populate_dictionaries()
    result.generate_visualisations()
    ent_base = os.path.join(paths.EXPRESSION_SET_PATH_EXPERIMENTAL,'ent_netOLD')
    result.visualization_dictionary['PROVS'].write_png(ent_base+'.png',\
                                                       prog=result.visualization_parameters['PROG'])
    #print(result.pretty_print())

    
if __name__ == "__main__":
    #png_query()
    query(["ron", "dumbledore"])
    
"""
NOTES:
def generate_prvhtm(self,usrn,maxa,terms): in svr_gt makes minimal paragraph examples
his system supports multiple query terms, but it doesnt get them from the form

april 10:
res_set is the same in both

"""