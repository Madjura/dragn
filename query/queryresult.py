import gzip
from util import paths
import os
from ast import literal_eval
from _collections import defaultdict
from query.fuzzyset import FuzzySet
from itertools import combinations

class QueryResult(object):
    
    def load_relations(self, 
                       path=os.path.join(
                           paths.RELATIONS_WITH_PROVENANCES_PATH, 
                           "relations_w_provenances.tsv.gz")):
        relations = []
        with gzip.open(path, "rb") as f:
            for line in f.read().decode().split("\n"):
                line_split = line.split("\t")
                try:
                    relation_tuple = literal_eval(line_split[0])
                except SyntaxError:
                    break
                provenance = line_split[1]
                weight = float(line_split[2])
                relations.append((relation_tuple, provenance, weight))
        return relations
    
    def load_relation2prov(self,
                         path=os.path.join(
                             paths.RELATION_PROVENANCES_PATH,
                             "provenances.tsv.gz")):
        relation2prov = defaultdict(lambda: list())
        with gzip.open(path, "r") as f:
            for line in f.read().decode().split("\n"):
                line_split = line.split("\t")
                try:
                    relation_tuple = literal_eval(line_split[0])
                except SyntaxError:
                    break
                provenances = literal_eval(line_split[1])
                relation2prov[relation_tuple].append(provenances)
        return relation2prov
    
    def prepare_for_query(self, query):
        query_relevant = FuzzySet()
        for term in query:
            query_relevant = query_relevant | FuzzySet([x for x in self.expressionsets[term]])
        for a, b in query_relevant.items():
            print(a, b)
        return query_relevant
    
    def filter_relevant(self, relevant):
        relevant_cut = FuzzySet()
        for token in relevant.cut(self.min_weight):
            relevant_cut[token] = relevant[token]
        return relevant_cut
    
    def load_expression_set(self):
        tuid2relt = defaultdict(lambda: list())
        with gzip.open(
            os.path.join(paths.EXPRESSION_SET_PATH_EXPERIMENTAL, 
                         "relationsets.tsv.gz"), "rb") as f:
            lines = f.read().decode()
            for line in lines.split('\n'):
                spl = line.split('\t')
                if len(spl) != 3:
                    continue
                key = spl[0]
                value = (spl[1], float(spl[2]))
                tuid2relt[key].append(value)
        return tuid2relt
    
    def generate_fuzzy_set(self, dct, agg=max):
        # generates a fuzzy set from a member->weight dictionary, normalising the
        # weight values first by a constant computed by the supplied agg function
        # from the dictionary values (maximum by default)

        fset = FuzzySet()
        if len(dct) == 0:
            return fset
        norm_const = agg(list(dct.values()))
        if norm_const <= 0:
            # making sure it's OK to divide by it meaningfully
            norm_const = 1.0
        for member, weight in list(dct.items()):
            # cutting off the values out of [0,1] interval
            w = float(weight) / norm_const
            if w > 1:
                w = 1
            if w < 0:
                w = 0
            fset[member] = w
        return fset
    
    def populate_dictionaries(self):
        for original_token in self.relevant_cut:
            tuid_weight = self.relevant_cut[original_token]
            for relation_tuple in self.tuid2suid[original_token]:
                (token, related_to, token2), suid_weight = relation_tuple
                if not (token in self.queried or token2 in self.queried):
                    continue
                self.suid_dict[(token, related_to, token2)] += tuid_weight * suid_weight
                self.tuid_dict[original_token] += tuid_weight * suid_weight
                if token != original_token:
                    self.tuid_dict[token] += tuid_weight * suid_weight
                if token2 != original_token:
                    self.tuid_dict[token2] += tuid_weight * suid_weight
                
                p = self.relation2prov[(token, related_to, token2)]
                for prov_tuple in p:
                    for provenance, prov_weight in prov_tuple:
                        self.puid_dict[provenance] += tuid_weight * suid_weight * prov_weight
                    for (prov1, w1), (prov2, w2) in combinations(self.relation2prov[(token, related_to, token2)], 2):
                        w = tuid_weight * suid_weight * (w1 + w2) / 2
                        self.prov_rels[(prov2, prov1)] += w
        self.suid_set = self.generate_fuzzy_set(self.suid_dict)
        print("SUID DICT LENGTH OLD: ", len(self.suid_dict))
        print("SUID SET LENGTH OLD: ", len(self.suid_set))
        self.puid_set = self.generate_fuzzy_set(self.puid_dict)
        print("PUID DICT LENGTH OLD: ", len(self.puid_dict))
        print("PUID SET LENGTH OLD: ", len(self.puid_set))
                
    def load_suid2stmt(self):
        tuid2suid = {}
        path = os.path.join(paths.RELATIONS_PATH, "relations.tsv.gz")
        with gzip.open(path, "rb") as f:
            for line in f.read().decode().split("\n"):
                spl = line.split("\t")
                try:
                    relation_tuple = literal_eval(spl[0])
                except SyntaxError:
                    break
                weight = float(spl[1])
   
                # updating the term ID -> statement ID mapping record for the subject
                if not relation_tuple[0] in tuid2suid:
                    tuid2suid[relation_tuple[0]] = []
                tuid2suid[relation_tuple[0]].append((relation_tuple, weight))
                # updating the term ID -> statement ID mapping record for the object
                if not relation_tuple[2] in tuid2suid:
                    tuid2suid[relation_tuple[2]] = []
                tuid2suid[relation_tuple[2]].append((relation_tuple, weight))
            f.close()
        return tuid2suid
    
    def __init__(self, queried=None, min_weight=0.5):
        self.relations = self.load_relations()
        self.relation2prov = self.load_relation2prov()
        self.expressionsets = self.load_expression_set()
        self.queried = queried
        self.suid_dict = defaultdict(int)  # statement -> overall combined relevance weight
        self.tuid_dict = defaultdict(int)
        self.puid_dict = defaultdict(int)  # provenance -> overall combined relevance weight
        self.prov_rels = defaultdict(float)
        self.suid_set = FuzzySet()  # fuzzy statement ID set
        self.puid_set = FuzzySet()  # fuzzy provenance ID set
        self.min_weight = min_weight
        self.relevant_cut = self.filter_relevant(self.prepare_for_query(queried))
        self.tuid2suid = self.load_suid2stmt()
        
if __name__ == "__main__":
    foo = QueryResult(["ron", "dumbledore"])
    foo.populate_dictionaries()