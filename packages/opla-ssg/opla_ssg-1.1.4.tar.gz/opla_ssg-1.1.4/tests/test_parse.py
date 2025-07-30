from pathlib import Path
from textwrap import dedent

import pytest

from opla import parse


@pytest.fixture
def theme():
    return "theme:\n    name: materialize"


class TestParseMarkdownFile:
    @pytest.fixture
    def setup_dir(self, tmp_path, theme) -> Path:
        """Create a markdown file with a header and sections for testing"""
        data = f"""\
---
title: Ma page perso
name: Erica
occupation: Chargée de recherche
{theme}
---

## Section 1

Section 1 content

## Section 2

### Section 2.1

Section 2.1 content

### Section 2.2

Section 2.2 content
Section 2.2 content

## Section 3

Section 3 content
"""
        with open(tmp_path / "test.md", "w") as f:
            f.write(data)
        mdfilepath = tmp_path / Path("test.md")

        return mdfilepath

    @pytest.mark.parametrize(
        "theme",
        ["", "theme:\n    name: materialize", "", "theme:\n    name: rawhtml"],
    )
    def test_parse_file_header(self, setup_dir, theme):
        header, _, _ = parse.parse_file(setup_dir)

        expected = {
            "title": "Ma page perso",
            "name": "Erica",
            "occupation": "Chargée de recherche",
            "theme": {"name": "water"},
        }

        if theme == "theme:\n    name: rawhtml":
            expected["theme"] = {"name": "rawhtml"}
            assert header == expected
        elif theme == "theme:\n    name: materialize":
            expected["theme"] = {"name": "materialize", "color": "teal"}
            assert header == expected
        else:
            assert header == expected

    def test_process_theme(self):
        config = {}
        parse.process_theme(config)
        assert config["theme"] == {"name": "water"}

        config = {"theme": {"name": "materialize"}}
        parse.process_theme(config)
        assert config["theme"] == {"name": "materialize", "color": "teal"}

        config = {"theme": {"name": "materialize", "color": "red"}}
        parse.process_theme(config)
        assert config["theme"] == {"name": "materialize", "color": "red"}

    def test_process_favicon(self):
        config = {}
        parse.process_favicon(config)
        assert "favicon" not in config

        favicon_icon_dict = {
            "rel": "icon",
            "href": "img/favicon-96x96.png",
            "type": "image/png",
            "sizes": "96x96",
        }
        favicon_apple_touch_dict = {
            "rel": "apple-touch-icon",
            "href": "img/apple-touch-icon.png",
        }

        # favicon is a dict
        config = {"theme": {"favicon": favicon_icon_dict}}
        parse.process_favicon(config)
        assert config["theme"]["favicon"] == [favicon_icon_dict]

        # favicon is a list
        config = {
            "theme": {"favicon": [favicon_icon_dict, favicon_apple_touch_dict]}
        }
        parse.process_favicon(config)
        assert config["theme"]["favicon"] == [
            favicon_icon_dict,
            favicon_apple_touch_dict,
        ]

        # favicon is not a list or a dict
        config = {"theme": {"favicon": "favicon"}}
        with pytest.raises(parse.ParseError) as e:
            parse.process_favicon(config)
            # check that the error message is correct
            assert str(e) == "Favicon config must be a list or a dict"

        # missing rel in favicon
        config = {"theme": {"favicon": [{"href": "img/favicon-96x96.png"}]}}
        with pytest.raises(parse.ParseError) as e:
            parse.process_favicon(config)
            # check that the error message is correct
            assert str(e) == "Missing rel in favicon config"

        # missing href in favicon
        config = {"theme": {"favicon": [{"rel": "icon"}]}}
        with pytest.raises(parse.ParseError) as e:
            parse.process_favicon(config)
            # check that the error message is correct
            assert str(e) == "Missing href in favicon config"

    def test_parse_file_sections(self, setup_dir):
        expected = [
            {
                "content": dedent(
                    """
                <p>Section 1 content</p>
                """
                ),
                "id": "section-1",
                "title": "Section 1",
            },
            {
                "content": dedent(
                    """
                <h3>Section 2.1</h3>
                <p>Section 2.1 content</p>
                <h3>Section 2.2</h3>
                <p>Section 2.2 content
                Section 2.2 content</p>
                """
                ),
                "id": "section-2",
                "title": "Section 2",
            },
            {
                "content": "\n<p>Section 3 content</p>",
                "id": "section-3",
                "title": "Section 3",
            },
        ]
        _, sections, _ = parse.parse_file(setup_dir)

        assert sections == expected

    def test_parse_file_menu(self, setup_dir):
        expected = [
            {"href": "#section-2", "text": "Section 2"},
            {"href": "#section-3", "text": "Section 3"},
        ]
        _, _, menu = parse.parse_file(setup_dir)
        assert menu == expected

    def test_get_custom_static_files(self):
        test_path = Path(__file__).parent
        config = {
            "theme": {
                "name": "materialize",
                "custom": (test_path / "custom_theme").as_posix(),
            }
        }
        parse.get_custom_static_files(config)
        assert config["theme"]["custom_css_files"] == [
            Path("css/index.css"),
            Path("css/index2.css"),
        ]
        assert config["theme"]["custom_js_files"] == [
            Path("js/bootstrap.min.js")
        ]

    def test_process_footer(self):
        config = {
            "footer": {
                "contact": [
                    "<jlrda@dix-huitieme-siecle.fr>",
                    "Six feet under the carrefour de Chateaudun-Place Kossuth, 75009 Paris, France",
                    "+33 1 01 02 03 04",
                ],
            },
        }
        parse.process_config(config)
        assert config["footer"]["contact"] == [
            '<a href="&#109;&#97;&#105;&#108;&#116;&#111;&#58;&#106;&#108;&#114;&#100;&#97;&#64;&#100;&#105;&#120;&#45;&#104;&#117;&#105;&#116;&#105;&#101;&#109;&#101;&#45;&#115;&#105;&#101;&#99;&#108;&#101;&#46;&#102;&#114;">&#106;&#108;&#114;&#100;&#97;&#64;&#100;&#105;&#120;&#45;&#104;&#117;&#105;&#116;&#105;&#101;&#109;&#101;&#45;&#115;&#105;&#101;&#99;&#108;&#101;&#46;&#102;&#114;</a>',
            "Six feet under the carrefour de Chateaudun-Place Kossuth, 75009 Paris, France",
            "+33 1 01 02 03 04",
        ]
