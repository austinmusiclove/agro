import uuid
from dotenv import load_dotenv
from pathlib import Path

import pytest

from lib.config import YamlConfigLoader
from lib.image_saver import S3ImageSaver


@pytest.fixture
def image_bytes():
    test_file = Path(__file__).parent.parent.parent / "assets" / "images" / "bytes" / "sample.jpg"
    return test_file.read_bytes()


@pytest.fixture
def screenshot_bytes():
    test_file = Path(__file__).parent.parent.parent / "assets" / "images" / "bytes" / "screenshot_sample.png"
    return test_file.read_bytes()


@pytest.fixture
def config_loader():
    load_dotenv(override=True)
    return YamlConfigLoader()


@pytest.fixture
def s3_saver(config_loader):
    return S3ImageSaver(config_loader)


@pytest.fixture(autouse=True)
def cleanup_s3_uploads(s3_saver):
    uploaded_keys = []

    original_save = s3_saver.save

    def tracked_save(image_bytes, name_hint=None):
        result = original_save(image_bytes, name_hint)
        if "s3://" in result:
            key = result.replace(f"s3://{s3_saver._bucket}/", "")
        else:
            parts = result.split(f".s3.{s3_saver._region}.amazonaws.com/")
            key = parts[1] if len(parts) > 1 else result.split("/")[-1]
        uploaded_keys.append(key)
        return result

    s3_saver.save = tracked_save
    s3_saver._uploaded_keys = uploaded_keys

    yield

    for key in uploaded_keys:
        try:
            s3_saver._s3_client.delete_object(Bucket=s3_saver._bucket, Key=key)
        except Exception:
            pass


def test_save_uploads_to_s3(s3_saver, image_bytes):
    path = s3_saver.save(image_bytes)
    assert path.startswith("https://")


def test_save_returns_s3_url(s3_saver, image_bytes):
    path = s3_saver.save(image_bytes)
    assert s3_saver._bucket in path
    assert ".jpg" in path


def test_save_with_name_hint(s3_saver, image_bytes):
    path = s3_saver.save(image_bytes, name_hint="test-banner")
    assert "test-banner" in path


def test_save_detects_jpg_extension(s3_saver, image_bytes):
    path = s3_saver.save(image_bytes)
    assert path.endswith(".jpg")


def test_save_detects_png_extension(s3_saver, screenshot_bytes):
    path = s3_saver.save(screenshot_bytes)
    assert path.endswith(".png")


def test_save_returns_unique_paths(s3_saver, image_bytes):
    path1 = s3_saver.save(image_bytes)
    path2 = s3_saver.save(image_bytes)
    assert path1 != path2


def test_save_with_path_prefix(s3_saver, image_bytes):
    path = s3_saver.save(image_bytes)
    assert s3_saver._path_prefix in path
