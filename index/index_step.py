import pickle
from util import paths
from index.fulltext import open_index, update_index, gen_cooc_suid2puid,\
    gen_sim_suid2puid, load_suids
import os, gzip
from knowledge_base.memstore import MemStore

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