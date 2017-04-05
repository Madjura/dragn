from util import paths
from index.fulltext import load_suids, gen_cooc_suid2puid_exp,\
    gen_sim_suid2puid_exp
import os, gzip
from knowledge_base.neomemstore import NeoMemStore
from _collections import defaultdict


def index_step():
    memstore = NeoMemStore()
    memstore.import_memstore(paths.MEMSTORE_PATH_EXPERIMENTAL)
    i = 0
    suid_lines = []
    expression_dictionary = defaultdict(lambda: set())
     
    #
    # WRITE EXPRESSION AND HOW THEY ARE RELATED AS SUIDS
    #
    ### original loads corpus with load_corpus, possibly needed
    for (expression, related_to, other_expression), weight in list(memstore.corpus.items()):
        suid_lines.append("\t".join([str(x) for x in [i, expression, related_to, other_expression, weight]]))
        i += 1
        expression_dictionary[expression].add((other_expression, weight))
        expression_dictionary[other_expression].add((expression, weight))
    with gzip.open(os.path.join(paths.SUIDS_PATH_EXPERIMENTAL, "suids.tsv.gz"), "wb") as f:
        f.write("\n".join(suid_lines).encode())
    f.close()
     
    #
    # WRITE EXPRESSION SET
    #
    ### equivalent: termsets
    term_lines = []
    for expression1, related_set in list(expression_dictionary.items()):
        for expression2, weight in related_set:
            term_lines.append("\t".join([str(x) for x in [expression1, expression2, weight]]))
    with gzip.open(os.path.join(paths.EXPRESSION_SET_PATH_EXPERIMENTAL, "expressionsets.tsv.gz"), "wb") as f:
        f.write(("\n".join(term_lines)).encode())
    f.close()
     
    suids = load_suids(paths.SUIDS_PATH_EXPERIMENTAL + "/suids.tsv.gz")
    suid2puid = gen_cooc_suid2puid_exp(memstore.sources, suids) # TODO: RENAME
    lines = []
    with gzip.open(os.path.join(paths.INDEX_PATH_EXPERIMENTAL, "provenances.tsv.gz"), "wb") as f_out:
        for suid in suid2puid:
            for puid, w in suid2puid[suid]:
                lines.append("\t".join( [str(suid), str(puid), str(w)] ))
        f_out.write(("\n".join(lines)).encode())
        _missing, _processed, _out = gen_sim_suid2puid_exp(suids, suid2puid, out_file=f_out)
        print(_missing, _processed)
    f_out.close()
    ### out:  '8033\ta.txt_14\t0.19269787540304012',
    ### suids:  ('young_man', 'related to', 'time_strength_sowing_wild_oat'): (24355, 0.4987936888425189),
    ### suid2puid: 29465: [('a.txt_13', 1.0)], <--- irrelevant it seems
    ### TODO: map suid_lines to provenance, see below gen_cooc_suid2puid

if __name__ == "__main__":
    index_step()