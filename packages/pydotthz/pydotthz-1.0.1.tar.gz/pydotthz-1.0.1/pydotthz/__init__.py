"""
PyDotTHz
=====

Provides classes for interacting with the .thz file format, a format for
storing data from terahertz time-domain spectroscopy measurements. For
more detail see: https://doi.org/10.1007/s10762-023-00947-w

The .thz file format is a domain specific implementation of the widely
used Hierarchical Data Format 5 standard. As such this package acts as
a wrapper around the h5py package, breaking up each HDF5 object into
multiple easier to use objects. A .thz file has the following internal
structure:

    .thz File
    |---->Measurement 1
    |     |---->Metadata
    |     |     |---->User
    |     |     |---->Temperature
    |     |     |...
    |     |---->Dataset 1
    |     |     |---->Electric Field
    |     |     |---->Time
    |     |---->Dataset 2
    |     |...
    |---->Measurement 2
    |...

This package will represent said file as a `DotthzFile` object, which serves
as a wrapper for the `Hdf5File` class.
This class is memory mapped to the file on the disk for quick and efficient
data access.
Datasets can take any structure but a shape (2, n) array is recommended.
Metadata/Attributes are also memory mapped and easily accessible for the user.

A `DotthzMetaData` object is optional but can be used for keeping track of the
meta-data outside the file context.
It contains multiple fixed attributes as defined in the .thz standard as well
as a dictionary of user defined attributes.

"""

from .pydotthz import (DotthzFile,
                       DotthzMetaData)

__all__ = [DotthzFile,
           DotthzMetaData]
