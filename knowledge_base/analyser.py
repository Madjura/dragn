import math
from knowledge_base.neomemstore import NeoMemStore

class Analyser:
    """
    Basic class for matrix perspective analysis, offering the following services:
      - clustering of the input matrix rows 
      - learning of rules from the perspective and its compressed counterpart
    """

    def __init__(self, store: NeoMemStore, ptype: str, compute=True, mem=True, trace=False):
        """
        Initialising the class with an input matrix to be analysed.
        """
    
        self.trace = trace
        self.store = store
        self.ptype = ptype
        # the matrix handler of the perspective, computed from scratch by default
        self.matrix = self.store.perspectives[self.ptype]
        if compute:
            self.matrix = self.store.computePerspective(self.ptype)
            
        # <expression>: {(close to, <expression2>): value}
        self.sparse = None
        
        # (close to, <expression>): [<expressions>], essentially the reverse of self.sparse
        self.col2row = None
        # get an in-memory representation of the matrix
        if mem and trace:
            print("DEBUG - getting the sparse in-memory matrix")
            self.sparse, self.col2row = self.matrix.get_sparse_dict()

    def similar_to(self, entity: str, top=100, minsim=0.001, sims2src={}):
        """
        Generates a list of (similar_entity,similarity) tuples for an input entity.
        sims2src is for storage of mapping pairs of similar things (or rather 
        their IDs) to the statements that were used for computing their similarity.
        """
    
        if entity == None or not entity in self.sparse:
            return []
        # the row vector of the sparse matrix (a column_index:weight dictionary)
        row = self.sparse[entity]
        un = math.sqrt(sum([row[expression]**2 for expression in row]))
        
        # promising holds all expressions that are possibly relevant
        promising = set()
        for col in row:
            promising |= self.col2row[col]
        if self.trace:
            print("DEBUG@similar_to() - entity vector size        :", len(row))
            print("DEBUG@similar_to() - number of possibly similar:", len(promising))
        sim_vec = []

        # now check all possibly relevant expressions for actual relevancy
        for possible_expression in promising:
            
            # ignore same, no reason to check
            if possible_expression == entity:
                continue
            
            # container for statements that lead to particular similarities
            statements_used = set()
            
            """
            this has the format:
                ("close to / relevant to", <expression>): value
            """
            compared_row = self.sparse[possible_expression]
            # computing the actual similarity
            uv = 0.0
            vn = 0.0
            for expression in compared_row:
                if expression in row:
                    tmp = row[expression]*compared_row[expression]
                    uv += tmp
                # updating the statements used information
                if self.ptype == 'LAxLIRA':
                    statements_used.add((entity, expression[0], expression[1]))
                    statements_used.add((possible_expression, expression[0], expression[1]))
                vn += compared_row[expression]**2
            vn = math.sqrt(vn)
            sim = float(uv)/(un*vn)
            if math.fabs(sim) >= minsim:
                # add only if similarity crosses the threshold (adding code 
                # translated from the sparse representation row index)
                sim_vec.append((sim, possible_expression))
                sims2src[(entity, possible_expression)] = statements_used
        if self.trace:
            print("DEBUG@similar_to() - number of actually similar:", len(sim_vec))
            print("DEBUG@similar_to() - sorting and converting the results now")
        # getting the (similarity, row vector ID) tuples sorted
        sorted_tuples = sorted(sim_vec,key=lambda expression: expression[0])
        sorted_tuples.reverse()
        return [(expression[1], expression[0]) for expression in sorted_tuples[:top]]

