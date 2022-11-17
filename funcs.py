import requests
import re
from copy import deepcopy


###########################
#        Constants        #
###########################

C_DEG = ["°C", "℃"]
C_DEG_OR = f"({'|'.join(C_DEG)})"
DEG_REGEX = re.compile(
    f"((?P<low>-*\d+\.*\d*)\s*(to|\s+)*\s*(?P<high>-*\d+\.*\d*)*)\s*{C_DEG_OR}"
)


#######################
#        Class        #
#######################


class Chemical:
    def __init__(self, cid):
        self.cid = cid
        self.data_url = (
            "https://pubchem.ncbi.nlm.nih.gov"
            f"/rest/pug_view/data/compound/{self.cid}/JSON/"
        )
        self.rest_params = dict(response_type="display")
        self.get_data()

    def get_data(self):
        resp = requests.get(url=self.data_url, params=self.rest_params)
        self.data = resp.json()

    def get_property(self, key, val):
        path = search_dict(self.data, key, val)
        property = nested_get(self.data, path)
        return property

    def get_bp(self):
        bp_data = self.get_property("TOCHeading", "Boiling Point")
        bp_list = bp_data["Information"]
        bp_candidates = []
        for bp in bp_list:
            if "StringWithMarkup" in bp["Value"]:
                candidate = bp["Value"]["StringWithMarkup"][0]["String"]
                if any_comp(C_DEG, candidate):
                    bp_candidates.append(candidate)
        # Iterate until a bp range or value is found (if at all)
        # If one is found convert range/value to float(s),
        # otherwise return None
        for candidate in bp_candidates:
            bp_try = DEG_REGEX.match(candidate)
            if bp_try is not None:
                break
        if bp_try:
            self.bp = get_temperatures(bp_try)
        else:
            self.bp = None

        # TEMP
        print(self.bp)


###########################
#        Functions        #
###########################


def any_comp(list, string):
    """
    Checks if any element in list is in string
    """
    return any(element in string for element in list)


def get_val_from_key_list(d, searched_key, searched_val, path=[]):
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
            get_val_from_key_list(d[key], searched_key, searched_val, path)
            if path[-1] != "END":
                path.pop()
    elif isinstance(d, list):
        for i, _ in enumerate(d):
            path.append(i)
            get_val_from_key_list(d[i], searched_key, searched_val, path)
            if path[-1] != "END":
                path.pop()
    return path[:-2]  # both "END" and the searched pair aren't needed


def search_dict(d, key, val):
    """
    Wrapper for get_val_from_key_list so that path is returned
    directly, without the need to create a new list object each time.
    """
    path = list()
    path = get_val_from_key_list(d, key, val, path)
    return path


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


def get_temperatures(T):
    if T:
        low_temp = float(T.group('low'))
        if T.group('high'):
            high_temp = float(T.group('high'))
            return (low_temp, high_temp)
        return low_temp
    return ''


if __name__ == "__main__":
    # ms = Chemical(4133)
    # ms = Chemical(8028)
    # ms = Chemical(6228)
    # ms = Chemical(6386)
    # ms = Chemical(1548943)
    ms = Chemical(180)
    ms.get_bp()
