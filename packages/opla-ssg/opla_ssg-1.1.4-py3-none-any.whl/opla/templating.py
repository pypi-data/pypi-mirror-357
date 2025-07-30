"""Provide a function to get the jinja template."""

import logging
from pathlib import Path

import jinja2

from . import THEMES

logger = logging.getLogger(__name__)

TEMPLATES_PATH = Path(__file__).parent / "themes"


def get_template(config: dict) -> jinja2.Template:
    """
    Get the appropriate template according to the theme configuration

    Args:
        config: the site configuration dictionary

    Returns:
        jinja2.Template: the requested template
    """

    theme_config = config["theme"]
    theme_name = theme_config["name"]

    if theme_name not in THEMES:
        raise ValueError(f"Unknown theme name: '{theme_name}'")

    theme_choices = []
    # Add custom templates directory if it exists
    if "custom" in theme_config:
        custom_templates_path = Path(theme_config["custom"]) / "templates"
        if custom_templates_path.exists():
            logger.info(f"Using custom templates: {custom_templates_path}")
            custom_loader = jinja2.FileSystemLoader(
                Path(custom_templates_path)
            )
            theme_choices.append(custom_loader)
        else:
            logger.debug("No custom templates found")

    base_loader = jinja2.FileSystemLoader(
        TEMPLATES_PATH / "base" / "templates"
    )
    theme_loader = jinja2.FileSystemLoader(
        TEMPLATES_PATH / theme_name / "templates"
    )
    theme_choices.extend([theme_loader, base_loader])

    env = jinja2.Environment(loader=jinja2.ChoiceLoader(theme_choices))
    template = env.get_template("index.html.j2")

    return template
