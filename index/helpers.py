"""Helper methods for index_step."""
from _collections import defaultdict


def generate_relation_provenance_weights(sources, relations):
    """
    Generates the mapping of predicate tuples to provenance with their score therein.
    """
    dictionary = defaultdict(lambda: list())
    inverse = defaultdict(lambda: set())
    for (subject, predicate, objecT, provenance), score in sources.items():
        score = relations[(subject, predicate, objecT)]
        dictionary[(subject, predicate, objecT)].append((provenance, score))
        inverse[subject].add(provenance)
        inverse[objecT].add(provenance)
    return dictionary, inverse


def add_related_to(relations, relation2prov):
    """
    Calculates "related to" relations.
    :param relations: Relations that were already found.
    :param relation2prov: The dictionary mapping relations to the provenance.
    :return: A dictionary containing the "related to" relations.
    """
    related = []
    dictionary = defaultdict(lambda: list())
    relations_d = defaultdict(lambda: set())
    for (subject, predicate, objecT), weight in relations.items():
        relations_d[subject].add((predicate, objecT))
        if predicate == "related to":
            related.append(((subject, predicate, objecT), weight))
    # check all "related to" triples
    for (subject, predicate, objecT), weight in related:
        combined_relations = relations_d[subject] & relations_d[objecT]
        prov2relatedscore = defaultdict(lambda: list())
        # get all the overlaps
        for related_relation, related in combined_relations:
            triple1 = (subject, related_relation, related)
            triple2 = (objecT, related_relation, related)
            relations_to_check = []
            if triple1 in relation2prov:
                relations_to_check.append((("SUBJECT", related), relation2prov[triple1]))
            if triple2 in relation2prov:
                relations_to_check.append((("OBJECT", related), relation2prov[triple2]))
            for relation_tuple in relations_to_check:
                related, provs = relation_tuple
                for prov, score in provs:
                    prov2relatedscore[prov].append((related, score))
        for provenance, tuples in prov2relatedscore.items():
            max_score_tuple = sorted(tuples, key=lambda x: x[1], reverse=True)[0]
            related_tuple, prov_weight = max_score_tuple
            identifier, actual_related = related_tuple
            if identifier == "SUBJECT":
                # noinspection PyPep8Naming
                objecT = actual_related
            elif identifier == "OBJECT":
                subject = actual_related
            else:
                raise ValueError("This should never happen unless something goes HORRIBLY wrong. Problematic value: "
                                 + identifier)
            prov_weight *= weight
            dictionary[(subject, predicate, objecT)].append((provenance, prov_weight))
    return dictionary


def index_to_db(index):
    """
    Writes the inverted index to the database.
    :param index: The index.
    :return:
    """
    import django
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dragn.settings")
    django.setup()
    from dataapp.models import InverseIndex

    bulk = []
    for term, provs in index.items():
        bulk.extend([InverseIndex(term=term, index=prov) for prov in provs])
    # noinspection PyBroadException
    try:
        InverseIndex.objects.bulk_create(bulk)
    except:
        print("DUPLICATE INDEX DETECTED. TEXT(S) ALREADY INDEXED.")
        return
    print("MADE {} INDEX OBJECTS".format(len(bulk)))
