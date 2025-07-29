import timeit

from .image_util import random_test_image_and_expected
from src.im2im.knowledge_graph_construction import encode_metadata
from src.im2im.util import instance_code_template


def time_cost(source, target, conversion, test_img_size=(256, 256), repeat_count=10):
    source_image, _ = random_test_image_and_expected(source, target, test_img_size)

    if(source_image is None):
        return float('inf')
    
    code = instance_code_template(conversion[1], "source_image", "target_image")
    globals_ = {
        'source_image': source_image,
    }

    if 'source_image' not in globals_ or globals_['source_image'] is None:
        raise ValueError("source_image is not properly initialized")

    try:
        execution_time = timeit.timeit(stmt=code, setup=f"{conversion[0]}", number=repeat_count, globals=globals_)
    except Exception as e:
        raise RuntimeError(
            f"Error: {e}\n"
            f"Code: {code}\n"
            f"Setup: {conversion[0]}"
        )
    return execution_time / repeat_count


def time_cost_in_kg(kg, test_img_size=(256, 256), repeat_count=10):
    time_costs = {}
    for edge in kg.edges:
        source, target = edge
        conversion = kg.get_edge_data(source, target).get('conversion')
        if conversion is not None:
            time_costs[(encode_metadata(source),
                        encode_metadata(target))] = time_cost(source, target, conversion, test_img_size, repeat_count)
    return time_costs
