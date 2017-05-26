from itertools import combinations, product
def get_text_for_terms(terms):
    import django    
    django.setup()
    from dataapp.models import InverseIndex
    
    provs = {}
    for term in terms:
        prov = InverseIndex.objects.get_queryset().filter(term=term)
        prov_set = set(x.index for x in prov)
        provs[term] = prov_set

    set_combos = []
    for i in range(len(prov.values())):
        combos = list(combinations(provs.values(), i+2))
        for c in combos:
            for s in product(*c):
                if len(s) == 1:
                    continue
                else:
                    set_combos.append(set(s))
    
    print(set_combos)
    intersect = None
    for term in terms:
        if not intersect:
            intersect = provs[term]
            continue
        intersect |= provs[term]
        
    #==========================================================================
    # cult = InverseIndex.objects.get_queryset().filter(term="cult")
    # water = InverseIndex.objects.get_queryset().filter(term="water")
    # cult_prov = set()
    # water_prov = set()
    # for i in cult:
    #     cult_prov.add(i.index)
    # for i in water:
    #     water_prov.add(i.index)
    # print(cult_prov, water_prov)
    # intersect = cult_prov.intersection(water_prov)
    # for prov in intersect:
    #     print(prov, load_prov(prov))
    #==========================================================================
        

if __name__ == "__main__":
    get_text_for_terms(["cult", "water", "fish", "fear"])