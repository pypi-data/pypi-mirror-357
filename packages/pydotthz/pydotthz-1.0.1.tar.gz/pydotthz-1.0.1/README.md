# Interface with dotTHz files using Python

[![PEP8](https://github.com/dotTHzTAG/pydotthz/actions/workflows/format.yml/badge.svg)](https://github.com/dotTHzTAG/pydotthz/actions/workflows/format.yml)
[![PyPI](https://img.shields.io/pypi/v/pydotthz?label=pypi%20package)](https://pypi.org/project/pydotthz/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/pydotthz)](https://pypi.org/project/pydotthz/)

This crate provides an easy way to interface with [dotTHz](https://github.com/dotTHzTAG) files in Python.

Install it

```shell
pip install pydotthz
```

or

```shell
pip3 install pydotthz
```

and then use like specified in the following example:

```python
from pathlib import Path
import numpy as np
from pydotthz import DotthzFile, DotthzMetaData

if __name__ == "__main__":
    # Sample data
    time = np.linspace(0, 1, 100)  # your time array
    data = np.random.rand(100)  # example 3D data array

    # save the file
    path1 = Path("test1.thz")
    with DotthzFile(path1, "w") as file:
        file.create_measurement("Measurement 1")

        # create meta-data
        metadata = DotthzMetaData()
        metadata.user = "John Doe"
        metadata.version = "1.00"
        metadata.instrument = "Toptica TeraFlash Pro"
        metadata.mode = "THz-TDS/Transmission"

        file["Measurement 1"].set_metadata(metadata)

        # for thzVer 1.00, we need to transpose the array!
        # important: do not manipulate keys on the `dataset` field, otherwise it won't be written to the file.
        file["Measurement 1"]["Sample"] = np.array([time, data]).T

```

Further examples (e.g. THz image scans) can be found in the [examples](https://github.com/dotTHzTAG/pydotthz/examples) directory.

### Requirements

Requires [hdf5](https://www.hdfgroup.org/solutions/hdf5/) to be installed.
