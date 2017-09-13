import os
import re

from django.db import IntegrityError
from django.http import JsonResponse
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
            lesser_edges = queryform.cleaned_data["lesser_edges"]
            print("FORM LESSER EDGES: ", lesser_edges)
            result = querystep.query(queryform.cleaned_data["query"], alias="\\"+alias.identifier,
                                     lesser_edges=lesser_edges)
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
                "samples": samples,
                "alias": alias.identifier
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
    for provenance, weight, content in samples:
        # for triples in weight check if it exists in the text, TODO
        matches = set()
        for n in normalized:
            match = re.findall("\\b{}\\b".format(n), content, re.IGNORECASE)
            if match:
                content = re.sub("\\b{}\\b".format(n), "<b>{}</b>".format(match[0]), content, flags=re.IGNORECASE)
                matches |= set(match)
        updated_samples.append((provenance, weight, content, matches))
    print("MARKUP SAMPLES")
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
            all_steps(processform.cleaned_data["texts"], language=processform.cleaned_data["language"],
                      alias=alias)
    processform = ProcessForm(text_choices=texts)
    context = {
        "processform": processform,
    }
    return render(request, "queryapp/process.html", context)


def get_provenance(request):
    provenance = request.POST["provenance"]
    next_or_previous = provenance.split("_")[-1]
    provenance_id = int(re.findall(r'_\d+_', provenance)[0].split("_")[1])
    if next_or_previous == "next":
        provenance_id += 1
    elif next_or_previous == "previous":
        provenance_id -= 1
    provenance_name = re.findall('(.+)_\d+', provenance)[0]
    provenance_id_next = provenance_id
    provenance_id_previous = provenance_id
    provenance_next = "{}_{}".format(provenance_name, provenance_id_next)
    provenance_previous = "{}_{}".format(provenance_name, provenance_id_previous)
    alias = request.POST["alias"]
    matches = request.POST.getlist("matches[]")
    file_path = "{}/{}/{}_{}".format(paths.PARAGRAPH_CONTENT_PATH, alias, provenance_name, provenance_id)
    data = {}
    if os.path.isfile(file_path):
        with open(file_path, "r", encoding="utf8") as paragraph:
            content = paragraph.read()
            for n in matches:
                match = re.findall("\\b{}\\b".format(n), content, re.IGNORECASE)
                if match:
                    content = re.sub("\\b{}\\b".format(n), "<b>{}</b>".format(match[0]), content, flags=re.IGNORECASE)
            data["content"] = content
    else:
        print(file_path)
    data["provenance"] = provenance
    data["next"] = provenance_next
    data["previous"] = provenance_previous
    data["matches"] = ";".join(matches)
    return JsonResponse(data)


if __name__ == "__main__":
    markup_samples(["Harry visited Hagrid and Harry."], ["harry_and_ron", "ron"])
