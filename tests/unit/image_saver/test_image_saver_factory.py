import pytest

from lib.config import YamlConfigLoader
from lib.image_saver import ImageSaverFactory, LocalImageSaver


@pytest.fixture
def config_loader(tmp_path):
    return YamlConfigLoader(config_overrides={
        "image_saver": {"images_dir": str(tmp_path / "test_images")}
    })


def test_create_returns_local_saver(config_loader):
    factory = ImageSaverFactory(config_loader)
    saver = factory.create()
    assert isinstance(saver, LocalImageSaver)


def test_create_with_explicit_type(config_loader):
    factory = ImageSaverFactory(config_loader)
    saver = factory.create("local")
    assert isinstance(saver, LocalImageSaver)


def test_create_raises_for_unknown_type(config_loader):
    factory = ImageSaverFactory(config_loader)
    with pytest.raises(ValueError, match="Unknown image_saver type"):
        factory.create("unknown_type")


def test_create_with_config_overrides(tmp_path):
    config_loader = YamlConfigLoader(config_overrides={
        "image_saver": {"images_dir": str(tmp_path / "custom_images")}
    })
    factory = ImageSaverFactory(config_loader)
    saver = factory.create()
    assert isinstance(saver, LocalImageSaver)
    path = saver.save(b"fake bytes")
    assert str(tmp_path / "custom_images") in path
