from typing import Union

from .knowledge_graph_construction import Metadata, encode_metadata
from .util import instance_code_template

def attribute_diff_count(u: str, v: str) -> int:
    s1 = u.split('.')
    s2 = v.split('.')
    counter = 0
    for a, b in zip(s1, s2):
        if a != b:
            counter += 1
    return counter


def huristic_function(u, v):
    return (0, attribute_diff_count(u, v))

class ConvertCodeGenerator:

    def __init__(self, knowledge_graph):
        self._knowledge_graph = knowledge_graph
        self._cache = {}

    def huristic_function(self, u, v):
        return (0, attribute_diff_count(u, v))

    @property
    def knowledge_graph(self):
        return self._knowledge_graph

    @knowledge_graph.setter
    def knowledge_graph(self, value):
        self._knowledge_graph = value

    def get_convert_path(self, source_metadata: Metadata, target_metadata: Metadata, allow_lossy_fallback=True):
        return self.knowledge_graph.get_shortest_path(source_metadata, target_metadata, self.huristic_function,
                                                      allow_lossy_fallback)

    def get_conversion(
            self,
            source_var_name: str,
            source_metadata: Metadata,
            target_var_name: str,
            target_metadata: Metadata,
            allow_lossy_fallback=True,
    ) -> Union[tuple[str, str], None]:
        """
        Generates Python code as a string that performs data conversion from a source variable to a target variable
         based on the provided metadata.

        Examples:
            >>> source_var_name = "source_image"
            >>> source_metadata = {"color_channel": "bgr", "channel_order": "channel last", ...}
            >>> target_var_name = "target_image"
            >>> target_metadata = {"color_channel": "rgb", "channel_order": "channel first", ...}
            >>> convert_code_generator = ConvertCodeGenerator()
            >>> conversion = convert_code_generator.get_conversion_using_metadata(source_var_name, source_metadata,
            >>> target_var_name, target_metadata)
            >>> conversion
            ('', '# Convert BGR to RGB\nvar1 = source_image[:, :, ::-1]\n# Change data format from HWC to CHW\nvar2 = np.transpose(var1, (2, 0, 1))\ntarget_image = var2')
        """
        source_encode_str = encode_metadata(source_metadata)
        target_encode_str = encode_metadata(target_metadata)
        if (source_encode_str, target_encode_str) in self._cache:
            cvt_path = self._cache[(source_encode_str, target_encode_str, allow_lossy_fallback)]
        else:
            cvt_path = self.knowledge_graph.get_shortest_path(source_metadata, target_metadata, self.huristic_function, allow_lossy_fallback)
            self._cache[(source_encode_str, target_encode_str, allow_lossy_fallback)] = cvt_path
        if cvt_path is None:
            result = None
        elif len(cvt_path) == 1:
            result = f"{target_var_name} = {source_var_name}"
        else:
            result = self._get_conversion_multiple_steps(
                cvt_path, source_var_name, target_var_name
            )
        return result

    def _get_conversion_multiple_steps(
            self, cvt_path_in_kg, source_var_name, target_var_name
    )->tuple[str, str]:
        imports = set()
        main_body = []
        arg = source_var_name
        for i in range(len(cvt_path_in_kg) - 1):
            return_name = "image" if i != len(cvt_path_in_kg) - 2 else target_var_name
            imports_step, main_body_step = self._get_conversion_per_step(
                cvt_path_in_kg[i], cvt_path_in_kg[i + 1], arg, return_name
            )
            if imports_step != "":
                imports.update(imports_step.split("\n"))
            main_body.append(main_body_step)
            arg = return_name
        return ("\n".join(sorted(imports)), "\n".join(main_body))

    def _get_conversion_per_step(self, source, target, arg, return_name):
        conversion_on_edge = self.knowledge_graph.get_edge_data(source, target)["conversion"]
        imports = conversion_on_edge[0]
        main_body = instance_code_template(conversion_on_edge[1], arg, return_name)
        return imports, main_body
