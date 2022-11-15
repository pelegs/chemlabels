import requests
from sys import argv
import re
from copy import deepcopy


##############################
#        URL settings        #
##############################

url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{argv[1]}/JSON/"
params = dict(
    response_type="display",
)
resp = requests.get(url=url, params=params)
data = resp.json()


###########################
#        Functions        #
###########################


def search_dict(d, searched_key, searched_val, path=[]):
    """
    Returns the first path in a nested dictionary/list which ends
    with a key, value pair. The condition to stop the recursion is when
    the pair is found, and the mechanism is by appending "END" to the list.
    """
    if len(path) > 0 and path[-1] == "END":
        return
    if isinstance(d, dict):
        for key, val in d.items():
            path.append(key)
            if key == searched_key and val == searched_val:
                path.append("END")
                return
            search_dict(d[key], searched_key, searched_val, path)
            if path[-1] != "END":
                path.pop()
    elif isinstance(d, list):
        for i, _ in enumerate(d):
            path.append(i)
            search_dict(d[i], searched_key, searched_val, path)
            if path[-1] != "END":
                path.pop()
    return path[:-2]  # both "END" and the searched pair aren't needed


def nested_get(dict, keys):
    """
    Returns a value in a nested dictionary (which could also have
    nested lists in it) by a list of sequential keys. example:
    d = {'foo': {'bar': 4}}, nested_get(d, ['foo', 'barr']) -> 4.
    """
    d = deepcopy(dict)
    for key in keys:
        d = d[key]
    return d


#######################
#        regex        #
#######################

fraction_regex = r"-*\d+\.*\d*"


#####################################
#        Physical properties        #
#####################################

path = list()
path = search_dict(data, "TOCHeading", "Boiling Point", path)
print(path)
print(nested_get(data, path))

path2 = list()
path2 = search_dict(data, "TOCHeading", "Melting Point", path2)
print(path2)
print(nested_get(data, path2))

path3 = list()
path3 = search_dict(data, "TOCHeading", "Density", path3)
print(path3)
print(nested_get(data, path3))

path4 = list()
path4 = search_dict(data, "TOCHeading", "GHS Classification", path4)
print(path4)
print(nested_get(data, path4))

path5 = list()
path5 = search_dict(data, "Name", "NFPA 704 Diamond", path5)
print(path5)
print(nested_get(data, path5[:-3]))
