"""
Copyright (C) 2012 Vit Novacek (vit.novacek@deri.org), Digital Enterprise
Research Institute (DERI), National University of Ireland Galway (NUIG)
All rights reserved.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

This class is based on the MemStoreQueryResult class of the original system.
The following functions were used from the original system:
    - populate_dictionaries

    Those functions were used as a base to develop the new ones in this file.
"""

import gzip
import json
import os
from _collections import defaultdict
from ast import literal_eval
from itertools import combinations
from math import log

import ujson

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

    def __init__(self, min_weight=0.5, alias=None, relation_type="all", lesser_edges=True):
        self.query = None
        self.lesser_edges = lesser_edges
        self.queried_combined = defaultdict(lambda: set())
        self.aliases = defaultdict(lambda: set())
        self.tokens2weights = defaultdict(int)
        self.relation_set = FuzzySet()
        self.provenance_set = FuzzySet()
        # minimum weight that relations must have to be considered
        self.min_weight = min_weight
        self.visualization_parameters = self.load_parameters()
        print("Loading relation to provenance mapping")
        self.relation2prov = self.load_relation2prov(
            path=paths.RELATION_PROVENANCES_PATH + alias + "/r2p.json")
        print("Loading related")
        self.relations = self.load_token2related(path=os.path.join(paths.RELATIONS_PATH + alias, "relations.tsv.gz"),
                                                 relation_type=relation_type)
        # { relation_triple: [(provenance, weight), ...] }
        # legacy stuff that is PROBABLY not important
        # print("Loading relations")
        # self.relation_sets = self.load_relation_sets(path=paths.RELATION_WEIGHT_PATH + alias)
        self.alias = alias
        self.provenance_dict = None

    @staticmethod
    def load_relation2prov(path=None):
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
        import time
        start_time = time.time()
        with open(path.replace("provenances.tsv.gz", "r2p.json")) as f:
            relation2prov = ujson.load(f)
        fix = {}
        for key in relation2prov.keys():
            fix[literal_eval(key)] = relation2prov[key]
        relation2prov = fix
        print("--- %s seconds FOR LOADING DICT ---" % (time.time() - start_time))
        start_time = time.time()
        # get the maximum value for each prov
        # this is necessary because in index step we calculate additional triples that are immediately written to file
        # here we eliminate the duplicates and take just the max value
        for key, value in relation2prov.items():
            prov_max = defaultdict(int)
            for l in value:
                tmp = []
                it = iter(l)
                for x in it:
                    tmp.append((x, next(it)))
                for prov, score in tmp:
                    current = prov_max[prov]
                    if score > current:
                        prov_max[prov] = score
            tmp = [(prov, score) for prov, score in prov_max.items()]
            relation2prov[key] = [tmp]
        print("--- %s seconds FOR SECOND HALF ---" % (time.time() - start_time))
        return defaultdict(lambda: list(), relation2prov)

    def prepare_for_query(self):
        """
        Returns original FuzzySet containing tokens relevant to the 
        query.
        """
        query_terms = [x for x in self.query]
        query_relevant = FuzzySet()
        for term in self.query:
            # x are tuples of (token, weight)
            # keeps the higher value of "close to" and "related to" both present
            triple_list = self.relations[term]
            tuple_list = []
            for spo, score in triple_list:
                s, _, o = spo
                tuple_token = None
                if s == term:
                    tuple_token = o
                elif o == term:
                    tuple_token = s
                tuple_list.append((tuple_token, score))
            query_relevant = query_relevant | FuzzySet([x for x in tuple_list])
            # legacy stuff that is probably not important but ill keep it just in case everything goes up in flames
            # query_relevant = query_relevant | FuzzySet([x for x in self.relation_sets[term]])
        for x in query_terms:
            query_relevant[x] = 1.0
        # query_relevant = query_relevant | FuzzySet([(x, 1.0) for x in query_terms])
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
        # relevant cut is combined for fear+talk (beyondthewall,book)
        return relevant_cut

    @staticmethod
    def load_relation_sets(path=paths.RELATION_WEIGHT_PATH):
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
            for line in f:
                line_split = line.decode().split("\t")
                token, token2, weight = line_split
                relation_tuple = (token2, float(weight))
                relations[token].append(relation_tuple)
        return relations

    def populate_dictionaries(self):
        """
        Prepares the ranking of tokens / relations for use with the graph.
        
            1) Get all tokens possibly relevant to the query
            2) Get all triples related to the token in some way
            3) Filter out those that don't have relevance to the query or that token
            4) Get the degree of membership of the token <-> the query
            5) Multiply the membership with the weight from the triple
            6) Add that value to a dict for the related token and the matching queryterm (used to calculate nodes)
            7) Get the provenance, weight tuple for the relation triple
            8) Weight the provenance by the prov weight * relation weight * membership
        """
        provenance_dict = defaultdict(lambda: [0, set()])
        query_relevant = self.prepare_for_query()
        related_tokens = self.filter_relevant(query_relevant)
        # iterate over the tokens relevant to the query
        for possibly_related in related_tokens:
            # get all relation tuples in which "possibly_related" appears
            for relation_triple in self.relations[possibly_related]:
                (subject, predicate, objecT), relation_weight = relation_triple
                # find the relation triples that contain "possibly_related" and
                # a term from the query
                if not (subject in self.query or objecT in self.query):
                    # random relation that does not have any relevance
                    continue
                # get the membership degree of "possibly related" to the query
                # this is the higher value of "related to" or "close to"
                membership = related_tokens[possibly_related]
                calculated_relation_weight = membership * relation_weight
                # add updated score to subject and object
                self.tokens2weights[subject] += calculated_relation_weight
                self.tokens2weights[objecT] += calculated_relation_weight
                # why in graph but not in texts: no text where both appear
                self.relation_set[(subject, predicate, objecT)] += calculated_relation_weight
                for prov_tuple in self.relation2prov[(subject, predicate, objecT)]:
                    for provenance, prov_weight in prov_tuple:
                        provenance_dict[provenance][0] += calculated_relation_weight * prov_weight
                        provenance_dict[provenance][1].add((prov_weight, subject, predicate, objecT))
        self.provenance_dict = provenance_dict

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
                graph_edge = Edge(start=nodes[subject], end=nodes[objecT], color=edge_color)
                back_edge = Edge(start=nodes[objecT], end=nodes[subject], color=edge_color)
                # night related to twisted_time + twisted_time close to night = blue instead of purple!
                check_edge = nodes[objecT].get_edge(end=nodes[subject])
                if check_edge and check_edge.color != graph_edge.color:
                    check_edge.color = "magenta"
                    graph_edge.color = "magenta"
                nodes[subject].add_edge_object(graph_edge)
                check_edge = nodes[subject].get_edge(end=nodes[objecT])
                if check_edge and check_edge.color != back_edge.color:
                    check_edge.color = "magenta"
                    back_edge.color = "magenta"
                nodes[objecT].add_edge_object(back_edge)
                edge_count += 2
        if self.lesser_edges:
            print("LESSER EDGES: TRUE")
            for combo in list(combinations(nodes.keys(), 2)):
                if edge_count >= max_edges:
                    break
                s, o = combo
                t1 = (s, "close to", o)
                t2 = (o, "close to", s)
                t11 = (s, "related to", o)
                t22 = (o, "related to", s)
                to_check = [t1, t2, t11, t22]
                # possible problem with creating non-existant relations again
                # explanation: example for "devil" and "unto"
                # "unto" appears in the text, "devil" does not
                # graph has unto related to devil, so it adds the relation to the table
                for t in to_check:
                    if any(t_ in self.relation_set for t_ in to_check):
                        break
                    val = self.relation2prov[t]
                    if not val:
                        continue
                    ss, pp, oo = t
                    edge_color = self.visualization_parameters["edge color"][pp]
                    check_edge = nodes[oo].get_edge(end=nodes[ss])
                    if not check_edge:
                        nodes[ss].get_edge(end=nodes[oo])
                    if check_edge and check_edge.color != edge_color:
                        edge_color = "magenta"
                    new_edge = Edge(start=nodes[ss], end=nodes[oo], color=edge_color)
                    nodes[ss].add_edge_object(new_edge)
                    edge_count += 2
                    for pt in val:
                        for prov, weight in pt:
                            self.provenance_dict[prov][0] += weight
                            self.provenance_dict[prov][1].add((weight, ss, pp, oo))
        self.provenance_set = ProvFuzzySet.from_list_dictionary(self.provenance_dict)
        return Graph(nodes=list(nodes.values()), clean=False)

    @staticmethod
    def load_token2related(path=os.path.join(paths.RELATIONS_PATH, "relations.tsv.gz"), relation_type="all"):
        """Loads the mapping of tokens to the related tokens."""
        token2related = defaultdict(lambda: list())
        with gzip.open(path, "rb") as f:
            for line in f:
                spl = line.decode().split("\t")
                try:
                    relation_triple = literal_eval(spl[0])
                except SyntaxError:
                    continue
                weight = float(spl[1])
                subject, predicate, objecT = relation_triple
                if relation_type == "related to" and predicate != "related to":
                    continue
                elif relation_type == "close to" and predicate != "close to":
                    continue
                token2related[subject].append((relation_triple, weight))
                token2related[objecT].append((relation_triple, weight))
            f.close()
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
