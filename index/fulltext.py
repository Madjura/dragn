from whoosh.fields import Schema, ID, TEXT
from whoosh.analysis.analyzers import StemmingAnalyzer
import sys, gzip
from whoosh.index import create_in, open_dir

def open_index(path):
    # creating and/or opening the fulltext index
    schema = Schema(\
                    identifier=ID(stored=True),\
                    content=TEXT(analyzer=StemmingAnalyzer())\
    )
    _ix = None
    try:
        # trying to create index if fresh
        _ix = create_in(path,schema)
    except:
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        print(exceptionType)
        print(exceptionValue)
        print(exceptionTraceback)
    # opening and returning the index
    _ix = open_dir(path)
    return _ix

def update_index(ix,text2index):
    # updating index using a dictionary of text keys mapped to their identifiers
    writer = ix.writer()
    for text, index in list(text2index.items()):
        try:
            writer.add_document(identifier=str(index),content=str(text))
        except UnicodeDecodeError:
            sys.stderr.write('\nW @ update_index(): unicode problems, skipping\n'+\
                             '  problematic text: '+text+'\n')
    writer.commit()
    
def gen_cooc_suid2puid(sources,stmt2suid):
    # generating the mapping from extracted statements to provenances and their
    # weights
    dct = {}
    for s, p, o, prov in sources:
        w = sources[(s,p,o,prov)]
        
        try:
            suid = stmt2suid[(s,p,o)][0]
        except KeyError:
            suid = None # TODO: handling
        if not suid in dct:
            dct[suid] = []
        dct[suid].append((prov,w))
    return dct

def gen_sim_suid2puid(stmt2suid,suid2puid,simrel_id):
    # process the stmt2suid, creating the dictionary mapping subjects to 
    # (predicate,object) tuples, and also generating a list of similarity
    # relationship statements together with their SUIDs and weights
    print("  - building the auxiliary dictionaries")
    s2po, sim_stmts = {}, {}
    for s,p,o in stmt2suid:
        if not s in s2po:
            s2po[s] = set()
        s2po[s].add((p,o))
        if p == simrel_id:
            sim_stmts[(s,o)] = stmt2suid[(s,p,o)]
    # process all the similarity statements, determining the co-occurrence
    # statements that led to them as an intersection of the (predicate,object)
    # tuple sets corresponding to the similar arguments
    print("  - processing the similarity statements")
    i, missing, processed = 0, 0, 0
    for s, o in sim_stmts:
        i += 1
        print("    ...", i, "out of", len(sim_stmts))
        sim_suid, sim_w = sim_stmts[(s,o)]
        puid2weight = {}
        # processing the shared statements
        for p_prov, o_prov in s2po[s] & s2po[o]:
            prov_suid1 = stmt2suid[(s, p_prov, o_prov)][0]
            prov_suid2 = stmt2suid[(o, p_prov, o_prov)][0]
            l = []
            if prov_suid1 in suid2puid:
                l += suid2puid[prov_suid1]
            if prov_suid2 in suid2puid:
                l += suid2puid[prov_suid2]
            for puid, w in l:
                if not puid in puid2weight:
                    puid2weight[puid] = []
                puid2weight[puid].append(w)
        if not len(puid2weight):
            missing += 1
        for puid in puid2weight:
            # computing the actual provenance weight as a product of the maximum
            # provenance weight of related co-occurrence statement and the similarity
            # value
            prov_w = max(puid2weight[puid])*sim_w
            # writing the provenance line to the out-file
            #f_out.write('\n'.encode())
            #f_out.write('\t'.join([str(sim_suid),str(puid),str(prov_w)]).encode())
            print("sim_suid: ", sim_suid, " puid: ", puid, " prov_w: ", prov_w)
            processed += 1
    return missing, processed

def load_suids(fname):
    # load the mapping of the statements to their IDs
    dct = {}
    lines = gzip.open(fname,'r').read().decode().split('\n')
    for line in lines:
        spl = line.split('\t')
        if len(spl) != 5:
            continue
        dct[(int(spl[1]),int(spl[2]),int(spl[3]))] = (int(spl[0]), float(spl[4]))
    return dct
