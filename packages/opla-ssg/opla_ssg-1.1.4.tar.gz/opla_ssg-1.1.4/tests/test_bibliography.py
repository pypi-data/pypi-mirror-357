import json
from pathlib import Path

import pytest

from opla import bibliography


def test_get_publications_noidhal_norocid():
    with pytest.raises(ValueError) as exception:
        bibliography.get_publications()

    assert exception.value.args[0] == "idhal or orcid must be provided"


def test_publications(mocker):
    # Patch the get_json_dict function to return a JSON dict
    with open(Path(__file__).parent / "data" / "test_hal_response.json") as f:
        json_dict = json.load(f)
    mocker.patch(
        "opla.bibliography.get_json_dict",
        return_value=json_dict,
    )
    for kwargs in ({"idhal": "any_idHal"}, {"orcid": "any_orcid"}):
        publications = bibliography.get_publications(**kwargs)
        assert isinstance(publications, dict)
        assert "ART" in publications
        assert "COMM" in publications
        assert (
            "Clémentine Courtès, Matthieu Boileau, Raphaël Côte, Paul Antoine Hervieux, Giovanni Manfredi."
            in publications["ART"][0]
        )
