import requests
import re
from copy import deepcopy
from warnings import warn
from numbers import Number
from collections.abc import Iterable


###########################
#        Constants        #
###########################

C_DEG = ["°C", "℃"]
C_DEG_OR = f"({'|'.join(C_DEG)})"
DEG_REGEX = re.compile(
    f"((?P<low>-*\d+\.*\d*)\s*(to|-|\s+)*\s*(?P<high>-*\d+\.*\d*)*)\s*{C_DEG_OR}"
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
        self.name = self.data["Record"]["RecordTitle"]
        self.get_CAS()
        self.get_molecular_formula()
        self.get_MW()
        self.get_SMILES()
        self.bp = self.get_phase_transition_temperature("Boiling Point")
        self.mp = self.get_phase_transition_temperature("Melting Point")
        self.get_GHS_pictograms()
        self.get_NFPA704_diamond()
        self.get_hazard_statements()
        self.get_precaution_statements()

    def __str__(self):
        return f"""
Name: {self.name}
CAS: {self.CAS}
Molecular formula: {self.molecular_formula}
MW: {self.MW} g/mol
SMILES: {self.SMILES}
B.P: {format_temperature_range(self.bp)}
M.P: {format_temperature_range(self.mp)}
Pictograms: {','.join(self.GHS_pictograms)}
NFPA704 diamond: {self.NFPA704_diamond}
Hazard statements: {self.hazard_statements}
Precautionary statements: {self.precaution_statements}
******************************************
"""

    def get_data(self):
        resp = requests.get(url=self.data_url, params=self.rest_params)
        self.data = resp.json()

    def get_property(self, key, val):
        path = get_path(self.data, key, val)
        if path:
            property = nested_get(self.data, path)
        else:
            property = None
        return property

    def get_CAS(self):
        CAS_dict = self.get_property("TOCHeading", "CAS")
        if CAS_dict:
            self.CAS = CAS_dict["Information"][0]["Value"]["StringWithMarkup"][0]["String"]
        else:
            self.CAS = None

    def get_molecular_formula(self):
        formula = self.get_property("TOCHeading", "Molecular Formula")
        if formula:
            self.molecular_formula = formula["Information"][0]["Value"]["StringWithMarkup"][0]["String"]
        else:
            self.molecular_formula = None

    def get_MW(self):
        MW_dict = self.get_property("TOCHeading", "Molecular Weight")
        if MW_dict:
            self.MW = MW_dict["Information"][0]["Value"]["StringWithMarkup"][0]["String"]
        else:
            self.MW = None

    def get_SMILES(self):
        SMILES_dict = self.get_property("TOCHeading", "Canonical SMILES")
        if SMILES_dict:
            self.SMILES = SMILES_dict["Information"][0]["Value"]["StringWithMarkup"][0]["String"]
        else:
            self.SMILES = None
    #
    # def get_density(self):
    #     density_dict = self.get_property("TOCHeading", "Density")

    def get_phase_transition_temperature(self, type="Boiling Point"):
        if type not in ["Boiling Point", "Melting Point"]:
            warn("Wrong phase transition type!")
            return None
        pt_data = self.get_property("TOCHeading", type)
        if not pt_data:
            return None
        pt_list = pt_data["Information"]
        pt_candidates = []
        for pt in pt_list:
            if "StringWithMarkup" in pt["Value"]:
                candidate = pt["Value"]["StringWithMarkup"][0]["String"]
                if any_comp(C_DEG, candidate):
                    pt_candidates.append(candidate)
            elif "Number" in pt["Value"]:
                pt = float(pt["Value"]["Number"][0])
                return pt
            else:
                return None
        # Iterate until a pt range or value is found (if at all)
        # If one is found convert range/value to float(s),
        # otherwise return None
        for candidate in pt_candidates:
            if isinstance(candidate, float):
                return None
            elif isinstance(candidate, str):
                pt_try = DEG_REGEX.match(candidate)
                if pt_try is not None:
                    break
        if pt_try:
            return get_temperatures_from_string(pt_try)
        else:
            return None

    def get_GHS_pictograms(self):
        path = get_path(self.data, "Name", "Chemical Safety")
        if path:
            d = nested_get(self.data, path)
            self.GHS_pictograms = [
                x["Extra"]
                for x in d["Value"]["StringWithMarkup"][0]["Markup"]
            ]
        else:
            self.GHS_pictograms = []

    def get_NFPA704_diamond(self):
        path = get_path(self.data, "Name", "NFPA 704 Diamond")
        # print(path)
        if path:
            d = nested_get(self.data, path)
            self.NFPA704_diamond = [
                x.strip() for x in (
                    d["Value"]["StringWithMarkup"][0]
                    ["Markup"][0]["Extra"].split('-')
                )
            ]
        else:
            self.NFPA704_diamond = []

    def get_hazard_statements(self):
        statements = self.get_property("Name", "GHS Hazard Statements")
        if statements:
            self.hazard_statements = [
                int(x) for x in flatten([
                    re.findall(r"H(\d+):", s["String"])
                    for s in statements["Value"]["StringWithMarkup"]
                ])
            ]
        else:
            self.hazard_statements = None

    def get_precaution_statements(self):
        statements = self.get_property("Name", "Precautionary Statement Codes")
        # self.precaution_statements = None
        # return
        if statements:
            self.precaution_statements = statements["Value"]["StringWithMarkup"][0]["String"]
        else:
            self.precaution_statements = None


###########################
#        Functions        #
###########################


def any_comp(list, string):
    """
    Checks if any element in list is in string.
    """
    return any(element in string for element in list)

def convert(lst):
    """
    Converts a list to a dictionaty, where the i-th element
    gets [i] as its key.
    """
    return {
        index: element
        for index, element in enumerate(lst)
    }


def flatten(xs):
    """
    Completely flattens a nested list.
    """
    for x in xs:
        if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            yield from flatten(x)
        else:
            yield x


def find_path(dct, key, val):
    """
    Finds the first path to a wanted key:value pair
    in a nested dictionary which may contain lists.
    """
    if isinstance(dct, list) or isinstance(dct, tuple):
        d = convert(dct)
    elif isinstance(dct, dict):
        d = dct
    else:
        return None
    if key in d.keys() and d[key] == val:
        return key
    path = None
    for d_key in d.keys():
        r = find_path(d[d_key], key, val)
        if r is None:
            continue
        else:
            return [x for x in flatten([d_key] + [r])]
    return path


def get_path(dct, key, val):
    """
    Wrapper around "find_path" that returns the path
    minus the last element.
    TODO: write explaination.
    """
    path = find_path(dct, key, val)
    if path:
        return path[:-1]
    else:
        return path  # None


def nested_get(dict, keys):
    """
    Returns a value in a nested dictionary (which could also have
    nested lists in it) by a list of sequential keys. example:
    d = {'foo': {'bar': 4}}, nested_get(d, ['foo', 'bar']) -> 4.
    """
    d = deepcopy(dict)
    for key in keys:
        d = d[key]
    return d


def get_temperatures_from_string(T):
    if T:
        low_temp = float(T.group("low"))
        if T.group("high"):
            high_temp = float(T.group("high"))
            return (low_temp, high_temp)
        return low_temp
    return ""


def format_temperature_range(range):
    if isinstance(range, Number):
        return f"{range} °C"
    elif isinstance(range, list) or isinstance(range, tuple):
        return f"{range[0]}-{range[-1]} °C"
    elif range is None:
        return None
    else:
        raise ValueError(f"Range has irrelevant type: {type(range)}.")


if __name__ == "__main__":
    # for cid in [4133, 8028, 6228, 6386, 1548943, 180, 5793, 674, 8400, 7037, 4311764]:
    for cid in [6367]:
        c = Chemical(cid)
        print(c)
