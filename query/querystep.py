from query.queryresult import QueryResult


def query(query=None):
    if query is None:
        query = []
    foo = QueryResult()
    foo.query = query
    foo.populate_dictionaries()
    return foo


if __name__ == "__main__":
    # png_query()
    query(["ron", "dumbledore"])
