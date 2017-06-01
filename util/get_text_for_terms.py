from _collections import defaultdict, OrderedDict
from itertools import combinations

from util.load_prov import load_prov


def get_text_for_terms(terms, sort=True, limit=None):
    """
    Loads the paragraphs of all processed texts that contain certain terms.
    Checks all combinations of the given terms and returns a mapping of 
    combinations to all the paragraphs that contain the specific combination.
    The mapping is optionally ordered by the number of paragraphs the 
    combinations appear in together, descending.
    
        Args:
            terms: The terms that are being queried.
            sort: Optional. Default: True.
                Whether the dictionary is to be sorted.
            limit: Optional. Default: None.
                To limit to the top X combinations.
                Only makes sense to be used with "sort" set to True.
        Returns:
            A dictionary in the format:
                tuple(): [paragraph, paragraph2, ...]
            With the paragraph lists sorted by their length.
    """
    # django setup stuff to access the index
    import django
    django.setup()
    from dataapp.models import InverseIndex

    # get all the provs for the terms
    provs = {}
    for term in terms:
        prov = InverseIndex.objects.get_queryset().filter(term=term)
        prov_set = set(x.index for x in prov)
        provs[term] = prov_set
    # create all the possible combinations
    dict_combos = []
    keys = provs.keys()
    for i in range(1, len(keys)):
        dict_combos.extend(list(combinations(keys, i + 1)))
    # create the intersection of provenances of all set combinations
    combo_sets = {}
    for combos in dict_combos:
        terms = []
        prov_set = None
        for term in combos:
            terms.append(term)
            # prov_set is the first, initialize
            if not prov_set:
                prov_set = provs[term]
            prov_set = prov_set.intersection(provs[term])
            # if after the intersection the set is empty, all future
            # intersections will be empty too, break
            if not prov_set:
                break
        if prov_set:
            combo_sets[tuple(x for x in terms)] = prov_set
    # load the provenances for the combos
    texts = defaultdict(lambda: list())
    for combo, provs in combo_sets.items():
        for prov in provs:
            content = load_prov(prov)
            if content:
                texts[combo].append(content)
    # sort and cutoff if needed
    ordered = OrderedDict()
    if not limit:
        limit = len(texts)
    if sort:
        for key in sorted(texts, key=lambda k: len(texts[k]), reverse=True)[:limit]:
            ordered[key] = sorted(texts[key], key=len)
        texts = ordered
    return texts


if __name__ == "__main__":
    print(get_text_for_terms(["cult", "water", "fish", "fear"], limit=2))
