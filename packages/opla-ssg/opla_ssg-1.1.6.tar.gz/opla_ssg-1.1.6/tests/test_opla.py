from pathlib import Path
import subprocess
import sys

from opla import opla, __version__


def test_argparse():
    parser = opla.get_parser()

    args = parser.parse_args([])
    assert args.mdfile == opla.DEFAULT_MD_FILE
    assert args.output == Path("build")

    args = parser.parse_args(["mysite.md"])
    assert args.mdfile == Path("mysite.md")

    args = parser.parse_args(["-o", "output"])
    assert args.output == Path("output")


def test_version_argument():
    """Test that --version and -V arguments work correctly"""
    # Test long option --version
    result = subprocess.run(
        [sys.executable, "-m", "opla", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == f"opla {__version__}"

    # Test short option -V
    result = subprocess.run(
        [sys.executable, "-m", "opla", "-V"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == f"opla {__version__}"


def test_main(tmp_path):
    data = """\
---
title: Ma page perso
name: Joanna
occupation: Chargée de recherche
theme:
    name: materialize
    color: teal
---
## Section 1

Section 1 content - Section 1 content Section 1 content - Section 1 content Section 1 content - Section 1 content
Section 1 content - Section 1 content
Section 1 content - Section 1 content

## Section 2

### Section 2.1

Section 2.1 content Section 2.1 content - Section 2.1 content

### Section 2.2

Section 2.2 content Section 2.2 content - Section 2.2 content
Section 2.2 content Section 2.2 content - Section 2.2 content"""

    with open(tmp_path / "test.md", "w") as f:
        f.write(data)
    file = tmp_path / "test.md"
    dir = tmp_path / "dirtest"
    sys.argv = ["opla", str(file), "-o", str(dir)]
    opla.main()
    assert (dir / "index.html").is_file()

    # Test file not found
    sys.argv = ["opla", "afilethatdoesnotexist.md"]
    code = opla.main()
    assert code == 1

    # Execute opla as a module
    result = subprocess.run(
        [sys.executable, "-m", "opla", str(file)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert (dir / "index.html").is_file()

    # Test file not found
    result = subprocess.run(
        [sys.executable, "-m", "opla", "afilethatdoesnotexist.md"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
