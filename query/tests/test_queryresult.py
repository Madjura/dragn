"""Tests for queryresult module."""
import unittest

from collections import defaultdict

from query.queryresult import QueryResult


class QueryresultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        qr = QueryResult()
        qr.query = ["apple"]
        relations = {
            "apple": [
                (("apple", "close to", "fruit"), 1),
                (("apple", "close to", "tree"), 0.8),
                (("apple", "related to", "leaf"), 0.5)
            ],
            "tree": [],
            "fruit": [],
            "leaf": [],
        }
        relation2prov = {
            ("apple", "close to", "fruit"): [[("fruit1.txt", 0.8)]],
            ("apple", "close to", "tree"): [[("fruit2.txt", 0.9)]],
            ("apple", "related to", "leaf"): [[("fruit1.txt", 0.5)]]
        }
        relation2prov = defaultdict(lambda: list(), relation2prov)
        qr.relations = relations
        qr.relation2prov = relation2prov
        qr.populate_dictionaries()
        cls.qr = qr

    def test_query(self):
        """Tests queries working in general."""
        qr = QueryresultTests.qr
        graph = qr.generate_statement_graph(100, 100)
        nodes = graph.nodes
        for node in nodes:
            if node.name == "apple":
                self.assertEqual(len(node.edges), 3)  # 3 relations, 3 edges
            else:
                self.assertEqual(len(node.edges), 0)

    def test_query_faulty_input(self):
        """Tests queries reacting to faulty input, in this case number of edges and nodes are both negative."""
        qr = QueryresultTests.qr
        graph = qr.generate_statement_graph(-100, -100)
        self.assertEqual(len(graph.nodes), 0)

    def test_query_no_edges(self):
        """Tests queries working correctly with no edges in the result graph."""
        qr = QueryresultTests.qr
        graph = qr.generate_statement_graph(100, 0)
        self.assertEqual(len(graph.nodes), 4)
        for node in graph.nodes:
            self.assertEqual(len(node.edges), 0)

    def test_query_no_nodes(self):
        """Tests queries working correctly with no nodes in the result graph."""
        qr = QueryresultTests.qr
        graph = qr.generate_statement_graph(0, 100)
        self.assertEqual(len(graph.nodes), 0)

if __name__ == "__main__":
    unittest.main()
