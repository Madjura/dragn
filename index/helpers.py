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
    related_statements = []
    relations = defaultdict(lambda: set())
    missing = 0
    processed = 0
    
    
    for (token, related_to, token2), weight in sources.items():
        relations[token].add( (related_to, token2))
        if related_to == "related to":
            related_statements.append( ((token, related_to, token2), weight) )
    for (token, related_to, token2), weight in related_statements:
        combined_relations = relations[token] & relations[token2]
        prov2weight = defaultdict(lambda: list())
        for related_relation, related_token in combined_relations:
            relation_tuple1 = (token, related_relation, related_token)
            relation_tuple2 = (token2, related_relation, related_token)
            tmp = []
            if relation_tuple1 in relation2prov:
                tmp.extend(relation2prov[relation_tuple1])
            if relation_tuple2 in relation2prov:
                tmp.extend(relation2prov[relation_tuple2])
            for prov_tuple in tmp:
                provenance, provenance_weight = prov_tuple
                prov2weight[provenance].append(provenance_weight)
        if not prov2weight:
            missing += 1
        for provenance in prov2weight:
            prov_weight = max(prov2weight[provenance]) * weight
            if out_file is not None:
                line = "\t".join([str( (token, related_to, token2) ), 
                                   str( (provenance, prov_weight) ) ])
                out_file.write(str.encode(line))
                out_file.write(str.encode("\n"))
            processed += 1
    return missing, processed