import unittest
from graph.node import Node
from util.pagerank import PageRank
from graph.graph import Graph

class TestPageRank(unittest.TestCase):
    '''
    Testcases for PageRank class.
    '''
    
    node1 = Node("node1")
    node2 = Node("node2")
    node3 = Node("node3")
    
    node1.add_edge(node2, 1)
    node3.add_edge(node2, 1)
    node2.add_edge(node1, 1)
    node2.add_edge(node3, 1)
    
    nodes = [node1,
             node2,
             node3,
             ]
    
    def test_initial_matrix(self):
        """Tests matrix initialization."""
        
        s = [[0, 1, 0], [1, 0, 1], [0, 1, 0]]
        p = PageRank(Graph(nodes=self.nodes))
        p.initial_matrix()
        
        for i, row in enumerate(p.matrix):
            self.assertEqual(row[0], s[i][0])
            self.assertEqual(row[1], s[i][1])
            self.assertEqual(row[2], s[i][2])
            
    def test_probability_matrix(self):
        """Tests probability matrix computation."""
        
        s = [[1/6, 2/3, 1/6], [5/12, 1/6, 5/12], [1/6, 2/3, 1/6]]
        p = PageRank(Graph(nodes=self.nodes), 0.5)
        p.initial_matrix()
        p.probability_matrix()

        for i, row in enumerate(p.matrix):
            self.assertAlmostEqual(row[0], s[i][0])
            self.assertAlmostEqual(row[1], s[i][1])
            self.assertAlmostEqual(row[2], s[i][2])
    
    def test_single_iteration(self):
        """Tests a single iteration of pagerank power method."""
        
        s = [1/6, 2/3, 1/6]
        vector = [1, 0, 0]
        p = PageRank(Graph(nodes=self.nodes), 0.5)
        p.initial_matrix()
        p.probability_matrix()    
        self.assertAlmostEqual(p.iterate(vector), s)
        
    def test_iteration_until_convergence(self):
        """Tests power method until convergence."""
        
        s = [5/18, 4/9, 5/18]
        vector = [1, 0, 0]
        p = PageRank(Graph(nodes=self.nodes), 0.5)
        p.initial_matrix()
        p.probability_matrix()
        v = p.iterate_until_convergence(vector).result
        
        self.assertAlmostEqual(v[0], s[0], 3)
        self.assertAlmostEqual(v[1], s[1], 3)
        self.assertAlmostEqual(v[2], s[2], 3)

    def test_few_iterations(self):
        """Tests a few iterations of pagerank power method."""
        
        s = [7/24, 5/12, 7/24]
        vector = [1, 0, 0]
        p = PageRank(Graph(nodes=self.nodes), 0.5)
        p.initial_matrix()
        p.probability_matrix()
        v = p.iterate_until_convergence(vector, iterations=4).result
        
        self.assertAlmostEqual(v[0], s[0], 3)
        self.assertAlmostEqual(v[1], s[1], 3)
        self.assertAlmostEqual(v[2], s[2], 3)
        
unittest.main()
