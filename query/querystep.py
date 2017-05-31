from query.queryresult import QueryResult


def query(query=[], queryname=None, max_nodes=25, max_edges=50):
    foo = QueryResult()
    foo.query = query
    foo.populate_dictionaries()
    return foo
    
if __name__ == "__main__":
    #png_query()
    query(["ron", "dumbledore"])