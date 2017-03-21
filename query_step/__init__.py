import gzip
import os
from util import paths
from query_step.fuzzyset import FuzzySet
from query_step.termsets import load_tuid2relt
import pprint
from query_step.memstorequeryresult import MemStoreQueryResult

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
    
    print(res_set["feel"])
    print(tuid2relt["feel"])
    
    result = MemStoreQueryResult(QUERY, res_set, QUERY)
    result.populate_dictionaries()
    result.generate_visualisations(tuid2relt)
    ent_base = os.path.join(paths.EXPRESSION_SET_PATH_EXPERIMENTAL,'ent_net')
    print("QUERY RES:",result)
    print("VIS DICT", result.vis_dict)
    print("ENT BASE", ent_base)
    result.vis_dict['STMTS'].write_png(ent_base+'.png',\
    prog=result.vis_par['PROG'])