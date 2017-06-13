from collections import Counter

class PageRank(object):
    '''
    Implemenation of pagerank algorithm
    '''
    
    CONVERGENCE = 0.0001
    MAX_STEPS = 50
    
    def __init__(self, graph=None, teleporter=0):
        '''
        Constructor
        '''
        
        if graph is None:
            raise Exception("A graph is required.")
        
        if teleporter < 0:
            teleporter = 0
            
        self.graph = graph
        self.teleporter = teleporter
        
    def initial_matrix(self):
        """Creates initial NxN matrix with initial edge values."""
        
        # initialize empty NxN matrix to 0
        matrix = [[0 for _ in range(0, len(self.graph.nodes))] \
                  for _ in range(0, len(self.graph.nodes))]
        
        # loop for rows
        for j in range(0, len(self.graph.nodes)):
            node = self.graph.nodes[j]
            
            # loop for value in each row
            for i in range(0, len(self.graph.nodes)):
                
                # check if edge exists
                edge = node.get_edge(end=self.graph.nodes[i])
                if edge:
                    matrix[j][i] = edge.val
        self.matrix = matrix
        
    def probability_matrix(self):
        """Calculates the initial probability matrix for pagerank computation
        using the steps described in the Stanford NLP book.
        
            1) If a row has no 1's, replace each element by 1/N. For all other
                rows, proceed.
            2) Divide each 1 by the number of 1's in its row.
            3) Multiply the matrix by 1-alpha, where alpha is the teleportation
                chance.
            4) Add alpha/N to each entry of the matrix.
        
        """
        
        # holds rows that had no 1's as described in step 1)
        done = []
        for i, row in enumerate(self.matrix):
            if not any(x in (1, 1.0) for x in row):
                row = [1/len(row) for _ in range(0, len(row))]
                done.append(i)
                self.matrix[i] = row
        
        for i, row in enumerate(self.matrix):
            if i in done:
                continue
            
            # used to count the 1's in each row
            count = -1
            for j, val in enumerate(row):
                if val == 1:
                    if count == -1:
                        count = Counter(row)[1]
                    
                    # step 2)
                    row[j] = row[j]/count
                
                # step 3)
                row[j] *= 1 - self.teleporter
                
                # step 4)
                row[j] += self.teleporter/len(row)
            self.matrix[i] = row
                        
    def iterate(self, vector):
        """Calculates a single iteration of pagerank power method.
            
            Args:
                vector: A 1xN vector, where N is the number of columns/rows
                    of the matrix.
            Returns:
                The vector after 1 iteration of power method.
        """
        
        new = []
        for i, _ in enumerate(vector):
            column = []
            for j in range(0, len(vector)):
                column.append(self.matrix[j][i])
                
            tmp = 0
            for j, c in enumerate(column):
                tmp += vector[j] * c
            new.append(tmp)
            
        return new
    
    def iterate_until_convergence(self, vector, iterations=-1):
        """Calculates iterations of pagerank power method until convergence.
        Convergence is checked by by comparing the difference between the 
        values of the vector at iteration step k and iteration step k+1.
        If the difference of all values is less than the convergence threshhold
        defined, then the method returns.
        Alternatively, it performs X iterations and returns after those X
        iterations.
            
            Args:
                vector: The initial input vector.
                iterations: The number of iterations to be performed.
            Returns:
                The vector after either X iterations or after convergence
                of the power method.
        """
        
        # calculate 1 iteration to have vector to compare to for convergence
        new = self.iterate(vector)
        
        # used to check whether the max iterations have been calculated
        counter = 1
        
        while all(abs(vector[x] - new[x]) > self.CONVERGENCE 
                  for x in range(0, len(vector))):
            
            # vector of step k
            vector = new
            
            # vector of step k+1
            new = self.iterate(vector)
            counter += 1
            if counter == self.MAX_STEPS or counter == iterations:
                break
            
        print("convergence after ", counter, " iterations (or possibly max "+
        "iterations reached if you specified that)")
        #return new
        return PagerankResult(new, counter)
    
class PagerankResult(object):
    def __init__(self, result_vector, iterations_performed):
        self.result = result_vector
        self.iterations = iterations_performed
