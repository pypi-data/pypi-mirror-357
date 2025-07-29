test_nodes = [
    {
        "data_representation": "numpy.ndarray",
        "color_channel": "rgb",
        "channel_order": "channel last",
        "minibatch_input": False,
        "image_data_type": "uint8",
        "device": "cpu"
    },
    {
        "data_representation": "numpy.ndarray",
        "color_channel": "bgr",
        "channel_order": "channel last",
        "minibatch_input": False,
        "image_data_type": "uint8",
        "device": "cpu"
    },
    {
        "data_representation": "torch.tensor",
        "color_channel": "rgb",
        "channel_order": "channel last",
        "minibatch_input": False,
        "image_data_type": "uint8",
        "device": "cpu"
    },
    {
        "data_representation": "torch.tensor",
        "color_channel": "rgb",
        "channel_order": "channel first",
        "minibatch_input": False,
        "image_data_type": "uint8",
        "device": "cpu"
    }

]

new_node = {
    "data_representation": "torch.tensor",
    "color_channel": "rgb",
    "channel_order": "channel first",
    "minibatch_input": True,
    "image_data_type": "uint8",
    "device": "cpu"
}

all_nodes = test_nodes + [new_node]

test_edges = [
    (test_nodes[0], test_nodes[1], ("", "return var[:, :, ::-1]", (0, 1))),
    (test_nodes[0], test_nodes[2], ("import torch", "return torch.from_numpy(var)", (0, 1))),
    (test_nodes[2], test_nodes[3], ("", "return var.permute(2, 0, 1)", (0, 1))),
    (test_nodes[1], test_nodes[2], ("", "im = var[:, :, ::-1]\nreturn torch.from_numpy(im)", (0, 1)))
]

new_edge = (test_nodes[3], new_node, ("import torch", "return torch.unsqueeze(var, 0)", (0, 1)))
