"""
Parse markdown file into header and sections and create menu from sections
"""

import logging
from pathlib import Path

from markdown_link_attr_modifier import LinkAttrModifierExtension
from mdslicer import MDSlicer

from .shortcodes import parser

logger = logging.getLogger(__name__)

slicer = MDSlicer(
    extensions=["attr_list", LinkAttrModifierExtension()],
    additional_parser=parser.parse,
)


class ParseError(Exception):
    pass


def parse_file(mdfile_path: Path) -> tuple[str, list[dict], list[dict]]:
    """
    Parse a markdown file into a config dict and a list of sections

    Args:
        mdfile_path: Path to the markdown file

    Returns:
        (config of the markdown file, content sections of the markdown file, menu items)
    """
    slicer = MDSlicer(
        extensions=["attr_list", LinkAttrModifierExtension()],
        additional_parser=parser.parse,
    )
    config, sections = slicer.slice_file(mdfile_path)
    process_config(config)
    menu = create_menu(sections)
    return config, sections, menu


def process_favicon(config: dict) -> None:
    """
    Check if favicon is present in the config dict

    Args:
        config: opla config dict
    """
    try:
        favicon = config["theme"]["favicon"]

        # transform favicon into a list if it is a dict
        if not isinstance(favicon, list):
            if isinstance(favicon, dict):
                config["theme"]["favicon"] = [favicon]
            else:
                raise ParseError("Favicon config must be a list or a dict")

        # rel and href must be present in each favicon config
        for favicon_rel in config["theme"]["favicon"]:
            for key in "rel", "href":
                if key not in favicon_rel:
                    raise ParseError(f"Missing {key} in favicon config")
    except KeyError:
        logger.debug("No favicon section found in config")


def process_theme(config: dict) -> None:
    """
    Process the theme section of the config dict

    Args:
        config: opla config dict
    """
    # Add theme to config if not presentx
    if "theme" not in config:
        config["theme"] = {}

    # Default theme is water
    if "name" not in config["theme"]:
        config["theme"]["name"] = "water"

    # Add default color to materialize theme
    if config["theme"]["name"] == "materialize":
        config["theme"]["color"] = config["theme"].get("color", "teal")

    process_favicon(config)

    # Add custom css and js files to custom theme
    get_custom_static_files(config)


def get_custom_static_files(config: dict):
    """
    Add css and js file paths to config["theme"]["custom"] dict

    Args:
        config: opla config dict
    """
    try:
        custom_path: Path = Path(config["theme"]["custom"])
    except KeyError:
        return

    if not custom_path.is_dir():
        logger.error(f"Custom theme path {custom_path} does not exist")

    custom_static_path = custom_path / "static"
    if custom_static_path.is_dir():
        logger.debug(f"Found custom static files in {custom_static_path}")
        # List all css and js files from custom static path
        css_files = custom_static_path.glob("**/*.css")
        config["theme"]["custom_css_files"] = [
            path.relative_to(custom_static_path) for path in css_files
        ]
        js_files = custom_static_path.glob("**/*.js")
        config["theme"]["custom_js_files"] = [
            path.relative_to(custom_static_path) for path in js_files
        ]
    else:
        logger.debug(f"No custom static files found in {custom_static_path}")
        config["theme"]["custom_css_files"] = []
        config["theme"]["custom_js_files"] = []


def process_footer(config: dict) -> None:
    """Process the footer section of the config dict

    Args:
        config: opla config dict
    """
    # Convert markdown lists to HTML in footer
    try:
        contact_list = config["footer"]["contact"]
    except KeyError:
        return
    # Remove <p> and </p> tags
    config["footer"]["contact"] = [
        slicer.md.convert(md_element)[3:-4] for md_element in contact_list
    ]


def process_config(config: dict) -> None:
    """
    Process the opla config dict

    Args:
        config: opla config dict
    """
    process_theme(config)
    process_footer(config)


def create_menu(sections: list[dict]) -> list[dict]:
    """
    Create a menu from a collection of sections

    Args:
        sections: Sections of the markdown with an id and a title

    Returns:
        A list of menu items with a link href and a text
    """
    menu_links = []
    for section in sections[1:]:
        if section["id"]:
            menu_links.append(
                {"href": f"#{section['id']}", "text": section["title"]}
            )

    return menu_links
