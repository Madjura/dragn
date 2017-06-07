import gzip
import os
from _collections import defaultdict
from ast import literal_eval
from itertools import combinations
from math import log

from graph.edge import Edge
from graph.graph import Graph
from graph.node import CytoNode
from query.fuzzyset import FuzzySet, ProvFuzzySet
from util import paths


class QueryResult(object):
    """
    Wrapper over the processed text files to produce a graph in JSON
    format that can be displayed to the user.
    """

    def __init__(self, min_weight=0.5):
        self.query = None
        self.queried_combined = defaultdict(lambda: set())
        self.aliases = defaultdict(lambda: set())
        self.tokens2weights = defaultdict(int)
        self.relation_set = FuzzySet()
        self.provenance_set = FuzzySet()
        # minimum weight that relations must have to be considered
        self.min_weight = min_weight
        self.visualization_parameters = self.load_parameters()
        self.relation2prov = self.load_relation2prov()
        self.relations = self.load_token2related()
        # { relation_triple: [(provenance, weight), ...] }
        self.relation_sets = self.load_relation_sets()

    @staticmethod
    def load_relation2prov(path=os.path.join(
            paths.RELATION_PROVENANCES_PATH, "provenances.tsv.gz")):
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
            lines = f.read().decode().split("\n")
            for line in lines:
                if not line:
                    continue
                line_split = line.split("\t")
                relation_tuple = literal_eval(line_split[0])
                provenances = literal_eval(line_split[1])
                relation2prov[relation_tuple].append(provenances)
        return relation2prov

    def prepare_for_query(self):
        """
        Returns original FuzzySet containing tokens relevant to the 
        query.
        """
        import time
        start = time.time()
        query_relevant = FuzzySet()
        for term in self.query:
            # x are tuples of (token, weight)
            # keeps the higher value of "close to" and "related to" both present
            query_relevant = query_relevant | FuzzySet([x for x in self.relation_sets[term]])
        print("prepare for query took {}".format(time.time() - start))
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

    @staticmethod
    def load_relation_sets(path=paths.EXPRESSION_SET_PATH_EXPERIMENTAL):
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

    def populate_dictionaries(self):
        """
        Prepares the ranking of tokens / relations for use with the graph.
        
            1) Get all tokens possibly relevant to the query
            2) Get all triples related to the token in some way
            3) Filter out those with too low of a relation as specified by min_weight
            4) Filter out those that don't have relevance to the query or that token
            5) Get the degree of membership of the token <-> the query
            6) Multiply the membership with the weight from the triple
            7) Add that value to a dict for the related token and the matching queryterm (used to calculate nodes)
            8) Get the provenance, weight tuple for the relation triple
            9) Weight the provenance by the prov weight * relation weight * membership
        """

        # { relation_triple: calculated weight }
        # used to rank / limit the graph nodes by top values
        relation_dict = defaultdict(int)

        # { provenance: calculated weight }
        # indicates how "related" a provenance is to the query
        provenance_dict = defaultdict(lambda: [0, []])

        # { (prov1, prov2): weight }
        # indicates how "related" two provenances are
        provenance_relations = defaultdict(float)

        # all relation tuples containing query terms, with weight above threshhold
        query_relevant = self.prepare_for_query()
        # relevant_cut = self.filter_relevant(query_relevant)
        relevant_cut = self.filter_relevant(query_relevant)
        # iterate over the tokens relevant to the query
        for possibly_related in relevant_cut:

            # get all relation tuples in which "possibly_related" appears
            for relation_triple in self.relations[possibly_related]:
                (subject, predicate, objecT), relation_weight = relation_triple

                # find the relation tuples that contain "possibly_related" and
                # a term from the query
                if not (subject in self.query or objecT in self.query):
                    # random relation that does not have any relevance
                    continue

                # get the membership degree of "possibly related" to the query             
                """
                makes fuzzyset of all (subject, weight) tuples 
                the tuples come from the dict with
                subject: [(objecT, weight), ...]
                then keeps only the ones with weight above threshhold
                from that it gets the value <--- membership
                keeps higher of close to / related to
                """
                membership = relevant_cut[possibly_related]
                calculated_relation_weight = membership * relation_weight
                relation_dict[(subject, predicate, objecT)] += calculated_relation_weight
                self.tokens2weights[possibly_related] += calculated_relation_weight
                if subject != possibly_related:
                    self.tokens2weights[subject] += calculated_relation_weight
                elif objecT != possibly_related:
                    self.tokens2weights[objecT] += calculated_relation_weight
                for prov_tuple in self.relation2prov[(subject, predicate, objecT)]:
                    for provenance, prov_weight in prov_tuple:
                        provenance_dict[provenance][0] += membership * relation_weight * prov_weight
                        provenance_dict[provenance][1].append((prov_weight, subject, predicate, objecT))
                    for (prov1, w1), (prov2, w2) in combinations(prov_tuple, 2):
                        w = membership * relation_weight * (w1 + w2) / 2
                        provenance_relations[(prov2, prov1)] += w
        self.relation_set = relation_dict
        if provenance_dict:
            self.provenance_set = ProvFuzzySet.from_list_dictionary(provenance_dict)

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
            # if token in self.queried_combined:
            if token in self.query:
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
            subject, predicate, objecT = relation_tuple
            if subject in nodes and objecT in nodes:
                if predicate in self.visualization_parameters["edge color"]:
                    edge_color = self.visualization_parameters["edge color"][predicate]
                else:
                    edge_color = "black"
                # subject = self.check_alias(subject)
                # objecT = self.check_alias(objecT)
                graph_edge = Edge(start=nodes[subject], end=nodes[objecT],
                                  color=edge_color)
                nodes[subject].add_edge_object(graph_edge)
                edge_count += 2
        print("RETURNING GRAPH")
        return Graph(nodes=nodes.values())

    @staticmethod
    def load_token2related():
        """Loads the mapping of tokens to the related tokens."""
        token2related = defaultdict(lambda: list())
        path = os.path.join(paths.RELATIONS_PATH, "relations.tsv.gz")
        with gzip.open(path, "rb") as f:
            for line in f.read().decode().split("\n"):
                spl = line.split("\t")
                try:
                    relation_triple = literal_eval(spl[0])
                except SyntaxError:
                    continue
                weight = float(spl[1])
                subject, _, predicate = relation_triple
                token2related[subject].append((relation_triple, weight))
                token2related[predicate].append((relation_triple, weight))
            f.close()
        print("LEN relations ", len(token2related))
        return token2related

    @staticmethod
    def load_parameters():
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

    def check_query_relevance(self, token):
        expanded_relevancy = set()
        for check in self.query:
            if check in token:
                expanded_relevancy.add(check)
        return expanded_relevancy

    def check_alias(self, token):
        for alias in self.aliases.keys():
            if token in self.aliases[alias]:
                return alias
        return token

    def get_top_provenances(self, top=10):
        tops = []
        for item in self.provenance_set.sort(reverse=True, limit=top):
            tops.append(item)
        return tops


if __name__ == "__main__":
    import time

    start = time.time()
    foo = QueryResult()
    print("INIT TOOK: ", time.time() - start)
    foo.query = ["cult", ]
    start = time.time()
    foo.populate_dictionaries()
    print("POPULTATE TOOK: ", time.time() - start)
    foo.generate_statement_graph(50, 100)
    foo.get_top_provenances()
