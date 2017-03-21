from util import paths
from index.fulltext import open_index, update_index, gen_cooc_suid2puid,\
    gen_sim_suid2puid, load_suids, update_index_exp, gen_cooc_suid2puid_exp,\
    gen_sim_suid2puid_exp
import os, gzip
from knowledge_base.memstore import MemStore
from knowledge_base.neomemstore import NeoMemStore
from _collections import defaultdict

memstore = NeoMemStore()
memstore.import_memstore(paths.MEMSTORE_PATH_EXPERIMENTAL)
ftext = open_index(paths.FULLTEXT_PATH_EXPERIMENTAL)
expressions = memstore.lexicon.keys() ### get all expressions
update_index_exp(ftext, expressions) ### FULLTEXT IS WRITTEN HERE
i = 0
suid_lines = []
expression_dictionary = defaultdict(lambda: set())
 
#
# WRITE EXPRESSION AND HOW THEY ARE RELATED AS SUIDS
#
### original loads corpus with load_corpus, possibly needed
for (expression, related_to, other_expression), weight in list(memstore.corpus.items()):
    suid_lines.append("\t".join([str(x) for x in [i, expression, related_to, other_expression, weight]])) ### changed first expression from i
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
    ### example: 'mediterranean\ttouch\t0.825498509999548',
    ### example from old code, below: 'greasy_plush_collarbox\tupstairs_room\t0.8692487144265308',
f.close()
 
### pprint.pprint(expression_dictionary["door"])
suids = load_suids(paths.SUIDS_PATH_EXPERIMENTAL + "/suids.tsv.gz")
suid2puid = gen_cooc_suid2puid_exp(memstore.sources, suids) # TODO: RENAME
 
lines = []
with gzip.open(os.path.join(paths.INDEX_PATH_EXPERIMENTAL, "provenances.tsv.gz"), "wb") as f_out:
    for suid in suid2puid:
        for puid, w in suid2puid[suid]:
            lines.append("\t".join( [str(suid), str(puid), str(w)] ))
    f_out.write(("\n".join(lines)).encode())
    missing, processed, out = gen_sim_suid2puid_exp(suids, suid2puid, out_file=f_out)
f_out.close()
### out:  '8033\ta.txt_14\t0.19269787540304012',
### suids:  ('young_man', 'related to', 'time_strength_sowing_wild_oat'): (24355, 0.4987936888425189),
### suid2puid: 29465: [('a.txt_13', 1.0)], <--- irrelevant it seems
print("foo")
### TODO: map suid_lines to provenance, see below gen_cooc_suid2puid

# STEP 4
### CHANGED TO .p
#memstore = pickle.load(open(paths.MEMSTORE_PATH + "/" + "memstore_comp.p", "rb"))
memstore = MemStore(trace=True)
memstore.imp(paths.MEMSTORE_PATH)
ftext = open_index(paths.FULLTEXT_PATH)
text2index = {}
for text, index in list(memstore.lexicon.lex2int.items()):
    text2index[text] = str(index)

update_index(ftext,text2index)

i, suid_lines, term_dict = 0, [], {}
for (s,p,o), w in list(memstore.corpus.items()):
    suid_lines.append('\t'.join([str(x) for x in [i,s,p,o,w]]))
    i += 1
    # updating the TERM CSV dictionary
    if not s in term_dict:
        term_dict[s] = set()
    if not o in term_dict:
        term_dict[o] = set()
    term_dict[s].add((o,w))
    term_dict[o].add((s,w))
### i is for .csv files


### suid lines sometimes has related_to instead of close_to - problematic?
## write suid_lines to suids.tsv.gzip 
f = gzip.open(os.path.join(paths.SUIDS_PATH,'suids.tsv.gz'),'wb')
f.write(('\n'.join(suid_lines)).encode())
#f.write("foo".encode())
f.close()

term_lines = []
for t1, rel_set in list(term_dict.items()):
    for t2, w in rel_set:
        term_lines.append('\t'.join([str(x) for x in [t1,t2,w]]))
#f = gzip.open(os.path.join(index_path,'termsets.tsv.gz'),'wb')
## write term_lines to termsets.tsv.gz

### termlines example: 'greasy_plush_collarbox\tupstairs_room\t0.8692487144265308',

### CHANGES FORMAT
suid_lines = load_suids(paths.SUIDS_PATH + '/suids.tsv.gz')

## difference: <class 'list'>: [('properly_significant_of_contrite_spirit', 1.0)]
## has term instead of number, probably insignifacant
suid2puid = gen_cooc_suid2puid(memstore.sources, suid_lines)


lines = []
### holy fuck
### suid = STATEMENT UNIQUE ID
### puid = PROVENANCE UNIQUE ID
### suid2puid maps statement ID to provenance (= paragraph in document) ID
f_out = gzip.open(os.path.join(paths.INDEX_PATH,'provenances.tsv.gz'),'wb')
for suid in suid2puid:
    for puid, w in suid2puid[suid]:
        lines.append('\t'.join([str(suid),str(puid),str(w)]))
f_out.write(str.encode('\n'.join(lines)))
simrel_id = -1
try:
    simrel_id = memstore.lexicon["related to"]
except KeyError:
    print('\nW@ixkb.py - no similarity relationships present\n')
### THIS WRITES PROVENANCE FILE
### LOOKS CORRECT BUT SOMETIMES THE SPACING IS INCOSISTENT IN FILE, TODO: FIX
missing, processed, out = gen_sim_suid2puid(suid_lines,suid2puid,simrel_id, out_file=f_out)
print("OUT ", out)
print("PROCESSED ", processed)