import math
import os
from unittest.mock import patch

import pytest

from .time_cost_measure import time_cost, time_cost_in_kg
from src.im2im.knowledge_graph_construction import KnowledgeGraph, encode_metadata
from .data_for_tests.nodes_edges import test_edges


@pytest.mark.parametrize("source_node,target_node,conversion", test_edges[:3])
def test_time_cost(source_node, target_node, conversion):
    result = time_cost(source_node, target_node, conversion)
    assert result != math.inf, "time_cost should return a finite value when conversion is successful"


@patch("tests.image_util.random_test_image_and_expected")
def test_infinite_time_cost(mock_random_test_image):
    mock_random_test_image.side_effect = Exception("Failed to generate image")
    result = time_cost("source_node", "target_node", ("", "return var"))
    assert result == math.inf, "time_cost should return math.inf when image generation fails"


@pytest.fixture
def kg():
    kg = KnowledgeGraph()
    kg.load_from_file(os.path.join(os.path.dirname(__file__), "data_for_tests/kg_5nodes_4edges.json"))
    return kg


def test_time_cost_to_throw_exception(kg):
    test_edge = list(kg.edges)[1]

    with pytest.raises(Exception) as exc_info:
        time_cost(test_edge[0], test_edge[1], ("", "return torch.from_numpy(var)"))

    assert "name 'torch' is not defined" in str(exc_info.value), \
        "time_cost should raise RuntimeError with the correct message when conversion fails"


def test_time_cost_in_kg(kg):
    costs = [1, 2, 3, 4]
    with patch('tests.time_cost_measure.time_cost') as mock_time_cost:
        mock_time_cost.side_effect = costs

        actual = time_cost_in_kg(kg, test_img_size=(256, 256), repeat_count=10)

        expected_time_costs = {}
        for i, (source, target) in enumerate(kg.edges):
            expected_time_costs[(encode_metadata(source), encode_metadata(target))] = costs[i]

        assert actual == expected_time_costs, "time_cost_in_kg should return the correct time costs"
