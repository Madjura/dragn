import json
class Graph(object):
    '''
    Simple graph with nodes and edges.
    '''

    def __init__(self, nodes: ["Node"] = None):
        '''
        Constructor
        '''
        
        if nodes is not None:
            self.nodes = nodes
        else:
            self.nodes = []
            
    def __str__(self, *args, **kwargs):
        out = ""
        for node in self.nodes:
            out += "Node: {}\n".format(node.name)
            for edge in node.edges:
                out += "--- Edge from {} to {}\n".format(edge.start, edge.end)
        return out
    
    def to_json(self):
        json_string = "["
        for node in self.nodes:
            json_string += """{{"group": "nodes","data": {{"id": "{}"}},"grabbable": true,"classes": "node-class"}},""".format(node.name)
        for j, node in enumerate(self.nodes):
            for i, edge in enumerate(node.edges):
                json_string += """{{"group": "edges","data": {{"id": "e{}-{}","source": "{}","target": "{}","color": "{}"}}}},""".format(j,i,edge.start.name,edge.end.name,edge.color)
        json_string = json_string[:-1]
        json_string += "]"
        print(json_string)
        return json_string
    
    def to_json_dump(self):
        dump = []
        for node in self.nodes:
            dump.append({
                "group": "nodes",
                "data": {
                    "id": node.name
                    },
                "grabbable": True,
                "classes": "node-class"
                })
        for i, node in enumerate(self.nodes):
            for j, edge in enumerate(node.edges):
                dump.append({
                    "group": "edges",
                    "data": {
                        "id": "e{}-{}".format(i,j),
                        "source": edge.start.name,
                        "target": edge.end.name,
                        "color": edge.color
                        }
                    })
        out = json.dumps(dump)
        return out