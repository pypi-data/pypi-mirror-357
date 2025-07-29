from src.im2im.knowledge_graph_construction import are_both_same_data_repr, is_differ_value_for_key, is_metadata_complete
from src.im2im.util import instance_code_template, func_obj_to_str, exclude_key_from_list


def test_instance_code_template():
    code_str = """# transformation
var_with_var_in_name_return = var + 1
for i in range(len(var)):
    var[i] = var[i] * 2  # Indentation inside the loop
return var
    """

    expected_output = """# transformation
var_with_var_in_name_return = source_image + 1
for i in range(len(source_image)):
    source_image[i] = source_image[i] * 2  # Indentation inside the loop
target_image = source_image
    """.strip()

    actual = instance_code_template(code_str, 'source_image', 'target_image').strip()

    assert actual == expected_output, "The transformed code does not match the expected output."


def func_example(x):
    result = 1
    for i in range(1, x + 1):
        if i % 2 == 0:
            result *= i
        else:
            result += i
    return result


def test_func_obj_to_str_function():
    expected_source = """def func_example(x):
    result = 1
    for i in range(1, x + 1):
        if i % 2 == 0:
            result *= i
        else:
            result += i
    return result
"""

    actual_source = func_obj_to_str(func_example)
    assert actual_source == expected_source


def test_exclude_key_from_list():
    keys = ['a', 'b', 'c', 'd']
    exclude_key = 'b'
    expected = ['a', 'c', 'd']
    actual = exclude_key_from_list(keys, exclude_key)
    assert actual == expected


def test_both_metadata_match_data_repr():
    metadata_a = {'data_representation': 'torch.tensor'}
    metadata_b = {'data_representation': 'torch.tensor'}
    data_repr = 'torch.tensor'
    assert are_both_same_data_repr(metadata_a, metadata_b, data_repr), \
        "Should return True when both metadata have the same data_representation matching data_repr"


def test_one_metadata_missing_data_repr():
    metadata_a = {'data_representation': 'torch.tensor'}
    metadata_b = {}
    data_repr = 'torch.tensor'
    assert not are_both_same_data_repr(metadata_a, metadata_b, data_repr), \
        "Should return False when one metadata is missing the data_representation key"


def test_one_metadata_different_data_repr():
    metadata_a = {'data_representation': 'torch.tensor'}
    metadata_b = {'data_representation': 'numpy.ndarray'}
    data_repr = 'torch.tensor'
    assert not are_both_same_data_repr(metadata_a, metadata_b, data_repr), \
        "Should return False when one metadata has a different data_representation value"


def test_both_metadata_missing_data_repr():
    metadata_a = {}
    metadata_b = {}
    data_repr = 'torch.tensor'
    assert not are_both_same_data_repr(metadata_a, metadata_b, data_repr), \
        "Should return False when both metadata are missing the data_representation key"


def test_both_metadata_different_data_repr():
    metadata_a = {'data_representation': 'torch.tensor'}
    metadata_b = {'data_representation': 'numpy.ndarray'}
    data_repr = 'PIL'
    assert not are_both_same_data_repr(metadata_a, metadata_b, data_repr), \
        "Should return False when both metadata have different data_representation values not matching data_repr"


def test_is_differ_value_for_key_true():
    metadata_a = {'key1': 'value1', 'key2': 'value2'}
    metadata_b = {'key1': 'diff_value1', 'key2': 'value2'}
    assert is_differ_value_for_key(metadata_a, metadata_b, 'key1'), \
        "Should return True when only the specified key differs"


def test_is_differ_value_for_key_false():
    metadata_a = {'key1': 'value1', 'key2': 'value2'}
    metadata_b = {'key1': 'value1', 'key2': 'value2'}
    assert not is_differ_value_for_key(metadata_a, metadata_b, 'key1'), \
        "Should return False when there are no differences, even for the specified key"


def test_is_metadata_complete_with_complete_metadata():
    metadata_instance = {
        "data_representation": "numpy.ndarray",
        "color_channel": "bgr",
        "channel_order": "channel last",
        "minibatch_input": False,
        "image_data_type": "uint8",
        "device": "cpu"
    }
    assert is_metadata_complete(metadata_instance)


def test_is_metadata_complete_with_incomplete_metadata():
    metadata_instance = {
        "data_representation": "numpy.ndarray",
        "color_channel": "bgr",
        "channel_order": "channel last",
        "minibatch_input": False,
        "image_data_type": "uint8"
        # "device" key is missing
    }
    assert not is_metadata_complete(metadata_instance)
