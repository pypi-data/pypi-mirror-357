# fs.filefs: Custom filesystem for pyfilesystem2

This package provides `FileFS`, a custom filesystem for [pyfilesystem2](https://pyfilesystem2.readthedocs.io/) that allows you to mount files from other filesystems.

## Installation

```sh
pip install fs.filefs
```

## Usage Example

```python
from fs.osfs import OSFS
from fs.filefs import FileFS

image_fs = OSFS("~/images")
file_fs = FileFS()
file_fs.add_file("screenshot_1.png", image_fs)
file_fs.add_file("screenshot_2.png", image_fs, name="img_2.png")

print(file_fs.listdir("/"))  # ['screenshot_1.png', 'img_2.png']
```

## Develpment

```sh
# Install package in editable mode
pip install -e .

# Run tests
python -m unittest discover -s tests
```
