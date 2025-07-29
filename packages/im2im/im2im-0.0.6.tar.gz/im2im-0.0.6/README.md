# im2im: Automatically Converting In-Memory Image Representations
---

[![PyPI - Version](https://img.shields.io/pypi/v/im2im.svg)](https://pypi.org/project/im2im/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/im2im)](https://pypi.org/project/im2im/)
[![Downloads](https://static.pepy.tech/badge/im2im)](https://pepy.tech/project/im2im)
[![Tests](https://github.com/c3di/im2im/actions/workflows/python%20tests%20with%20coverage.yml/badge.svg)](https://github.com/c3di/im2im/actions/workflows/python%20tests%20with%20coverage.yml)
[![codecov](https://codecov.io/github/c3di/im2im/graph/badge.svg?token=BWBXANX8W7)](https://codecov.io/github/c3di/im2im)

The `im2im` python package provides an automated approach for converting in-memory image representations across a variety of image processing libraries, including `scikit-image`, `opencv-python`, `scipy`, `PIL`, `numpy`, `PyTorch`, and `Tensorflow`. It handles the nuances inherent to each library's image representation, such as data formats (numpy arrays, PIL images, torch tensors, and so on), color channel (RGB or grayscale), channel order (channel first or last or none), device (CPU/GPU), and pixel intensity ranges.

## Usage

`im2im` is developed to simplify image type conversions in **Visual Programming Systems (VPS)** for image processing. It removes the need for manual conversion steps, significantly improving accessibility—especially for non-expert users.

###  Installation (At Execution Environment) 

Install the package via pip:

```bash
pip install im2im
```

Or install the package directly from GitHub:

```python
pip install git+https://github.com/c3di/im2im.git
```


### Usage for Auto Type Conversion

**API Entry Point: im2im**

```python
import numpy as np
from im2im import Image, im2im

# Example input: an image that is a numpy.ndarray with shape (20, 20, 3) in uint8 format
to_be_converted = Image(np.random.randint(0, 256, (20, 20, 3), dtype=np.uint8), "numpy.rgb_uint8")
# Convert to the target image with metadata preset "torch.gpu".
converted: Image = im2im(to_be_converted, "torch.gpu")
```

Metadata presets are defined in `src/im2im/find_metadata_builtin_preset.py`. 

For additional APIs such as `im2im_code`, please refer to `src/im2im/api.py`. 



####  Integration in Visual Programming Systems:

Take the Blockly visual programming framework as an example. To enable automatic type conversion:

* Call `im2im()` before operations to convert the input.
* Explicitly set the metadata for the output image.

**Without `im2im`**

```javascript
Blockly.Python.forBlock['gaussian_blur'] = function (block) {
  requiredImports.add("from skimage.filters import gaussian");
  // inputs
  var image = Blockly.Python.valueToCode(block, "IMAGE", Blockly.Python.ORDER_NONE) || "None";
  var sigma = block.getFieldValue("SIGMA") || "0.5";
  var resultVar = Blockly.Python.nameDB_.getDistinctName("out_im", Blockly.VARIABLE_CATEGORY_NAME);
  // code without im2im
  var code = `${resultVar} = gaussian(${image}, sigma=${sigma})`;
  // output
  Blockly.Python.definitions_["define_" + resultVar] = code;
  return [`${resultVar}`, Blockly.Python.ORDER_NONE];
};
```

**With `im2im`**

```javascript
Blockly.Python.forBlock['gaussian_blur'] = function (block) {
  // inputs as above ...
  // code with im2im
  var convert_to = `in_im1 = im2im(${image}, 'skimage.before_gaussian')`;
  var operation = `e_gaussian_filtered = gaussian(in_im1.raw_image, sigma=${sigma})`;
  var convert_back = `${resultVar} = Image(e_gaussian_filtered, {**in_im1.metadata, 'image_data_type': 'float64(0to1)'})`;
  var code = `${convert_to}\n${operation}\n${convert_back}`;
  // outputs as above...
};
```

For additional implementation examples, see the `comparative_analysis/1/enhanced_VPL4IP.html` and `comparative_analysis/2/enhanced_VPL4IP.html` .



**Note:** For detailed comparisons between visual programming systems (**visual interface and execution**) with and without `im2im`, refer to the following studies: [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1cf5M1gOMdMXaRIKsCYalVj99RzMYSy8C?usp=sharing), [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1qPPL-IvovlhdKv-_0SjADBSOc60SPZDT?usp=sharing).

## Contribution

We welcome all contributions to this project! If you have suggestions, feature requests, or want to contribute in any other way, please feel free to open an issue or submit a pull request. For detailed instructions on developing, building, and publishing this package, please refer to the [README_DEV](https://github.com/c3di/im2im/blob/main/README_Dev.md).



## Cite

`im2im: Automatically Converting In-Memory Image Representations using A Knowledge Graph Approach`

accepted for publication in OOPSLA 2025.



## License

This project is licensed under the MIT License. See the LICENSE file for details.
