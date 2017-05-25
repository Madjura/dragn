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
    for (subject, predicate, objecT), weight in sources.items():
        relations[subject].add( (predicate, objecT))
        if predicate == "related to":
            related_statements.append( ((subject, predicate, objecT), weight) )
    for (subject, predicate, objecT), weight in related_statements:
        combined_relations = relations[subject] & relations[objecT]
        prov2weight = defaultdict(lambda: list())
        for related_relation, related in combined_relations:
            relation_tuple1 = (subject, related_relation, related)
            relation_tuple2 = (objecT, related_relation, related)
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
                # other: ('obscurity', 'close to', 'ancient_inscription')    [('call_of_cthulhu.txt_3', 0.5)]
                # this: str: ('punch', 'related to', 'favorite_punching_bag')    [('harrypotter.txt_127', 0.3080712829341244)]
                line = "\t".join([str( (subject, predicate, objecT) ), 
                                   str( [(provenance, prov_weight)] ) ])
                out_file.write(str.encode(line))
                out_file.write(str.encode("\n"))
            processed += 1
    return missing, processed