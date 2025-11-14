# combinações e cross-product das palavras/patterns

def generate_combinations(mg):
    base = []

    # suspeito
    base.append(mg.name.lower())
    base.append(mg.name.capitalize())

    # datas
    base.append(mg.birth)
    base.append(mg.birth[-4:])  # ano

    # filhos
    for c in mg.children:
        base.append(c.lower())
        base.append(c.capitalize())

    # animais
    for p in mg.pets:
        base.append(p.lower())
        base.append(p.capitalize())

    # keywords
    for k in mg.keywords:
        base.append(k.lower())
        base.append(k.capitalize())

    # remover duplicados mantendo ordem
    seen = set()
    final = []
    for item in base:
        if item not in seen and item != "":
            final.append(item)
            seen.add(item)

    return final
