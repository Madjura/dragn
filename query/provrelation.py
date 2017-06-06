class ProvRelation(object):
    def __init__(self, provenance, prov_weight, relation_triple):
        self.provenance = provenance
        self.prov_weight = prov_weight
        self.subject, self.predicate, self.objecT = relation_triple