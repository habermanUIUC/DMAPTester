# SOLUTION
apples = {
    "McIntosh": {"sweetness": 3, "tartness": 7},
    "Red Delicious": {"sweetness": 5, "tartness": 1},
    "Fuji": {"sweetness": 8, "tartness": 3},
    "Gala": {"sweetness": 6, "tartness": 1},
    "Ambrosia": {"sweetness": 7, "tartness": 1},
    "Honeycrisp": {"sweetness": 7.5, "tartness": 8},
    "Granny Smith": {"sweetness": 1, "tartness": 10}
}

def by_sweetness(d):
    # d[0] is the key   apples[k]["sweetness"]
    # d[1] is the dict  d[1]["sweetness"]
    return d[1]["sweetness"]


def by_tartness(d):
    # d[0] is the key   apples[k]["sweetness"]
    # d[1] is the dict  d[1]["sweetness"]
    return d[1]["tartness"]


def apple_sorting(model, fn):
    # what happens when the var n lamda is the same
    # as a parementer name ???
    # key=lambda by_sweetness: by_sweetness[1]['sweetness'])
    return sorted(model.items(), key=fn, reverse=True)


def sort_by_total_calories(v):
    out = []
    for v in sorted(v.items(),
                    key=lambda item: item[1]["count"] * item[1]["calories"],
                    reverse=True):
        out.append((v[0], v[1]["count"] * v[1]["calories"]))
    return out
