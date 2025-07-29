import os

import numpy as np
import pytest
import torch

from src.im2im import add_conversion_for_metadata_pairs, _code_generator, _constructor, \
    im2im_code, im2im, Image, get_possible_metadata, find_target_metadata
from src.im2im.code_generator import ConvertCodeGenerator
from src.im2im.knowledge_graph_construction import KnowledgeGraph


def test_im2im():
    source_image = Image(np.random.randint(0, 256, (20, 20, 3), dtype=np.uint8), "numpy.rgb_uint8")

    actual_image = im2im(source_image, "torch")
    expected_image = (torch.from_numpy(source_image.raw_image).permute(2, 0, 1).unsqueeze(0)) / 255

    assert torch.allclose(actual_image.raw_image, expected_image), \
        f"expected {expected_image} but got {actual_image}"


def test_get_conversion_code():
    # source = get_possible_metadata("numpy.float64(0to1)")
    source = {"data_representation": "numpy.ndarray", "minibatch_input": False, "device": "cpu",
     "image_data_type": "float32(0to1)", "color_channel": "rgb", "channel_order": "channel last"}
    target = find_target_metadata(source, "torch.gpu")

    actual_code = im2im_code("source_image", source, "target_image", target)
    expected_code = ('import torch',
                     'image = torch.from_numpy(source_image)\n'
                     'image = image.permute(2, 0, 1)\n'
                     'image = image.unsqueeze(0)\n'
                     'target_image = image.cuda()')

    assert actual_code == expected_code


@pytest.fixture
def conversion_for_metadata_pairs():
    return [({"color_channel": "bgr", "channel_order": "channel first", "minibatch_input": False,
              "image_data_type": "uint8", "device": "gpu", "data_representation": "torch.tensor"},
             {"color_channel": "rgb", "channel_order": "channel first", "minibatch_input": False,
              "image_data_type": "uint8", "device": "gpu", "data_representation": "torch.tensor"},
             ("", "return var[[2, 1, 0], :, :]")),
            ({"color_channel": "bgr", "channel_order": "channel first", "minibatch_input": False,
              "image_data_type": "uint8", "device": "gpu", "data_representation": "torch.tensor"},
             {"color_channel": "rgb", "channel_order": "channel first", "minibatch_input": False,
              "image_data_type": "uint8", "device": "gpu", "data_representation": "torch.tensor"},
             ("", "return var[[2, 1, 0], :, :]"))
            ]


def test_add_conversion_for_metadata_pair_empty():
    def noop():
        pass

    _constructor.save_knowledge_graph = noop

    _constructor.clear_knowledge_graph()
    add_conversion_for_metadata_pairs([])
    assert _code_generator.knowledge_graph.nodes == []
    assert _code_generator.knowledge_graph.edges == []


def test_add_conversion_for_metadata_pair_none():
    def noop():
        pass

    _constructor.save_knowledge_graph = noop

    _constructor.clear_knowledge_graph()
    add_conversion_for_metadata_pairs(None)
    assert _code_generator.knowledge_graph.nodes == []
    assert _code_generator.knowledge_graph.edges == []


@pytest.fixture
def mock_code_generator(monkeypatch):
    kg = KnowledgeGraph()
    kg.load_from_file(os.path.join(os.path.dirname(__file__), 'data_for_tests/kg_5nodes_4edges.json'))
    mock = ConvertCodeGenerator(kg)
    monkeypatch.setattr('src.im2im.api._code_generator', mock)
    return mock


def test_add_conversion_for_metadata_pair_single_value(conversion_for_metadata_pairs):
    def noop():
        pass

    _constructor.save_knowledge_graph = noop

    _constructor.clear_knowledge_graph()
    pair = conversion_for_metadata_pairs[0]
    add_conversion_for_metadata_pairs(pair)
    assert _code_generator.knowledge_graph.nodes == [pair[0], pair[1]]
    assert _code_generator.knowledge_graph.edges == [(pair[0], pair[1])]
    edge_data = _code_generator.knowledge_graph.get_edge_data(pair[0], pair[1])
    edge_data["conversion"] == pair[2]
    edge_data["factory"] == "manual"


def test_add_conversion_for_metadata_pair_list_values(conversion_for_metadata_pairs):
    def noop():
        pass

    _constructor.save_knowledge_graph = noop

    _constructor.clear_knowledge_graph()
    add_conversion_for_metadata_pairs(conversion_for_metadata_pairs)
    for pair in conversion_for_metadata_pairs:
        assert pair[0] in _code_generator.knowledge_graph.nodes
        assert pair[1] in _code_generator.knowledge_graph.nodes
        assert (pair[0], pair[1]) in _code_generator.knowledge_graph.edges
        edge_data = _code_generator.knowledge_graph.get_edge_data(pair[0], pair[1])
        edge_data["conversion"] == pair[2]
        edge_data["factory"] == "manual"
