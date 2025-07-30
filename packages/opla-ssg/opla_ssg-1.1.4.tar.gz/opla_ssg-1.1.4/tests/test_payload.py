from pathlib import Path

import pytest

from opla import parse, payload

TEST_PATH = Path(__file__).parent


def test_create_output_directory(tmp_path):
    dir = tmp_path / Path("output")
    payload.create_output_directory(dir)
    assert dir.exists()

    # Check if the directory exists
    file = dir / "coco.txt"
    file.touch()

    # Create the directory again
    payload.create_output_directory(dir)
    assert dir.exists()


@pytest.fixture
def setup_dir(tmp_path):
    dir = payload.create_output_directory(tmp_path / Path("dir"))
    return dir


def test_copy_file(setup_dir):
    # Copy a file
    src = TEST_PATH / "custom_theme" / "static" / "css" / "index2.css"
    payload.copy(src, setup_dir)
    assert (setup_dir / "index2.css").is_file()


def test_copy_dir(setup_dir):
    # Copy a directory
    src = TEST_PATH / "data" / "img"
    dst_path = setup_dir / "img"
    payload.copy(src, dst_path)
    assert dst_path.exists()


def test_materialize(setup_dir):
    config = {"theme": {"name": "materialize"}}
    payload.copy_static_files(config, setup_dir)
    assert (setup_dir / "materialize" / "static").exists()
    assert (setup_dir / "materialize" / "static" / "css").exists()
    assert (setup_dir / "materialize" / "static" / "js").exists()


def test_water(setup_dir):
    config = {"theme": {"name": "water"}}
    payload.copy_static_files(config, setup_dir)
    assert (setup_dir / "water" / "static").exists()


def test_copy_custom_static_files(setup_dir):
    config = {
        "theme": {
            "custom": (TEST_PATH / "custom_theme").as_posix(),
            "custom_css_files": [
                Path("css/index.css"),
                Path("css/index2.css"),
            ],
            "custom_js_files": [Path("js/bootstrap.min.js")],
        }
    }
    payload.copy_custom_static_files(config, setup_dir)
    assert (setup_dir / "custom" / "css" / "index.css").is_file()
    assert (setup_dir / "custom" / "css" / "index2.css").is_file()
    assert (setup_dir / "custom" / "js" / "bootstrap.min.js").is_file()


def test_copy_data(setup_dir):
    config = {
        "theme": {"name": "rawhtml"},
        "data": [
            f"{TEST_PATH}/data/img",
            f"{TEST_PATH}/data/Resume.pdf",
        ],
    }
    payload.copy_data_files(config, setup_dir)
    assert Path(setup_dir / "img").exists()


def test_copy_payload(setup_dir):
    config = {
        "theme": {
            "name": "rawhtml",
            "custom": f"{TEST_PATH}/custom_theme",
        },
        "data": [
            f"{TEST_PATH}/data/img",
            f"{TEST_PATH}/data/Resume.pdf",
        ],
    }
    parse.get_custom_static_files(config)
    payload.copy_payload(config, setup_dir)
    assert (setup_dir / "img").is_dir()
    assert (setup_dir / "custom" / "css" / "index.css").is_file()
    assert (setup_dir / "custom" / "css" / "index2.css").is_file()
    assert (setup_dir / "Resume.pdf").is_file()
