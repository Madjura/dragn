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
        self.sparse = None
        self.rmaps = None
        self.cmaps = None
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
    
        # @NOTE - an implementation that makes use of a simple dictionary-based 
        #         sparse matrix representation and corresponding column to row 
        #         index
        
        entity_id = entity
        if entity_id == None or not entity_id in self.sparse:
            return []
        # the row vector of the sparse matrix (a column_index:weight dictionary)
        row = self.sparse[entity_id]
        un = math.sqrt(sum([row[x]**2 for x in row]))
        # getting promising vectors for the similarity computation
        promising = set()
        for col in row:
            promising |= self.col2row[col]
        if self.trace:
            print("DEBUG@similar_to() - entity vector size        :", len(row))
            print("DEBUG@similar_to() - number of possibly similar:", len(promising))
        # structures for:
        # - (similarity,vector ID) tuples
        # - similar vector ID tuples mapped to source statements that were used
        #   to compute them
        #sim_vec, sims2src = [], {}
        sim_vec = []
        # going through all promising rows in the sparse matrix representation
        for v_id in promising:
            if v_id == entity_id:
                # don't process the same entity as similar
                continue
            # container for statements that lead to particular similarities
            statements_used = set()
            compared_row = self.sparse[v_id]
            # computing the actual similarity
            uv, vn = 0.0, 0.0
            for x in compared_row:
                if x in row:
                    tmp = row[x]*compared_row[x]
                    uv += tmp
                # updating the statements used information
                if self.ptype == 'LAxLIRA':
                    statements_used.add((entity_id,x[0],x[1]))
                    statements_used.add((v_id,x[0],x[1]))
                vn += compared_row[x]**2
            vn = math.sqrt(vn)
            sim = float(uv)/(un*vn)
            if math.fabs(sim) >= minsim:
                # add only if similarity crosses the threshold (adding code 
                # translated from the sparse representation row index)
                sim_vec.append((sim,v_id))
                sims2src[(entity_id,v_id)] = statements_used
        if self.trace:
            print("DEBUG@similar_to() - number of actually similar:", len(sim_vec))
            print("DEBUG@similar_to() - sorting and converting the results now")
        # getting the (similarity, row vector ID) tuples sorted
        sorted_tuples = sorted(sim_vec,key=lambda x: x[0])
        sorted_tuples.reverse()
        return [(x[1], x[0]) for x in sorted_tuples[:top]]

