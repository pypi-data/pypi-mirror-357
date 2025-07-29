import os
import shutil
import tempfile
from pathlib import Path
from click.testing import CliRunner
from PIL import Image
import pytest

from faviconx.__main__ import main, ICON_SIZES

def create_sample_image(path, size=(256, 256), color=(255, 0, 0, 255)):
    """Create a simple PNG image for testing."""
    img = Image.new('RGBA', size, color)
    img.save(path)

@pytest.fixture(scope="module")
def sample_image(tmp_path_factory):
    tmp_dir = tmp_path_factory.mktemp("data")
    img_path = tmp_dir / "sample.png"
    create_sample_image(img_path)
    return img_path

@pytest.fixture
def temp_output_dir(tmp_path):
    return tmp_path / "output"

def test_cli_required(sample_image, temp_output_dir):
    runner = CliRunner()
    result = runner.invoke(main, [str(sample_image), str(temp_output_dir), '--option', 'required'])
    assert result.exit_code == 0
    # Check that required icons are generated
    for icon in ICON_SIZES:
        if icon['option'] == 'Required':
            filename = icon['filename'].replace('favicon', 'icon', 1)
            assert (temp_output_dir / filename).exists()

def test_cli_prefix(sample_image, temp_output_dir):
    runner = CliRunner()
    prefix = 'testico'
    result = runner.invoke(main, [str(sample_image), str(temp_output_dir), '--prefix', prefix, '--option', 'required-recommended'])
    assert result.exit_code == 0
    # Check that files use the prefix
    for icon in ICON_SIZES:
        if icon['option'] in {'Required', 'Recommended'}:
            filename = icon['filename'].replace('favicon', prefix, 1)
            assert (temp_output_dir / filename).exists()

def test_cli_optional(sample_image, temp_output_dir):
    runner = CliRunner()
    result = runner.invoke(main, [str(sample_image), str(temp_output_dir), '--option', 'optional'])
    assert result.exit_code == 0
    # Check that optional icons are generated
    for icon in ICON_SIZES:
        if icon['option'] in {'Required', 'Recommended', 'Optional'}:
            filename = icon['filename'].replace('favicon', 'icon', 1)
            assert (temp_output_dir / filename).exists()

def test_cli_all(sample_image, temp_output_dir):
    runner = CliRunner()
    result = runner.invoke(main, [str(sample_image), str(temp_output_dir), '--option', 'all'])
    assert result.exit_code == 0
    # Check that all icons are generated
    for icon in ICON_SIZES:
        filename = icon['filename'].replace('favicon', 'icon', 1)
        assert (temp_output_dir / filename).exists()

def test_cli_error_on_missing_image(temp_output_dir):
    runner = CliRunner()
    result = runner.invoke(main, ["notfound.png", str(temp_output_dir)])
    assert result.exit_code != 0
    assert "does not exist" in result.output

def test_cli_no_html_option(sample_image, temp_output_dir):
    runner = CliRunner()
    result = runner.invoke(main, [str(sample_image), str(temp_output_dir), '--no-html'])
    assert result.exit_code == 0
    # Check that favicons are generated but HTML files are not
    assert (temp_output_dir / "icon.ico").exists()
    assert not (temp_output_dir / "index.html").exists()
    assert not (temp_output_dir / "site.webmanifest").exists()

def test_cli_verbose_output(sample_image, temp_output_dir):
    runner = CliRunner()
    result = runner.invoke(main, [str(sample_image), str(temp_output_dir), '--verbose'])
    assert result.exit_code == 0
    # Check that verbose output is present
    assert "Source image:" in result.output
    assert "Output directory:" in result.output 