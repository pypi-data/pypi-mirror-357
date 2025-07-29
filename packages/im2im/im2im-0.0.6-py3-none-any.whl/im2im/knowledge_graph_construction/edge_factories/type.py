from typing import Callable, List, Tuple, Union

from ..metedata import Metadata

# import_code, convert_code, IsLossy(default False), IsOnGPU(default False)
Conversion = Union[Tuple[str, str, Union[bool, None], Union[bool, None]], None]
EdgeFactory = Callable[[Metadata, Metadata], Conversion]
FactoriesCluster = Tuple[Callable[[Metadata, Metadata], bool], List[EdgeFactory]]
ConversionForMetadataPair = Tuple[Metadata, Metadata, Conversion]
