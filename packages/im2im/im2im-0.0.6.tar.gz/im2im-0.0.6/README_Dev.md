# im2im Development
## Setup Dev Environment
**Clone the Repository**

```bash
git clone git@github.com:c3di/im2im.git
```

**Installing Dependencies**

With your Python virtual environment active, choose the appropriate file—either `requirements_cpu.txt` or `requirements_gpu.txt`, both located in the root folder of your project, and use its correct path to install the necessary dependencies. For those requiring TensorFlow with CUDA support, it's crucial to confirm system compatibility by consulting the [TensorFlow Installation Guide](https://www.tensorflow.org/install/pip).

```bash
pip install -r path/to/requirements.txt
```

## Knowledge Graph Extension

Our package is designed for easy knowledge graph extension. Once you are familiar with the mechanisms behind the construction of the knowledge graph, you can leverage a suite of functions designed for various extension requirements including `add_meta_values_for_image`, `add_edge_factory_cluster`, and `add_conversion_for_metadata_pairs`, each tailored for different extension needs. 

## Run Tests

Navigate to the root directory and run the tests in the tests folder using the following command:
```bash
pytest tests
```
or run the tests through test runner interface of IDE like PyCharm or Visual Studio Code.

## Build

The version number of this project is automatically determined based on the latest git tag through `setuptools_scm`.
To create a new version, create a new tag and push it to the repository:
```bash
git tag -a v0.1.0 -m "Version 0.1.0"
git push origin v0.1.0
```
Please change the version number accordingly.

To build the package, use the following command:
```bash
tox -e build
```

Also, you can remove old distribution files and temporary build artifacts (`./build` and `./dist`) using the following command:
```bash
tox -e clean
```

## Publish

To publish the package to a package index server, use the following command:
```bash
tox -e publish
```
By default, it uses `testpypi`. If you want to publish the package to be publicly accessible in PyPI, use the `-- --repository pypi` option.
