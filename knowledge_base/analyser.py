import math

class Analyser:
    """
    Basic class for matrix perspective analysis, offering the following services:
      - clustering of the input matrix rows 
      - learning of rules from the perspective and its compressed counterpart
    """

    def __init__(self, 
                 mem=True,
                 trace=False,
                 matrix=None):
        """Initialising the class with an input matrix to be analysed."""
        self.trace = trace
        # the matrix handler of the perspective, computed from scratch by default
        self.matrix = matrix
            
        # <token>: {(close to, <token2>): value}
        self.sparse = None
        
        # (close to, <token>): [<tokens>], essentially the reverse of self.sparse
        self.col2row = None
        # get an in-memory representation of the matrix
        if mem and trace:
            print("DEBUG - getting the sparse in-memory matrix")
            self.sparse, self.col2row = self.matrix.get_sparse_dict()

    def similar_to(self, subject: str, top=100, minsim=0.001):
        """
        Calculates tokens similar to a given one.
        """
    
        if subject == None or not subject in self.sparse:
            return []
        # the row vector of the sparse matrix (a column_index:weight dictionary)
        #                 paul     ball     roof
        # close to, paul   1.0      0.8      0.3
        # close to, roof   0.6      0.5      0.2
        # close to, ball   0.3      0.3      1.0
        # values are examples
        # sparse[paul] = [(close to, paul): 1.0, (close to, roof): 0.6, (close to, ball: 0.3)]
        row = self.sparse[subject]
        
        # length of row
        # sum = 1.0**2 + 0.6**2 + 0.3**2 = 1.45
        # sqrt(sum) = 0.6708
        un = math.sqrt(sum([row[expression]**2 for expression in row]))
        
        # promising holds all expressions that are possibly relevant
        # paul, roof, ball
        promising = set()
        for col in row:
            promising |= self.col2row[col]
        if self.trace:
            print("DEBUG@similar_to() - subject vector size        :", len(row))
            print("DEBUG@similar_to() - number of possibly similar:", len(promising))
        sim_vec = []

        # now check all possibly relevant expressions for actual relevancy
        # paul, roof, ball
        for possible in promising:
            
            # ignore same, no reason to check
            if possible == subject:
                continue
            # example: roof
            # paul: 0.3, roof: 0.2, ball: 1.0
            compared_row = self.sparse[possible]
            # computing the actual similarity
            uv = 0.0
            vn = 0.0
            for expression in compared_row:
                if expression in row:
                    # example: paul and ball
                    # row[(close to, paul)] = 1.0
                    # compared_row[(close to, paul)] = 0.3
                    # uv += 0.3 
                    tmp = row[expression] * compared_row[expression]
                    uv += tmp
                vn += compared_row[expression]**2
            # vn is length of compared_row after sqrt
            vn = math.sqrt(vn)
            
            # vn is length of compared, un is length of original
            # uv is the product of weights of entries that are in both rows
            sim = float(uv)/(un*vn)
            if math.fabs(sim) >= minsim:
                # add only if similarity crosses the threshold (adding code 
                # translated from the sparse representation row index)
                sim_vec.append((sim, possible))
        if self.trace:
            print("DEBUG@similar_to() - number of actually similar:", len(sim_vec))
            print("DEBUG@similar_to() - sorting and converting the results now")
        # getting the (similarity, row vector ID) tuples sorted
        sorted_tuples = sorted(sim_vec,key=lambda expression: expression[0])
        sorted_tuples.reverse()
        return [(expression[1], expression[0]) for expression in sorted_tuples[:top]]