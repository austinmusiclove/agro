import os
from pathlib import Path

import pytest

from lib.config import YamlConfigLoader
from lib.image_saver import LocalImageSaver


@pytest.fixture
def image_bytes():
    test_file = Path(__file__).parent.parent.parent / "assets" / "images" / "bytes" / "sample.jpg"
    return test_file.read_bytes()


@pytest.fixture
def png_bytes():
    test_file = Path(__file__).parent.parent.parent / "assets" / "images" / "bytes" / "screenshot_sample.png"
    return test_file.read_bytes()


@pytest.fixture
def config_loader(tmp_path):
    return YamlConfigLoader(config_overrides={
        "image_saver": {"images_dir": str(tmp_path / "test_images")}
    })


def test_save_creates_file(tmp_path, image_bytes, config_loader):
    saver = LocalImageSaver(config_loader)
    path = saver.save(image_bytes)
    assert os.path.exists(path)
    assert os.path.isfile(path)


def test_save_returns_absolute_path(tmp_path, image_bytes, config_loader):
    saver = LocalImageSaver(config_loader)
    path = saver.save(image_bytes)
    assert os.path.isabs(path)


def test_save_with_name_hint(tmp_path, image_bytes, config_loader):
    saver = LocalImageSaver(config_loader)
    path = saver.save(image_bytes, name_hint="test-banner")
    assert "test-banner" in path


def test_save_creates_directory_if_missing(tmp_path, image_bytes, config_loader):
    saver = LocalImageSaver(config_loader)
    path = saver.save(image_bytes)
    assert os.path.exists(path)


def test_save_detects_jpg_extension(tmp_path, image_bytes, config_loader):
    saver = LocalImageSaver(config_loader)
    path = saver.save(image_bytes)
    assert path.endswith(".jpg")


def test_save_returns_unique_paths(tmp_path, image_bytes, config_loader):
    saver = LocalImageSaver(config_loader)
    path1 = saver.save(image_bytes)
    path2 = saver.save(image_bytes)
    assert path1 != path2


def test_save_detects_png_extension(tmp_path, png_bytes, config_loader):
    saver = LocalImageSaver(config_loader)
    path = saver.save(png_bytes)
    assert path.endswith(".png")
