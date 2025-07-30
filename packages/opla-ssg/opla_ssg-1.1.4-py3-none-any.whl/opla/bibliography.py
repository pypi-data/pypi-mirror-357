"""Retrieve publications from HAL and handle publications list style format"""

import json
from urllib import request

from pybtex.backends.markdown import Backend  # type: ignore
from pybtex.style.formatting.plain import Style  # type: ignore
from pybtex.style.sorting import BaseSortingStyle  # type: ignore
from pybtex.style.template import field, href, join, optional, sentence  # type: ignore


class MyBackend(Backend):
    """Output the entry in a markdown list"""

    def write_entry(self, key, label, text):
        self.output(f"- {text}\n")


class MySortingStyle(BaseSortingStyle):
    """Sort entries by year in descending order"""

    def sorting_key(self, entry):
        return entry.fields["year"]

    def sort(self, entries):
        return sorted(entries, key=self.sorting_key, reverse=True)


class MyStyle(Style):
    """A custom class to display the HAL reference"""

    def format_web_refs(self, e):
        """Add HAL ref based on urlbst output.web.refs"""
        return sentence[
            optional[self.format_eprint(e)],
            optional[self.format_pubmed(e)],
            optional[self.format_doi(e)],
            optional[self.format_idhal(e)],
        ]

    def format_idhal(self, e):
        """Format HAL ref based on urlbst format.doi"""
        url = join[" https://hal.science/", field("hal_id", raw=True)]
        return href[url, join["hal:", field("hal_id", raw=True)]]


def get_json_dict(url: str) -> dict[str, list[str]]:
    """
    Get a JSON dictionnary from an URL

    Args:
        url: The URL to retrieve the JSON

    Returns:
        dict: The JSON dictionnary
    """
    f = request.urlopen(url)  # pragma: no cover
    return json.loads(f.read())  # pragma: no covers


def get_publications(
    idhal: str | None = None, orcid: str | None = None
) -> dict[str, list[str]]:
    """
    Get the list of publications sorted by the document type, based on
    the IDHal or the ORCID of the author by questionning HAL

    Args:
        idhal: The IDHal of the author
        orcid: The ORCID of the author

    Returns:
        dict: A dictionnary containing the publications retrieved
                  from the HAL API sorted by document type
    """
    if idhal:
        query = f"authIdHal_s:{idhal}"
    elif orcid:
        query = f"authORCIDIdExt_id:{orcid}"
    else:
        raise ValueError("idhal or orcid must be provided")

    url = (
        f"https://api.archives-ouvertes.fr/search/?q={query}"
        r"&wt=json&fl=docType_s,citationFull_s&rows=10000"
        r"&sort=publicationDate_tdate%20desc"
    )

    jsondict = get_json_dict(url)

    pub_list = jsondict["response"]["docs"]
    # Create a {docType: [pub_str]} dictionnary
    pub_dict: dict[str, list[str]] = {}
    for pub in pub_list:
        if pub["docType_s"] in pub_dict:
            pub_dict[pub["docType_s"]].append(pub["citationFull_s"])
        else:
            pub_dict[pub["docType_s"]] = [pub["citationFull_s"]]
    return pub_dict
