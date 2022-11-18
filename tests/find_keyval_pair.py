from collections.abc import Iterable


def convert(lst):
    return {
        index: element
        for index, element in enumerate(lst)
    }

def flatten(xs):
    for x in xs:
        if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            yield from flatten(x)
        else:
            yield x


def is_valid(dct, key, val):
    if isinstance(dct, list) or isinstance(dct, tuple):
        d = convert(dct)
    elif isinstance(dct, dict):
        d = dct
    else:
        return None
    if key in d.keys() and d[key] == val:
        return key
    ans = None
    for d_key in d.keys():
        r = is_valid(d[d_key], key, val)
        if r is None:
            continue
        else:
            return [x for x in flatten([d_key] + [r])]
    return ans


if __name__ == "__main__":
    data = {
        "foo": "test",
        "bar": {
            "baz": [1, 2, {"Here?": "Yes"}, 4, 5],
            "bla": {
                "hey": "ho",
                "you": "there",
                "num": 4,
            },
            "more": {
                "num": 3,
                "you": "what?",
                "gej": "no idea"
            }
        },
        "here": "I am",
        "yes": {
            "Recursion": "is fun?",
            "Nope": {
                "sometimes": "yes",
                "you": "hmmmm",
                "num": 5
            }
        }
    }

    path = is_valid(data, "Here?", "Yes")
    print(path)
