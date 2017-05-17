from django.shortcuts import render
from queryapp.forms import QueryForm
from query import querystep
from util import paths
from _collections import defaultdict

# Create your views here.
def query(request):
    if request.method == "POST":
        queryform = QueryForm(request.POST)
        if queryform.is_valid():
            result = querystep.query(queryform.cleaned_data["query"],
                                    max_nodes=queryform.cleaned_data["max_nodes"],
                                    max_edges=queryform.cleaned_data["max_edges"])
            graph = result.generate_statement_graph(
                queryform.cleaned_data["max_nodes"], 
                queryform.cleaned_data["max_edges"])
            samples = load_samples(result.get_top_provenances(queryform.cleaned_data["top_text_samples"]))
            print(samples)
        context = {
                "graph_elements": graph.to_json(),
                "queryform": queryform,
                "samples": samples
            }
        return render(request, "queryapp/result.html", context)
    elif request.method == "GET":
        queryform = QueryForm()
        context = {
                "queryform": queryform,
            }
        return render(request, "queryapp/result.html", context)
    
def load_samples(tops):
    texts = []
    for name, weight in tops:
        with open(paths.PARAGRAPH_CONTENT_PATH + "/{}".format(name), "r") as text:
            texts.append((name, weight, text.read()))
    return texts