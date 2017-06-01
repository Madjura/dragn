import re

from django.shortcuts import render

from query import querystep
from queryapp.forms import QueryForm
from util import paths


# Create your views here.
def query(request):
    if request.method == "POST":
        queryform = QueryForm(request.POST)
        if queryform.is_valid():
            result = querystep.query(queryform.cleaned_data["query"])
            graph = result.generate_statement_graph(
                queryform.cleaned_data["max_nodes"],
                queryform.cleaned_data["max_edges"])
            samples = load_samples(result.get_top_provenances(
                queryform.cleaned_data["top_text_samples"]))
            nodes = [x.name for x in graph.nodes]
            samples = markup_samples(samples, nodes)
            context = {
                "graph_elements": graph.to_json(),
                "queryform": queryform,
                "samples": samples
            }
        else:
            context = {}
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
        with open(paths.PARAGRAPH_CONTENT_PATH + "/{}".format(name), "r",
                  encoding="utf8") as text:
            texts.append((name, weight, text.read()))
    return texts


def markup_samples(samples, nodes):
    normalized = set()
    for node in nodes:
        normalized |= {node.replace("_", " ")}
    updated_samples = []
    print(normalized)
    for provenance, weight, content in samples:
        for n in normalized:
            match = re.findall("\\b{}\\b".format(n), content, re.IGNORECASE)
            if match:
                content = re.sub("\\b{}\\b".format(n), "<b>{}</b>".format(match[0]), content, flags=re.IGNORECASE)
        updated_samples.append((provenance, weight, content))
    print(updated_samples)
    return updated_samples


if __name__ == "__main__":
    markup_samples(["Harry visited Hagrid and Harry."], ["harry_and_ron", "ron"])
