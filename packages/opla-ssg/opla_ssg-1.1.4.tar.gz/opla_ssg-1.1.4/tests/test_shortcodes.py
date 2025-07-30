import json
from pathlib import Path

import pytest

from opla import shortcodes


class TestPublicationsHandlerHal:
    @pytest.fixture
    def setup_pub(self, request, mocker):
        # Mock HAL publications
        # Patch the get_json_dict function to return a JSON dict
        with open(
            Path(__file__).parent / "data" / "test_hal_response.json"
        ) as f:
            json_dict = json.load(f)
        mocker.patch(
            "opla.bibliography.get_json_dict",
            return_value=json_dict,
        )

        def unset_HAL_PUBLICATIONS():
            shortcodes.HAL_PUBLICATIONS = None

        request.addfinalizer(unset_HAL_PUBLICATIONS)

    def get_exception_message(self, kwargs: dict) -> str:
        with pytest.raises(shortcodes.ShortcodeError) as exception:
            shortcodes.publications_handler_hal(None, kwargs)

        return exception.value.args[0]

    def test_no_idhal_no_orcid(self, setup_pub):
        kwargs = {"doctype": "ART"}
        assert (
            self.get_exception_message(kwargs)
            == "publications_hal shortcode: idhal or orcid is a required argument"
        )

    def test_no_doctype(self, setup_pub):
        kwargs = {"idhal": "any_idhal"}
        assert (
            self.get_exception_message(kwargs)
            == "publications_hal shortcode: doctype is a required argument"
        )

    def test_unknown_doctype(self, setup_pub):
        kwargs = {"idhal": "any_idhal", "doctype": "PUB"}
        assert (
            self.get_exception_message(kwargs)
            == "Publications_hal shortcode: doctype PUB not found in HAL publications"
        )

    def test_publications_handler(self, setup_pub):
        # Test with idhal
        kwargs = {"idhal": "any_idhal", "doctype": "ART"}
        content = shortcodes.publications_handler_hal(None, kwargs)
        assert "Micromagnetic simulations of the size" in content
        # Test with orcid
        kwargs = {"orcid": "any_orcid", "doctype": "ART"}
        content = shortcodes.publications_handler_hal(None, kwargs)
        assert "Micromagnetic simulations of the size" in content


class TestPublicationsHandlerBibtex:
    @pytest.fixture
    def file(self, tmp_path):
        data = """
                @article{heu:hal-03546417,
    TITLE = {{Holomorphic Connections on Filtered Bundles over Curves}},
    AUTHOR = {Heu, Viktoria and Biswas, Indranil},
    URL = {https://hal.science/hal-03546417},
    JOURNAL = {{Documenta Mathematica}},
    PUBLISHER = {{Universit{\"a}t Bielefeld}},
    YEAR = {2013},
    KEYWORDS = {2010 Mathematics Subject Classification: 14H60 ; 14F05 ; 53C07 Keywords and Phrases: Holomorphic connection ; filtration ; Atiyah bundle ; parabolic subgroup},
    HAL_ID = {hal-03546417},
    HAL_VERSION = {v1},
    }
                """
        with open(tmp_path / "test.html", "w") as f:
            f.write(data)

        yield tmp_path / "test.html"

    def test_all_types(self, file):
        kwargs = {"bibtex": file}
        res = shortcodes.publications_handler_bibtex(None, kwargs, None)
        assert "Holomorphic Connections on Filtered Bundles over Curves" in res

    def test_article_type(self, file):
        kwargs = {"bibtex": file, "type": "article"}
        res = shortcodes.publications_handler_bibtex(None, kwargs, None)
        assert "Holomorphic Connections on Filtered Bundles over Curves" in res

    def test_book_type(self, file):
        kwargs = {"bibtex": file, "type": "book"}
        res = shortcodes.publications_handler_bibtex(None, kwargs, None)
        assert res == ""
