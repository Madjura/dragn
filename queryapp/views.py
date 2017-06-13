import os
import re

from django.db import IntegrityError
from django.shortcuts import render

from allsteps.allsteps import all_steps
from query import querystep
from queryapp.forms import QueryForm, ProcessForm
from queryapp.models import Text, TextsAlias
from util import paths


# Create your views here.
def query(request):
    if request.method == "POST":
        queryform = QueryForm(request.POST)
        if queryform.is_valid():
            alias = TextsAlias.objects.get(pk=queryform.cleaned_data["texts"])
            result = querystep.query(queryform.cleaned_data["query"], alias="\\"+alias.identifier)
            graph = result.generate_statement_graph(
                queryform.cleaned_data["max_nodes"],
                queryform.cleaned_data["max_edges"])
            samples = load_samples(result.get_top_provenances(
                queryform.cleaned_data["top_text_samples"]), alias="/"+alias.identifier)
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


def load_samples(tops, alias):
    texts = []
    for name, weight in tops:
        with open(paths.PARAGRAPH_CONTENT_PATH + alias + "/{}".format(name), "r",
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
        matches = set()
        for n in normalized:
            match = re.findall("\\b{}\\b".format(n), content, re.IGNORECASE)
            if match:
                content = re.sub("\\b{}\\b".format(n), "<b>{}</b>".format(match[0]), content, flags=re.IGNORECASE)
                matches |= set(match)
        updated_samples.append((provenance, weight, content, matches))
    print(updated_samples)
    return updated_samples


def process(request):
    texts = []
    for file in os.listdir(paths.TEXT_PATH):
        if os.path.isfile(os.path.join(paths.TEXT_PATH, file)):
            texts.append(file)
    if request.method == "POST":
        processform = ProcessForm(text_choices=texts, data=request.POST)
        if processform.is_valid():
            text_objects = []
            texts = processform.cleaned_data["texts"]
            print("SELECTED TEXTS: ", texts)
            for text in texts:
                try:
                    text_objects.append(Text.objects.create(name=text))
                except IntegrityError:
                    text_objects.append(Text.objects.get(name=text))
            alias = TextsAlias.for_texts(text_objects)
            if not alias:
                name_alias = ",".join(texts)
                alias = TextsAlias.objects.create(identifier=name_alias)
                alias.save()
                for text in text_objects:
                    alias.texts.add(text)
            all_steps(texts=processform.cleaned_data["texts"], language=processform.cleaned_data["language"],
                      alias=alias)
    processform = ProcessForm(text_choices=texts)
    context = {
        "processform": processform,
    }
    return render(request, "queryapp/process.html", context)

if __name__ == "__main__":
    markup_samples(["Harry visited Hagrid and Harry."], ["harry_and_ron", "ron"])
