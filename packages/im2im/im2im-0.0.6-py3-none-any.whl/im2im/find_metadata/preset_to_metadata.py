from typing import Dict, Union, List, TypedDict, Literal


class PossibleMetadata(TypedDict):
    data_representation: Union[str, List[str]]
    color_channel: Union[str, List[str]]
    channel_order: Union[Literal['channel last', 'channel first', 'none'], List[Literal['channel last', 'channel first', 'none']]]
    minibatch_input: Union[bool, List[bool]]
    image_data_type: Union[
        Literal[
            'uint8', 'uint16', 'uint32', 'uint64', 'float32', 'float64', 'double', 'int8', 'int16', 'int32', 'int64',
            'float32(0to1)', 'float32(-1to1)', 'float64(0to1)', 'float64(-1to1)', 'double(0to1)', 'double(-1to1)'
        ],
        List[
            Literal[
                'uint8', 'uint16', 'uint32', 'uint64', 'float32', 'float64', 'double', 'int8', 'int16', 'int32', 'int64',
                'float32(0to1)', 'float32(-1to1)', 'float64(0to1)', 'float64(-1to1)', 'double(0to1)', 'double(-1to1)'
            ]
        ]
    ]
    device: Union[str, List[str]]


class Metadata4Library:

    def __init__(self, metadata):
        self.metadata = metadata
        self.preset_with_override_metadata: Dict[str, Union[PossibleMetadata, List[PossibleMetadata]]] = {}

    def add_preset_with_override_metadata(self, preset: str, metadata: Union[PossibleMetadata, List[PossibleMetadata]]):
        self.preset_with_override_metadata[preset] = metadata

    def get_possible_metadata(self, preset):
        if preset not in self.preset_with_override_metadata:
            return self.metadata

        if isinstance(self.preset_with_override_metadata[preset], list):
            final_metadata = []
            for metadata in self.preset_with_override_metadata[preset]:
                raw_metadata = self.metadata.copy()
                raw_metadata.update(metadata)
                final_metadata.append(raw_metadata)
            return final_metadata

        final_metadata = self.metadata.copy()
        final_metadata.update(self.preset_with_override_metadata[preset])
        return final_metadata


class PresetToMetadataTable:
    def __init__(self):
        self.presets: Dict[str, Metadata4Library] = {}

    def add_lib_metadata(self, lib: str, metadata: Metadata4Library):
        self.presets[lib] = metadata

    def get_possible_metadata(self, path) -> PossibleMetadata:
        if "." in path:
            lib, path = path.split(".")
        else:
            lib = path
            path = None
        if lib not in self.presets:
            raise Exception(f"No metadata available for {lib}")
        return self.presets[lib].get_possible_metadata(path)


preset_table = PresetToMetadataTable()


def get_preset_table():
    return preset_table
