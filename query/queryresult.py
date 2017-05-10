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
                if not line:
                    continue
                line_split = line.split("\t")
                relation_tuple = literal_eval(line_split[0])
                provenances = literal_eval(line_split[1])
                relation2prov[relation_tuple].append(provenances)
        return relation2prov
    
    def prepare_for_query(self):
        """Returns a FuzzySet containing tokens relevant to the query."""
        
        relation_sets = self.load_relation_sets()
        #self.queried = [x for x in relation_sets.keys() if any(y in x for y in query)]
        query_relevant = FuzzySet()
        for term in self.queried:
            # x are tuples of (token2, weight)
            query_relevant = query_relevant | FuzzySet([x for x in relation_sets[term]])
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
                token, token2, weight = line_split
                relation_tuple = (token2, float(weight))
                relations[token].append(relation_tuple)
        return relations
    
    def generate_fuzzy_set(self, dictionary):
        """
        Generates a FuzzySet from a dictionary.
        CURRENTLY UNUSED. POSSIBLY USELESS.
        """
        
        fuzzy_set = FuzzySet()
        if len(dictionary) == 0:
            return fuzzy_set
        norm_const = max(list(dictionary.values()))
        if norm_const <= 0:
            norm_const = 1.0
        for member, weight in list(dictionary.items()):
            w = float(weight) / norm_const
            if w > 1:
                w = 1
            if w < 0:
                w = 0
            fuzzy_set[member] = w
        return fuzzy_set
    
    def populate_dictionaries(self):
        """
        Prepares the ranking of tokens / relations for use with the graph.
        """
        
        # { relation_tuple: [(provenance, weight), ...] }
        relation2prov = self.load_relation2prov()
        
        # { relation_tuple: calculated weight }
        # used to rank / limit the graph nodes by top values
        relation_dict = defaultdict(int)
        
        # { provenance: calculated weight }
        # indicates how "related" a provenance is to the query
        provenance_dict = defaultdict(int)
        
        # { (prov1, prov2): weight }
        # indicates how "related" two provenances are
        provenance_relations = defaultdict(float)
        
        # all relation tuples containing query terms, with weight above threshhold
        relevant_cut = self.filter_relevant(self.prepare_for_query())

        # iterate over the tokens relevant to the query
        for possibly_related in relevant_cut:
            
            # get all relation tuples in which "possibly_related" appears
            for relation_tuple in self.relations[possibly_related]:
                (token, related_to, token2), relation_weight = relation_tuple
                
                # find the relation tuples that contain "possibly_related" and
                # a term from the query
                if not (token in self.queried or token2 in self.queried):
                    # random relation that does not have any relevance to the query
                    continue
                
                # get the membership degree of "possibly related" to the query             
                """
                makes fuzzyset of all (token, weight) tuples 
                the tuples come from the dict with
                token: [(token2, weight), ...]
                then keeps only the ones with weight above threshhold
                from that it gets the value <--- membership
                keeps higher of close to / related to
                """
                membership = relevant_cut[possibly_related]
                calculated_relation_weight = membership * relation_weight
                relation_dict[(token, related_to, token2)] += calculated_relation_weight
                self.tokens2weights[possibly_related] += calculated_relation_weight
                if token != possibly_related:
                    self.tokens2weights[token] += calculated_relation_weight
                if token2 != possibly_related:
                    self.tokens2weights[token2] += calculated_relation_weight
                
                # UNUSED CURRENTLY
                for prov_tuple in relation2prov[(token, related_to, token2)]:
                    for provenance, prov_weight in prov_tuple:
                        provenance_dict[provenance] += membership * relation_weight * prov_weight
                    for (prov1, w1), (prov2, w2) in combinations(prov_tuple, 2):
                        w = membership * relation_weight * (w1 + w2) / 2
                        provenance_relations[(prov2, prov1)] += w
        #self.relation_set = self.generate_fuzzy_set(relation_dict)
        self.relation_set = relation_dict
        print("SUID DICT LENGTH OLD: ", len(relation_dict))
        print("SUID SET LENGTH OLD: ", len(self.relation_set))
        
        # UNUSED CURRENTLY
        self.provenance_set = self.generate_fuzzy_set(provenance_dict)
        print("PUID DICT LENGTH OLD: ", len(provenance_dict))
        print("PUID SET LENGTH OLD: ", len(self.provenance_set))
    
    def generate_statement_nodes(self, max_nodes):
        """
        Generates the nodes that exist in the query-graph.
            
            Args:
                max_nodes: The maximum number of nodes.
        """
        
        # get and sort the relevant tokens by weight
        token_list = list(self.tokens2weights.items())
        token_list.sort(key=lambda x: x[1], reverse=True)
        tokens = [x[0] for x in token_list[:max_nodes]]
        # weight for normalization
        token_weight = {x: self.tokens2weights[x] for x in tokens}
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
            graph_nodes[token] = CytoNode(name=token, 
                                          color=node_color,
                                          width=node_width,
                                          label_size=font_size)
        return graph_nodes
    
    def generate_statement_graph(self, max_nodes, max_edges):
        """
        Generates the graph object for the query.
        Only the top most relevant nodes and edges are in the graph.
        
            Args:
                max_nodes: The maximum number of nodes in the graph.
                max_edges: The maximum number of edges in the graph.
        """
        
        # get all the graph nodes
        nodes = self.generate_statement_nodes(max_nodes)
        token_list = list(self.relation_set.items())
        edge_count = 0
        token_list.sort(key=lambda x: x[1], reverse=True)
        for relation_tuple, _ in token_list:
            if edge_count >= max_edges:
                break
            token, related_to, token2 = relation_tuple
            if token in nodes and token2 in nodes:
                if related_to in self.visualization_parameters["edge color"]:
                    edge_color = self.visualization_parameters["edge color"][related_to]
                graph_edge = Edge(start=nodes[token], end=nodes[token2],
                                  color=edge_color)
                nodes[token].add_edge_object(graph_edge)
        print("RETURNING GRAPH")
        return Graph(nodes=nodes.values())
    
    def load_token2related(self):
        """Loads the mapping of tokens to the related tokens."""
        
        token2related = defaultdict(lambda: list())
        path = os.path.join(paths.RELATIONS_PATH, "relations.tsv.gz")
        with gzip.open(path, "rb") as f:
            for line in f.read().decode().split("\n"):
                spl = line.split("\t")
                try:
                    relation_tuple = literal_eval(spl[0])
                except SyntaxError:
                    continue
                weight = float(spl[1])
                token, _, token2 = relation_tuple
                token2related[token].append((relation_tuple, weight))
                token2related[token2].append((relation_tuple, weight))
            f.close()
        print("LEN relations ", len(token2related))
        return token2related
    
    def load_parameters(self):
        """
        Returns a dictionary of visualization parameters used for the graph.
        TODO: load from a config file or database
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
        self.queried = queried
        self.tokens2weights = defaultdict(int)
        self.relation_set = FuzzySet()
        self.provenance_set = FuzzySet()
        # minimum weight that relations must have to be considered
        self.min_weight = min_weight
        self.relations = self.load_token2related()
        self.visualization_parameters = self.load_parameters()
        
if __name__ == "__main__":
    foo = QueryResult(["ron", "dumbledore"])
    foo.populate_dictionaries()
    foo.generate_statement_graph(50, 100)