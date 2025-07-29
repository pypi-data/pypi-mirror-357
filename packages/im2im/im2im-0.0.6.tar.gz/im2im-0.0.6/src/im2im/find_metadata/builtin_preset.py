from .preset_to_metadata import Metadata4Library, get_preset_table

preset_table = get_preset_table()

opencv_lib = Metadata4Library(
    {"data_representation": "numpy.ndarray", "minibatch_input": False, "image_data_type": "uint8", "device": "cpu"}, )
opencv_lib.add_preset_with_override_metadata("bgr", {"color_channel": "bgr", "channel_order": "channel last"})
opencv_lib.add_preset_with_override_metadata("gray", {"color_channel": "gray", "channel_order": "none"})
preset_table.add_lib_metadata("opencv", opencv_lib)

skimage_lib = Metadata4Library(
    {"data_representation": "numpy.ndarray", "minibatch_input": False, "device": "cpu",
     "image_data_type": ["uint8", "uint16", "uint32", "int8", "int16", "int32", "float32", "float64", "double",
                         "float32(0to1)", "float32(-1to1)", "float64(0to1)", "float64(-1to1)", "double(0to1)",
                         "double(-1to1)",
                         ], })
skimage_lib.add_preset_with_override_metadata("rgb", {"color_channel": "rgb", "channel_order": "channel last"})
skimage_lib.add_preset_with_override_metadata("gray", {"color_channel": "gray", "channel_order": "none"})

skimage_lib.add_preset_with_override_metadata("before_gaussian", [
    skimage_lib.get_possible_metadata("gray"), skimage_lib.get_possible_metadata("rgb")])

skimage_lib.add_preset_with_override_metadata("before_equalize_adapthist",
                                              skimage_lib.get_possible_metadata("before_gaussian"))

preset_table.add_lib_metadata("skimage", skimage_lib)

pil_lib = Metadata4Library(
    {"data_representation": "PIL.Image", "minibatch_input": False, "image_data_type": "uint8", "device": "cpu"})
pil_lib.add_preset_with_override_metadata("rgb_uint8", {"color_channel": "rgb", "channel_order": "channel last"})
pil_lib.add_preset_with_override_metadata("gray_uint8", {"color_channel": "gray", "channel_order": "none"})
pil_lib.add_preset_with_override_metadata('rgb_gray', [pil_lib.get_possible_metadata('rgb_uint8'),
                                                       pil_lib.get_possible_metadata('gray_uint8')])
preset_table.add_lib_metadata("pil", pil_lib)

torch_lib = Metadata4Library(
    {"data_representation": "torch.tensor", "channel_order": "channel first", "minibatch_input": True,
     "image_data_type": "float32(0to1)", "device": ["cpu", "gpu"], "color_channel": ["rgb", "gray"]})
torch_lib.add_preset_with_override_metadata("rgb", {"color_channel": "rgb"})
torch_lib.add_preset_with_override_metadata("gray", {"color_channel": "gray"})
torch_lib.add_preset_with_override_metadata("gpu", {"device": "gpu"})

preset_table.add_lib_metadata("torch", torch_lib)

numpy_lib = Metadata4Library(
    {"data_representation": "numpy.ndarray", "minibatch_input": False, "device": "cpu",
     "image_data_type": ["uint8", "uint16", "uint32", "int8", "int16", "int32", "float32", "float64", "double",
                         "float32(0to1)", "float32(-1to1)", "float64(0to1)", "float64(-1to1)", "double(0to1)",
                         "double(-1to1)",
                         ], })
numpy_lib.add_preset_with_override_metadata("rgb", {"color_channel": "rgb", "channel_order": "channel last"})
numpy_lib.add_preset_with_override_metadata("gray", {"color_channel": "gray", "channel_order": "none"})
numpy_lib.add_preset_with_override_metadata("rgb_uint8", {"color_channel": "rgb", "channel_order": "channel last",
                                                          "image_data_type": "uint8"})
numpy_lib.add_preset_with_override_metadata("uint8", [
    {"color_channel": "rgb", "channel_order": "channel last", "image_data_type": "uint8"},
    {"color_channel": "gray", "channel_order": "none", "image_data_type": "uint8"}])
numpy_lib.add_preset_with_override_metadata('gray_float64(0to1)', {"color_channel": "gray", "channel_order": "none",
                                                                   'image_data_type': 'float64(0to1)'})
numpy_lib.add_preset_with_override_metadata('float64(0to1)', [{"color_channel": "gray", "channel_order": "none",
                                                               'image_data_type': 'float64(0to1)'}, {
                                                                  "color_channel": "rgb",
                                                                  "channel_order": "channel last",
                                                                  'image_data_type': 'float64(0to1)'}])
preset_table.add_lib_metadata("numpy", numpy_lib)
