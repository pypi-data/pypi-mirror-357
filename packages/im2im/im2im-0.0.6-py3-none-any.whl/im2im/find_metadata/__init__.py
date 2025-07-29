from typing import Union, List

from .preset_to_metadata import Metadata4Library, PresetToMetadataTable, get_preset_table, PossibleMetadata
from .builtin_preset import *
from ..knowledge_graph_construction import is_metadata_complete, Metadata


def get_default_metadata(possible_metadata: PossibleMetadata) -> Metadata:
    default_metadata = {}
    for key, value in possible_metadata.items():
        if isinstance(value, list):
            default_metadata[key] = value[0]
        else:
            default_metadata[key] = value
    return default_metadata


def find_default_metadata(possible_metadata: PossibleMetadata, target: Metadata) -> Metadata:
    default_metadata = {}
    for key, value in possible_metadata.items():
        if isinstance(value, list):
            if target[key] in value:
                default_metadata[key] = target[key]
            else:
                default_metadata[key] = value[0]
        else:
            default_metadata[key] = value
    return default_metadata


def find_closest_match(all_possible: Union[PossibleMetadata, List[PossibleMetadata]], target):
    if not isinstance(all_possible, list):
        all_possible = [all_possible]
    for possible_metadata in all_possible:
        matched_metadata = {'data_representation': possible_metadata['data_representation']}
        for key, value in target.items():
            if key == 'data_representation':
                continue
            allowed_value = possible_metadata.get(key)
            if isinstance(allowed_value, list):
                if value in allowed_value:
                    matched_metadata[key] = value
            elif value == allowed_value:
                matched_metadata[key] = allowed_value
        if is_metadata_complete(matched_metadata):
            return matched_metadata

    for possible_metadata in all_possible:
        color_channel = possible_metadata['color_channel']
        if isinstance(color_channel, list):
            if target.get('color_channel') in color_channel:
                return find_default_metadata(possible_metadata, target)
        else:
            if target.get('color_channel') == color_channel:
                return find_default_metadata(possible_metadata, target)
    return find_default_metadata(all_possible[0], target)


def find_target_metadata(source_metadata, target_preset_path) -> Metadata:
    """
    Return the metadata of the target preset path by finding the closest match with the source metadata.
    """
    all_possible: Union[PossibleMetadata, List[PossibleMetadata]] = get_preset_table().get_possible_metadata(target_preset_path)
    return find_closest_match(all_possible, source_metadata)
