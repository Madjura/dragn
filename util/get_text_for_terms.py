from itertools import combinations
from util.load_prov import load_prov
from _collections import defaultdict


def get_text_for_terms(terms):
    import django    
    django.setup()
    from dataapp.models import InverseIndex
    
    provs = {}
    for term in terms:
        prov = InverseIndex.objects.get_queryset().filter(term=term)
        prov_set = set(x.index for x in prov)
        provs[term] = prov_set


    dict_combos = []
    keys = provs.keys()
    for i in range(1, len(keys)):
        dict_combos.append(list(combinations(keys, i+1)))
    
    combo_sets = {}
    for combos in dict_combos:
        for t in combos:
            prov_set = None
            terms = []
            for term in t:
                terms.append(term)
                if not prov_set:
                    prov_set = provs[term]
                    continue
                prov_set = prov_set.intersection(provs[term])
            if prov_set:
                combo_sets[tuple(x for x in terms)] = prov_set
    
    texts = defaultdict(lambda: list())
    for combo, provs in combo_sets.items():
        for prov in provs:
            texts[combo].append(load_prov(prov))
    return texts

if __name__ == "__main__":
    get_text_for_terms(["cult", "water", "fish", "fear"])