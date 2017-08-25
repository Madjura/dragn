from _collections import defaultdict


def generate_relation_provenance_weights(sources, relations):
    """
    Generates the mapping of predicate tuples to provenance with closeness
    therein.
    """

    dictionary = defaultdict(lambda: list())
    inverse = defaultdict(lambda: set())
    for (subject, predicate, objecT, provenance), closeness in sources.items():
        closeness = relations[(subject, predicate, objecT)]
        dictionary[(subject, predicate, objecT)].append((provenance, closeness))
        inverse[subject].add(provenance)
        inverse[objecT].add(provenance)
    return dictionary, inverse


def add_related_to(sources, relation2prov, out_file=None):
    related = []
    relations = defaultdict(lambda: set())
    for (subject, predicate, objecT), weight in sources.items():
        relations[subject].add((predicate, objecT))
        if predicate == "related to":
            # (('jesus_of_nazareth', 'related to', 'custom_moses'), 0.279028174830471),
            if subject == "jesus_of_nazareth" and predicate == "custom_moses":
                print("INDEX IF 1")
            elif subject == "custom_moses" and predicate == "jesus_of_nazareth":
                print("INDEX IF 2")
            related.append(((subject, predicate, objecT), weight))
    # check all "related to" triples
    for (subject, predicate, objecT), weight in related:
        combined_relations = relations[subject] & relations[objecT]
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
            if out_file is not None:
                # predicate is ALWAYS related to
                line = "\t".join([str((subject, predicate, objecT)),
                                  str([(provenance, prov_weight)])])
                out_file.write(str.encode(line))
                out_file.write(str.encode("\n"))


def index_to_db(index):
    import django
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dragn.settings")
    django.setup()
    from dataapp.models import InverseIndex

    bulk = []
    for term, provs in index.items():
        bulk.extend([InverseIndex(term=term, index=prov) for prov in provs])
    try:
        InverseIndex.objects.bulk_create(bulk)
    except:
        print("DUPLICATE INDEX DETECTED. TEXT(S) ALREADY INDEXED.")
        return
    print("MADE {} INDEX OBJECTS".format(len(bulk)))
