from pathlib import Path
from textwrap import dedent

import pytest

from opla import parse, opla, payload, templating


class TestGetTemplate:
    def test_materialize(self):
        config = {"theme": {"name": "materialize"}}
        template = opla.get_template(config)
        assert (
            Path(template.filename)
            == templating.TEMPLATES_PATH
            / "materialize/templates/index.html.j2"
        )

    def test_rawhtml(self):
        config = {"theme": {"name": "rawhtml"}}
        template = opla.get_template(config)
        assert Path(template.filename) == templating.TEMPLATES_PATH / Path(
            "rawhtml/templates/index.html.j2"
        )

    def test_unknown_theme(self):
        config = {"theme": {"name": "doesnotexist"}}
        with pytest.raises(
            ValueError, match=r"Unknown theme name: 'doesnotexist'"
        ):
            opla.get_template(config)


def test_social_media(tmp_path):
    config, _, _ = parse.parse_file(Path(__file__).parent / "example_media.md")
    template = templating.get_template(config)
    output_directory_path = tmp_path / "output"
    payload.copy_payload(config, output_directory_path)

    html_out = template.render(
        sections=[],
        config=config,
        menu=[],
        output=output_directory_path,
    )
    footer_extract = """\
        <footer class="page-footer teal">
        <div class="container">

            <div id="social" style="margin: 2rem 0 2rem 0;">

                <a href="https://www.github.com/jlrda" style="padding-right: 1rem; text-decoration: none">
                    <i aria-hidden="true" class="fa-brands fa-github fa-2xl"
                        style="color: white;"></i>
                    <span class="fa-sr-only">Link to my github account</span>
                </a>

                <a href="https://www.researchgate.com/jlrda" style="padding-right: 1rem; text-decoration: none">
                    <i aria-hidden="true" class="fa-brands fa-researchgate fa-2xl"
                        style="color: black;"></i>
                    <span class="fa-sr-only">Link to my researchgate account</span>
                </a>

                <a href="https://www.twitter.com/jlrda" style="padding-right: 1rem; text-decoration: none">
                    <i aria-hidden="true" class="fa-brands fa-twitter fa-2xl"
                        style="color: black;"></i>
                    <span class="fa-sr-only">Link to my twitter account</span>
                </a>

                <a href="https://www.gitlab.inria.fr/jlrda" style="padding-right: 1rem; text-decoration: none">
                    <i aria-hidden="true" class="fa-brands fa-gitlab fa-2xl"
                        style="color: black;"></i>
                    <span class="fa-sr-only">Link to my gitlab account</span><span>Inria</span>
                </a>

            </div>

        </div>"""
    assert footer_extract in html_out


def test_custom(tmp_path):
    # Test custom templates
    config, _, _ = parse.parse_file(Path(__file__).parent / "example_logos.md")
    # Rewrite the template path to use an absolute path
    config["theme"]["custom"] = Path(__file__).parent / "custom_theme"
    parse.get_custom_static_files(config)
    template = templating.get_template(config)
    output_directory_path = tmp_path / "output"
    payload.copy_payload(config, output_directory_path)

    html_out = template.render(
        sections=[],
        config=config,
        menu=[],
        output=output_directory_path,
    )
    footer_extract = """\
            <div id="logos" style="margin: 2rem 0 2rem 0;">
                <a href="https://en.wikipedia.org/wiki/Jean_le_Rond_d%27Alembert" style="padding-right: 1rem;">
                    <img src="https://portrait_dAlembert.jpg" alt="Jean Le Rond d'Alembert" style="height: 5rem; padding-top: 1rem">
                </a>
                <a href="https://www.example.com" style="padding-right: 1rem;">
                    <img src="img/300.png" alt="Fake logo" style="height: 5rem; padding-top: 1rem">
                </a>
            </div>
"""
    assert footer_extract in html_out


def test_custom_no_template_dir(tmp_path):
    config = {"theme": {"name": "rawhtml", "custom": "doesnotexist"}}
    template = templating.get_template(config)
    package_path = Path(opla.__file__).parent
    expected_template_path = (
        package_path / "themes" / "rawhtml" / "templates" / "index.html.j2"
    )
    assert Path(template.filename).relative_to(
        package_path
    ) == expected_template_path.relative_to(package_path)


def test_favicon(tmp_path):
    config, _, _ = parse.parse_file(
        Path(__file__).parent / "example_favicon.md"
    )
    template = templating.get_template(config)
    output_directory_path = tmp_path / "output"

    html_out = template.render(
        sections=[],
        config=config,
        menu=[],
        output=output_directory_path,
    )
    favicon_rel_icon_extract = dedent(
        """<link rel="icon" type="image/png" href="img/favicon-96x96.png" sizes="96x96">"""
    )
    assert favicon_rel_icon_extract in html_out

    favicon_apple_icon_extract = dedent(
        """<link rel="apple-touch-icon" href="img/apple-touch-icon.png">"""
    )
    assert favicon_apple_icon_extract in html_out
