"""
Main module for the opla package
"""

import argparse
import logging
import sys
from pathlib import Path

from . import __version__
from .parse import parse_file
from .payload import copy_payload, create_output_directory
from .templating import get_template

logger = logging.getLogger(__name__)

DEFAULT_MD_FILE = Path("opla.md")


def get_parser():
    """
    Return the parser for the opla command-line interface

    Returns:
        argparse.ArgumentParser: the parser for the opla command-line interface
    """
    parser = argparse.ArgumentParser(
        description=(
            "A professional webpage generator with a focus "
            "on research activities"
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "mdfile",
        nargs="?",
        type=Path,
        help="markdown file path",
        default=DEFAULT_MD_FILE,
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("build"),
        help="output directory",
    )
    parser.add_argument(
        "--debug", action="store_true", help="enable debug logging"
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"opla {__version__}"
    )

    return parser


def main():
    """
    Generates a personal page by parsing command-line arguments,
    creating the page content and its menu, renders the HTML template,
    and writes the result into a HTML file
    """
    parser = get_parser()
    args = parser.parse_args(sys.argv[1:])

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    output_directory_path = args.output
    md_file = args.mdfile

    try:
        config, sections, menu = parse_file(md_file)
    except FileNotFoundError:
        # print argparse help message
        logger.error(f"File not found: {md_file}\n")
        parser.print_help()
        return 1

    create_output_directory(output_directory_path)
    copy_payload(config, output_directory_path)

    template = get_template(config)
    html_out = template.render(
        opla_version=__version__,
        config=config,
        sections=sections,
        menu=menu,
        output=output_directory_path,
    )

    with open(output_directory_path / "index.html", "w") as f:
        f.write(html_out)
        logger.info(
            f"Webpage generated at {output_directory_path / 'index.html'}"
        )


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
