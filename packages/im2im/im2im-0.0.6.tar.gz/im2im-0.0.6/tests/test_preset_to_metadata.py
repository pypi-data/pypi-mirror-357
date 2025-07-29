import pytest

from src.im2im.find_metadata import Metadata4Library, PresetToMetadataTable, find_target_metadata, get_default_metadata, \
    find_closest_match
from src.im2im.knowledge_graph_construction import Metadata


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


@pytest.fixture
def opencv_lib(opencv_metadata):
    lib = Metadata4Library(opencv_metadata)
    lib.add_preset_with_override_metadata("gray", {"color_channel": "gray", "channel_order": "none"})
    return lib


@pytest.fixture
def skimage_metadata():
    return Metadata({
        "data_representation": "numpy.ndarray",
        "color_channel": "rgb",
        "channel_order": "channel last",
        "minibatch_input": False,
        "device": "cpu"
    })


@pytest.fixture
def skimage_lib(skimage_metadata):
    lib = Metadata4Library(skimage_metadata)
    lib.add_preset_with_override_metadata("gray", {"color_channel": "gray", "channel_order": "none"})
    return lib


@pytest.fixture
def pil_metadata():
    return Metadata({
        "data_representation": "PIL.Image",
        "color_channel": "rgb",
        "channel_order": "channel last",
        "minibatch_input": False,
        "device": "cpu"
    })


@pytest.fixture
def pil_lib(pil_metadata):
    lib = Metadata4Library(pil_metadata)
    lib.add_preset_with_override_metadata("gray", {"color_channel": "gray", "channel_order": "none"})
    return lib


@pytest.fixture
def preset_table(opencv_lib, skimage_lib, pil_lib):
    table = PresetToMetadataTable()
    table.add_lib_metadata("opencv", opencv_lib)
    table.add_lib_metadata("ski", skimage_lib)
    table.add_lib_metadata("pil", pil_lib)
    return table


def test_metadata4library_initialization(opencv_metadata):
    metadata_lib = Metadata4Library(opencv_metadata)
    assert metadata_lib.metadata == opencv_metadata


def test_add_preset_with_override_metadata(opencv_lib):
    override_metadata = Metadata({
        "color_channel": "gray",
        "channel_order": "none"
    })
    opencv_lib.add_preset_with_override_metadata("new_gray", override_metadata)
    assert opencv_lib.preset_with_override_metadata["new_gray"] == override_metadata
    assert opencv_lib.get_possible_metadata("new_gray") == {
        "data_representation": "numpy.ndarray",
        "color_channel": "gray",
        "channel_order": "none",
        "minibatch_input": False,
        "image_data_type": "uint8",
        "device": "cpu"
    }


def test_get_metadata_without_preset(opencv_lib, opencv_metadata):
    assert opencv_lib.get_possible_metadata(None) == opencv_metadata


def test_get_metadata_with_preset(opencv_lib, opencv_metadata):
    final_metadata = opencv_metadata.copy()
    final_metadata.update({"color_channel": "gray", "channel_order": "none"})
    assert opencv_lib.get_possible_metadata("gray") == final_metadata


def test_preset_to_metadata_table(preset_table, opencv_metadata, skimage_metadata, pil_metadata):
    assert preset_table.get_possible_metadata("opencv") == opencv_metadata
    assert preset_table.get_possible_metadata("opencv.gray") == {
        "data_representation": "numpy.ndarray",
        "color_channel": "gray",
        "channel_order": "none",
        "minibatch_input": False,
        "image_data_type": "uint8",
        "device": "cpu"
    }
    assert preset_table.get_possible_metadata("ski") == skimage_metadata
    assert preset_table.get_possible_metadata("pil") == pil_metadata


def test_find_target_metadata():
    source_metadata = Metadata({
        "data_representation": "numpy.ndarray",
        "color_channel": "rgb",
        "channel_order": "channel first",
        "minibatch_input": False,
        "image_data_type": "float32(0to1)",
        "device": "cpu"
    })
    expected_metadata = source_metadata.copy()
    expected_metadata.update({
        "color_channel": "gray",
        "channel_order": "none"
    })

    result_metadata = find_target_metadata(source_metadata, "skimage.gray")
    assert result_metadata == expected_metadata


def test_get_default_metadata(skimage_metadata):
    input_metadata = skimage_metadata.copy()
    input_metadata["color_channel"] = ["rgb", "gray"]

    result_metadata = get_default_metadata(input_metadata)
    assert result_metadata == skimage_metadata


def test_find_closest_match(skimage_metadata):
    input_metadata = skimage_metadata.copy()
    input_metadata["color_channel"] = ["rgb", "gray"]
    input_metadata["channel_order"] = "channel first"

    result_metadata = find_closest_match(input_metadata, skimage_metadata)
    skimage_metadata["channel_order"] = "channel first"

    assert result_metadata == skimage_metadata
