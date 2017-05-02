from _collections import defaultdict

def generate_relation_provenance_weights(sources):
    """
    Generates the mapping of relation tuples to provenance with closeness
    therein.
    """
    
    dictionary = defaultdict(lambda: list())
    for (token, relation, token2, provenance), closeness in sources.items():
        dictionary[(token, relation, token2)].append((provenance, closeness))
    return dictionary

def generate_relation_to_provenances(sources: "suids", 
                                     relation2prov: "suid2puid", 
                                     out_file=None):
    pass