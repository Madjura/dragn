from _collections import defaultdict
from operator import itemgetter


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


def generate_relation_to_provenances(sources: "suids",
                                     relation2prov: "suid2puid",
                                     out_file=None):
    # relation2prov is: SPO: [provenance, score]
    related = []
    relations = defaultdict(lambda: set())
    missing = 0
    processed = 0
    for (subject, predicate, objecT), weight in sources.items():
        relations[subject].add((predicate, objecT))
        if predicate == "related to":
            related.append(((subject, predicate, objecT), weight))
    # check all "related to" triples
    to_write = defaultdict(lambda: defaultdict(int))
    for (subject, predicate, objecT), weight in related:
        # get all "<subject> predicate <objecT>" triples and "<objectT> predicate <subject>" triples THAT APPEAR IN BOTH
        combined_relations = relations[subject] & relations[objecT]
        prov2weight = defaultdict(lambda: list())
        prov2relatedscore = defaultdict(lambda: list())

        # get all the overlaps
        for related_relation, related in combined_relations:
            # triple1: paul close to house
            # triple2: house close to house
            triple1 = (subject, related_relation, related)
            triple2 = (objecT, related_relation, related)
            relations_to_check = []
            # lets say we find "paul close to house" in paragraphs 1, 2 and 5
            # we then add ( (paragraph 1, FMI), (paragraph 2, FMI), (paragraph 5, FMI) ) to tmp
            if triple1 in relation2prov:
                relations_to_check.append((("SUBJECT", related), relation2prov[triple1]))
            if triple2 in relation2prov:
                relations_to_check.append((("OBJECT", related), relation2prov[triple2]))
            for relation_tuple in relations_to_check:
                related, provs = relation_tuple
                for prov, score in provs:
                    prov2relatedscore[prov].append((related, score))
        if not prov2weight:
            missing += 1
        for provenance, tuples in prov2relatedscore.items():
            # maximum relation value * related_to weight
            max_score_tuple = sorted(tuples, key=lambda x: x[1], reverse=True)[0]
            related_tuple, prov_weight = max_score_tuple
            identifier, actual_related = related_tuple
            if identifier == "SUBJECT":
                subject = actual_related
            elif identifier == "OBJECT":
                # noinspection PyPep8Naming
                objecT = actual_related
            else:
                raise ValueError("This should never happen unless something goes HORRIBLY wrong. Problematic value: "
                                 + identifier)
            if out_file is not None:
                line = "\t".join([str((subject, predicate, objecT)),
                                  str([(provenance, prov_weight)])])
                out_file.write(str.encode(line))
                out_file.write(str.encode("\n"))
            processed += 1
    return missing, processed


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
