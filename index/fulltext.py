import gzip
from _collections import defaultdict

def gen_cooc_suid2puid_exp(sources, stmt2suid):
    ### maps expression, p, other_expression, prevnance to pargraph, weight
    ### through this, can access expression, p, other_expression paragraph and their weight there
    
    ### sources: dict: {('make', 'close to', 'stream', 'a.txt_21'): 0.8333333333333333,
    ### stmt2suid:  6    startle    close to    destine    0.26632781872686007
    dictionary = defaultdict(lambda:list())
    for expression, p, other_expression, provenance in sources:
        # this is the closeness.closeness value
        closeness = sources[(expression, p, other_expression, provenance)]
        try:
            suid = stmt2suid[(expression, p, other_expression)][0]
        except KeyError:
            suid = None
            print("ERROR FOR : ", expression, p , other_expression)
        dictionary[suid].append((provenance, closeness))
    return dictionary

def gen_sim_suid2puid_exp(suids, suid2puid, out_file=None):
    # process the suids, creating the dictionary mapping subjects to 
    # (related_to,object_) tuples, and also generating a list of similarity
    # relationship statements together with their SUIDs and weights
    print("  - building the auxiliary dictionaries")
    s2po = defaultdict(lambda: set())
    sim_stmts = {}
    for expression, related_to, object_ in suids:
        s2po[expression].add( (related_to, object_) )
        if related_to == "related to":
            sim_stmts[ (expression, object_) ] = suids[ (expression, "related to", object_ )]
            #a = suids[(expression, "related to", object_)]
    # process all the similarity statements, determining the co-occurrence
    # statements that led to them as an intersection of the (related_to,object_)
    # tuple sets corresponding to the similar arguments
    print("  - processing the similarity statements")
    missing = 0
    processed = 0
    i = 0
    for expression, object_ in sim_stmts:
        i += 1
        print("    ...", i, "out of", len(sim_stmts))
        # sim_w is relation tuple, sim_w is just the weight
        sim_suid, sim_w = sim_stmts[ (expression, object_ )]
        puid2weight = defaultdict(lambda: list())
        # processing the shared statements
        combined = s2po[expression] & s2po[object_]
        if combined:
            print("foo")
        for p_prov, o_prov in s2po[expression] & s2po[object_]:
            _foo = s2po[expression]
            _foo2 = s2po[object_]
            prov_suid1 = suids[(expression, p_prov, o_prov)][0]
            prov_suid2 = suids[(object_, p_prov, o_prov)][0]
            l = []
            if prov_suid1 in suid2puid:
                l += suid2puid[prov_suid1]
            if prov_suid2 in suid2puid:
                l += suid2puid[prov_suid2]
            
            # oh my god he uses extend above
            # holy shit why
            for puid, w in l:
                puid2weight[puid].append(w)
        if not len(puid2weight):
            missing += 1
        for puid in puid2weight:
            # computing the actual provenance weight as a product of the maximum
            # provenance weight of related co-occurrence statement and the similarity
            # value
            prov_w = max(puid2weight[puid]) * sim_w
            
            # writing the provenance line to the out-file
            if out_file is not None:
                line = "\n" + "\t".join([str(sim_suid), puid, str(prov_w)])
                out_file.write(str.encode(line))
            processed += 1
    return missing, processed

def load_suids(fname):
    # load the mapping of the statements to their IDs
    dct = {}
    
    with (gzip.open(fname, "r")) as suids:
        lines = suids.read().decode().split('\n')
        for line in lines:
            spl = line.split('\t')
            if len(spl) != 5:
                continue
            dct[(spl[1],spl[2],spl[3])] = ((spl[0]), float(spl[4]))
    suids.close()
    return dct
