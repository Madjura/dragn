import gzip
from util import paths
import os
from ast import literal_eval
from _collections import defaultdict
from query.fuzzyset import FuzzySet
from itertools import combinations
from graph.node import CytoNode
from graph.edge import Edge
from graph.graph import Graph
from math import log

class QueryResult(object):
    """
    Wrapper over the processed text files to produce a graph in JSON
    format that can be displayed to the user.
    """
    
    def load_relations(self, 
                       path=os.path.join(
                           paths.RELATIONS_WITH_PROVENANCES_PATH, 
                           "relations_w_provenances.tsv.gz")):
        """
        Loads all the relation statements from the processed texts.
        The relation statements are format:
            ( (token, relation, token2), provenance, weight )
        
            Args:
                path: Optional. Default: paths.RELATIONS_WITH_PROVENANCES_PATH.
                    The path to the file of relation statements, as created
                    in index_step.
            Returns:
                A list of relation statement tuples, with provenance and
                weight.
        """
        
        #======================================================================
        # relations = defaultdict(lambda: [])
        #  
        # with gzip.open(path, "rb") as f:
        #     for line in f.read().decode().split("\n"):
        #         line_split = line.split("\t")
        #         try:
        #             relation_tuple = literal_eval(line_split[0])
        #         except SyntaxError:
        #             # in case of invalid format, stop
        #             break
        #         token, _, token2 = relation_tuple
        #         provenance = line_split[1]
        #         weight = float(line_split[2])
        #         relations[token].append( (relation_tuple, provenance, weight) )
        #         relations[token2].append( (relation_tuple, provenance, weight) )
        # print(len(relations))
        # return relations
        #======================================================================
    
    
        relations = []
        with gzip.open(path, "rb") as f:
            for line in f.read().decode().split("\n"):
                line_split = line.split("\t")
                try:
                    relation_tuple = literal_eval(line_split[0])
                except SyntaxError:
                    # in case of invalid format, stop
                    break
                provenance, weight = literal_eval(line_split[1])
                relations.append((relation_tuple, provenance, weight))
        return relations
    
    def load_relation2prov(self,
                         path=os.path.join(
                             paths.RELATION_PROVENANCES_PATH,
                             "provenances.tsv.gz")):
        """
        Loads the mapping of relation tuples to the provenances.
        The format is:
            (token, related_to, token2): [ (provenance, weight), ...]
        
            Args:
                path: Optional. Default: paths.RELATION_PROVENANCES_PATH.
                    The path to the file of tuple -> provennces mapping, as
                    created in index_step.
            Returns:
                A dictionary of relation tuple -> provenance mappings.
        """
        
        relation2prov = defaultdict(lambda: list())
        with gzip.open(path, "r") as f:
            for line in f.read().decode().split("\n"):
                line_split = line.split("\t")
                try:
                    # (token, related_to, token2)
                    relation_tuple = literal_eval(line_split[0])
                except SyntaxError:
                    break
                # (provenance, weight)
                provenances = literal_eval(line_split[1])
                relation2prov[relation_tuple].append(provenances)
        return relation2prov
    
    def prepare_for_query(self, query):
        query_relevant = FuzzySet()
        for term in query:
            query_relevant = query_relevant | FuzzySet([x for x in self.relation_sets[term]])
        return query_relevant
    
    def filter_relevant(self, relevant: FuzzySet):
        """
        Filters the relation tuples by the min_weight specified.
        Relation tuples that are below the specified value will be excluded
        from the result.
            
            Args:
                relevant: A FuzzySet containing the (token, weight) tuples
                    for the query terms.
            Returns:
                A FuzzySet with the values that were below the min_weight
                threshhold.
        """
        
        relevant_cut = FuzzySet()
        for token in relevant.cut(self.min_weight):
            relevant_cut[token] = relevant[token]
        return relevant_cut
    
    def load_relation_sets(self,
                             path=paths.EXPRESSION_SET_PATH_EXPERIMENTAL):
        """
        Loads the processed relationsets from index_step.
        Returns a dictionary mapping tokens to a list of tuples in the format:
            token: [ (token2, weight), ... ]
        This dictionary can be used to access the tokens that are related to
        another token by accessing the dictionary by key.
        """
        
        relations = defaultdict(lambda: list())
        with gzip.open(
            os.path.join(path, "relationsets.tsv.gz"), "rb") as f:
            lines = f.read().decode()
            for line in lines.split("\n"):
                line_split = line.split("\t")
                key = line_split[0]
                value = (line_split[1], float(line_split[2]))
                relations[key].append(value)
        return relations
    
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
        
        # iterate over the tokens relevant to the query
        for original_token in self.relevant_cut:
            relation_weight = self.relevant_cut[original_token]
            for relation_tuple in self.tuid2suid[original_token]:
                (token, related_to, token2), suid_weight = relation_tuple
                if not (token in self.queried or token2 in self.queried):
                    continue
                self.suid_dict[(token, related_to, token2)] += relation_weight * suid_weight
                self.tuid_dict[original_token] += relation_weight * suid_weight
                if token != original_token:
                    self.tuid_dict[token] += relation_weight * suid_weight
                if token2 != original_token:
                    self.tuid_dict[token2] += relation_weight * suid_weight
                
                p = self.relation2prov[(token, related_to, token2)]
                for prov_tuple in p:
                    for provenance, prov_weight in prov_tuple:
                        self.puid_dict[provenance] += relation_weight * suid_weight * prov_weight
                    for (prov1, w1), (prov2, w2) in combinations(self.relation2prov[(token, related_to, token2)], 2):
                        w = relation_weight * suid_weight * (w1 + w2) / 2
                        self.prov_rels[(prov2, prov1)] += w
        self.suid_set = self.generate_fuzzy_set(self.suid_dict)
        print("SUID DICT LENGTH OLD: ", len(self.suid_dict))
        print("SUID SET LENGTH OLD: ", len(self.suid_set))
        self.puid_set = self.generate_fuzzy_set(self.puid_dict)
        print("PUID DICT LENGTH OLD: ", len(self.puid_dict))
        print("PUID SET LENGTH OLD: ", len(self.puid_set))
    
    def generate_statement_nodes(self, max_nodes):
        token_list = list(self.tuid_dict.items())
        token_list.sort(key=lambda x: x[1], reverse=True)
        tokens = [x[0] for x in token_list[:max_nodes]]
        token_weight = dict([(x, self.tuid_dict[x]) for x in tokens])
        norm = 1.0
        graph_nodes = {}
        if token_weight:
            norm = min(token_weight.values())
        for token in token_weight:
            token_weight[token] /= norm
        for token in tokens:
            node_width = log(self.visualization_parameters["node width"] * token_weight[token], 10)
            if node_width < 0.4:
                node_width = 0.4
            font_size = int(24 * node_width)
            node_color = self.visualization_parameters["node color"]
            if token in self.queried:
                node_color = "green"
            graph_nodes[token] = CytoNode(name=token, color=node_color,
                                         width=node_width, label_size=font_size)
        return graph_nodes
    
    def generate_statement_graph(self, max_nodes, max_edges):
        nodes = self.generate_statement_nodes(max_nodes)
        token_list = list(self.suid_set.items())
        edge_count = 0
        token_list.sort(key=lambda x: x[1], reverse=True)
        for relation_tuple, _ in token_list:
            if edge_count >= max_edges:
                break
            token, related_to, token2 = relation_tuple
            if token in nodes and token2 in nodes:
                if related_to in self.visualization_parameters["edge color"]:
                    edge_color = self.visualization_parameters["edge color"][related_to]
                graph_edge = Edge(nodes[token], nodes[token2], color=edge_color)
                nodes[token].add_edge_object(graph_edge)
        print("RETURNING GRAPH")
        return Graph(nodes.values())
    
    def load_token2related(self):
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
        print("LEN tuid2suid ", len(tuid2suid))
        return tuid2suid
    
    def load_parameters(self):
        """
        Returns a dictionary of visualization parameters used for the graph.
        """
        
        parameters = {
            "node width": 0.25,
            "node color": "#6699CC",
            "max label length": 50,
            "edge color": {
                "related to": "red",
                "close to": "blue"
                }
            }
        return parameters
    
    def __init__(self, queried=None, min_weight=0.5):
        self.relations = self.load_relations()
        self.relation2prov = self.load_relation2prov()
        self.relation_sets = self.load_relation_sets()
        self.queried = queried
        self.suid_dict = defaultdict(int)  # statement -> overall combined relevance weight
        self.tuid_dict = defaultdict(int)
        self.puid_dict = defaultdict(int)  # provenance -> overall combined relevance weight
        self.prov_rels = defaultdict(float)
        self.suid_set = FuzzySet()  # fuzzy statement ID set
        self.puid_set = FuzzySet()  # fuzzy provenance ID set
        
        # minimum weight that relations must have to be considered
        self.min_weight = min_weight
        self.relevant_cut = self.filter_relevant(self.prepare_for_query(queried))
        self.tuid2suid = self.load_token2related()
        self.visualization_parameters = self.load_parameters()
        
if __name__ == "__main__":
    foo = QueryResult(["ron", "dumbledore"])
    foo.populate_dictionaries()
    foo.generate_statement_graph(50, 100)