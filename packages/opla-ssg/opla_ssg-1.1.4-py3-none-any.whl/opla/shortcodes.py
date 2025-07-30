"""Handle shortcodes for generating publications list from HAL and from BibTeX files"""

import io
from typing import Dict, List, Optional

import shortcodes  # type: ignore
from pybtex.plugin import find_plugin  # type: ignore

from opla.bibliography import (
    MyBackend,
    MySortingStyle,
    MyStyle,
    get_publications,
)

HAL_PUBLICATIONS: Optional[Dict[str, List[str]]] = None

parser = shortcodes.Parser(start="{{%", end="%}}", esc="\\")


class ShortcodeError(Exception):
    """Custom exception for shortcode errors"""

    pass


@shortcodes.register("publications_hal")
def publications_handler_hal(_, kwargs: dict) -> str:
    """
    Generate a list of publications sorted by the document type

    Args:
        _: unused positional argument
        kwargs: keyword arguments (may contain idhal or orcid and doctype)

    Returns:
        str: The list of the selected type of document publications
    """

    global HAL_PUBLICATIONS

    idhal = kwargs.get("idhal")
    orcid = kwargs.get("orcid")
    if idhal is None and orcid is None:
        raise ShortcodeError(
            "publications_hal shortcode: idhal or orcid is a required argument"
        )

    try:
        doctype = kwargs["doctype"]
    except KeyError:
        raise ShortcodeError(
            "publications_hal shortcode: doctype is a required argument"
        )

    # Retrieve the publications from HAL if not already done
    # (use global variable to avoid multiple API requests)
    if HAL_PUBLICATIONS is None:
        HAL_PUBLICATIONS = get_publications(idhal=idhal, orcid=orcid)
    try:
        publications = HAL_PUBLICATIONS[doctype]
        content = "\n- " + "\n- ".join(publications)
    except KeyError:
        raise ShortcodeError(
            f"Publications_hal shortcode: doctype {doctype} not found in HAL publications"
        )
    return content


@shortcodes.register("publications_bibtex")
def publications_handler_bibtex(_, kwargs: dict, __) -> str:
    """
    Generate a table of publications from a bibtex file

    Args:
        _: unused positional argument
        kwargs: keyword arguments
        __: unused context

    Returns:
        str: the list of the publications
    """

    file = kwargs["bibtex"]
    bib_parser = find_plugin("pybtex.database.input", "bibtex")
    bib_data = bib_parser().parse_file(file)

    entry_type = kwargs.get("type")
    # Keep only the entries of the selected type
    if entry_type:
        bib_data.entries = {
            key: entry
            for key, entry in bib_data.entries.items()
            if entry.type == entry_type
        }

    style = MyStyle()
    style.sort = MySortingStyle().sort
    data_formatted = style.format_entries(bib_data.entries.values())
    output = io.StringIO()
    MyBackend().write_to_stream(data_formatted, output)

    return output.getvalue()


parser.register(publications_handler_hal, "publications_hal")
parser.register(publications_handler_bibtex, "publications_bibtex")
