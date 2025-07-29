from typing import List, Union

from .code_generator import ConvertCodeGenerator
from .find_metadata import find_target_metadata, Metadata4Library, get_preset_table, PossibleMetadata
from .knowledge_graph_construction import (
    get_knowledge_graph_constructor,
    MetadataValues,
    FactoriesCluster,
    ConversionForMetadataPair, Metadata, is_metadata_complete,
)

_constructor = get_knowledge_graph_constructor()
_code_generator = ConvertCodeGenerator(_constructor.knowledge_graph)
preset_table = get_preset_table()


class Image:
    def __init__(self, raw_image, config: Union['Metadata', str]):
        self.raw_image = raw_image
        self._init_metadata(config)

    def _init_metadata(self, config: Union['Metadata', str]):
        """
        Args:
            config: Metadata | str: If str, it should be a preset path ("lib.preset"). If Metadata, it should be a complete metadata.
        """
        hint_msg = (f" Please provide complete metadata including 'data_representation', 'color_channel',"
                    f" 'channel_order', 'minibatch_input', 'image_data_type', 'device'.")
        if isinstance(config, str):
            metadata = get_possible_metadata(config)
            if not is_metadata_complete(metadata):
                raise Exception(f"Metadata {metadata} got using the preset for {config} is not complete." + hint_msg)
            self.metadata = metadata
        else:
            if not is_metadata_complete(config):
                raise Exception(f"Provided metadata {config} is not complete. " + hint_msg)
            self.metadata = config


def im2im(source_image: Image, target: Union['Metadata', str], allow_lossy_fallback=True) -> Image:
    target_metadata = find_target_metadata(source_image.metadata, target) if isinstance(target, str) else target
    
    if source_image.metadata == target_metadata:
        return source_image

    raw_image = source_image.raw_image
    target_image_name = "target_image"
    code = im2im_code("raw_image", source_image.metadata, target_image_name, target_metadata, allow_lossy_fallback)
    exec('\n'.join(code))
    return Image(locals()[target_image_name], target_metadata)


def im2im_code(source_var_name: str, source_metadata: Metadata, target_var_name: str, target_metadata: Metadata,
               allow_lossy_fallback=True) -> Union[tuple[str, str], None]:
    """
    Generates Python code as a string that performs data conversion from a source variable to a target variable based on specified preset path.

   """
    return _code_generator.get_conversion(source_var_name, source_metadata, target_var_name, target_metadata,
                                          allow_lossy_fallback)



def new_cost_function_on_edge(cost_function: callable):
    """
    You can use this function to set a new cost function for the goal function.
    The cost function should take two metadata, u, v, edge_attributes and return the cost.
    By default, it returns (information loss, step cost + gpu penalty).
    """
    _code_generator.cost_on_edge = cost_function

def new_heuristic_function(function):
    _code_generator.huristic_function = function


def get_possible_metadata(preset: str) -> PossibleMetadata:
    return get_preset_table().get_possible_metadata(preset)


def add_lib_metadata(lib: str, metadata: Metadata4Library):
    preset_table.add_metadata4library(lib, metadata)


def add_meta_values_for_image(new_metadata: MetadataValues):
    new_knowledge_graph = _constructor.add_metadata_values(new_metadata)
    _code_generator.knowledge_graph = new_knowledge_graph


def add_edge_factory_cluster(factory_cluster: FactoriesCluster):
    new_knowledge_graph = _constructor.add_edge_factory_cluster(factory_cluster)
    _code_generator.knowledge_graph = new_knowledge_graph


def add_conversion_for_metadata_pairs(
        pairs: Union[List[ConversionForMetadataPair], ConversionForMetadataPair]
):
    new_knowledge_graph = _constructor.add_conversion_for_metadata_pairs(pairs)
    _code_generator.knowledge_graph = new_knowledge_graph
