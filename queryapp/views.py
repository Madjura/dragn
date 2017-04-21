from django.shortcuts import render
from queryapp.forms import QueryForm
from query import querystep

# Create your views here.
def query(request):
    if request.method == "POST":
        queryform = QueryForm(request.POST)
        if queryform.is_valid():
            graph = querystep.query(queryform.cleaned_data["query"],
                                    max_nodes=queryform.cleaned_data["max_nodes"],
                                    max_edges=queryform.cleaned_data["max_edges"])
        
        context = {
                "graph_elements": graph.to_json(),
                "queryform": queryform,
            }
        return render(request, "queryapp/result.html", context)
    elif request.method == "GET":
        queryform = QueryForm()
        context = {
                "queryform": queryform,
            }
        return render(request, "queryapp/result.html", context)