import pytest

from src.im2im import Metadata, Image


@pytest.fixture
def opencv_metadata():
    return Metadata({
        "data_representation": "numpy.ndarray",
        "color_channel": "bgr",
        "channel_order": "channel last",
        "minibatch_input": False,
        "image_data_type": "uint8",
        "device": "cpu"
    })


def test_image_initialization_with_metadata(opencv_metadata):
    raw_image = "raw image data"
    image = Image(raw_image, opencv_metadata)
    assert image.raw_image == raw_image
    assert image.metadata == opencv_metadata


def test_image_initialization_with_preset(opencv_metadata):
    raw_image = "raw image data"
    image = Image(raw_image, "opencv.gray")
    expected_metadata = opencv_metadata.copy()
    expected_metadata.update({
        "color_channel": "gray",
        "channel_order": "none"
    })
    assert image.raw_image == raw_image
    assert image.metadata == expected_metadata


def test_image_initialization_with_incomplete_metadata():
    raw_image = "raw image data"
    incomplete_metadata = {
        "data_representation": "numpy.ndarray",
        "color_channel": "bgr",
        "channel_order": "channel last",
        "minibatch_input": False
        # Missing keys: image_data_type, device
    }
    with pytest.raises(Exception, match="Provided metadata .* is not complete.*"):
        Image(raw_image, incomplete_metadata)


def test_image_initialization_with_incomplete_preset():
    raw_image = "raw image data"
    with pytest.raises(Exception, match="Metadata .* got using the preset for skimage is not complete.*"):
        Image(raw_image, "skimage")
