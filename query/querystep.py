import gzip
import os
from util import paths
from query.fuzzyset import FuzzySet
from query.termsets import load_tuid2relt
from query.memstorequeryresult import MemStoreQueryResult

if __name__ == "__main__":
    QUERY = "night"
    res_set = FuzzySet()
    with gzip.open(os.path.join(paths.EXPRESSION_SET_PATH_EXPERIMENTAL, "expressionsets.tsv.gz"), "rb") as f:
        lines = f.read().decode()
        tuid2relt = load_tuid2relt(lines)
        res_set = res_set | FuzzySet([x for x in tuid2relt[QUERY]])
        # MISSING: the searcher stuff to find similar stuff
        # example: "feel" -> "felt" etc
    f.close()
    
    result = MemStoreQueryResult(QUERY, res_set, QUERY)
    result.populate_dictionaries()
    result.generate_visualisations()
    ent_base = os.path.join(paths.EXPRESSION_SET_PATH_EXPERIMENTAL,'ent_net')
    print("QUERY RES:",result)
    print("VIS DICT", result.visualization_dictionary)
    print("ENT BASE", ent_base)
    result.visualization_dictionary['STMTS'].write_png(ent_base+'.png',\
    prog=result.visualization_parameters['PROG'])
    print(result.pretty_print())
    
"""
NOTES:
def generate_prvhtm(self,usrn,maxa,terms): in svr_gt makes minimal paragraph examples
his system supports multiple query terms, but it doesnt get them from the form


"""