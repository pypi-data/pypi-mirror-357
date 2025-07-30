"""
DotTHz File Interface

This module defines classes and methods to read, write, and manipulate `.thz`
files, a format for storing terahertz time-domain spectroscopy (THz-TDS)
measurements. It supports automatic saving, metadata handling, and dataset
management using HDF5.

Classes:
--------
- DotthzMetaData: Stores user and measurement metadata.
- DotthzFile: Handles reading/writing `.thz` files and provides access to
stored measurements.

Dependencies:
-------------
- numpy
- h5py
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Union
from collections.abc import Iterable
from warnings import warn
import numpy as np
import h5py
import warnings

warnings.simplefilter("always", DeprecationWarning)


@dataclass
class DotthzMetaData:
    """An optional data class holding metadata for measurements in the .thz
    file format.

    Attributes
    ----------
    user : str
        The user who performed the measurement.
    email : str
        The email of the user.
    orcid : str
        The ORC ID of the user.
    institution : str
        The institution the user belongs to.
    description : str
        A description of the measurement.
    md : dict
        A dictionary of custom metadata (e.g. thickness, temperature, etc.).
    version : str, optional
        The version of the .thz file standard used.
        Defaults to "1.00".
    mode : str
        The measurement modality (e.g. transmission).
    instrument : str
        The instrument used to perform the measurement.
    time : str
        Timestamp of when the measurement was conducted.
    date : str
        The date on which the measurement was conducted.
    """
    user: str = ""
    email: str = ""
    orcid: str = ""
    institution: str = ""
    description: str = ""
    md: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.00"
    mode: str = ""
    instrument: str = ""
    time: str = ""
    date: str = ""

    def add_field(self, key, value):
        """
        Add a custom metadata field.

        Parameters
        ----------
        key : str
            Name of the metadata field.
        value : Any
            Value of the metadata field.
        """
        self.md[key] = value


class DotthzFile:
    """
    Interface for reading, writing, and managing measurements in the `.thz`
    file format.

    This class provides persistent storage of THz time-domain spectroscopy
    data via HDF5.

    Supports context manager (`with` statement) for automatic file handling.
    """

    def __init__(self, name: Union[str, Path], mode="r",
                 driver=None, libver=None,
                 userblock_size=None, swmr=False, rdcc_nslots=None,
                 rdcc_nbytes=None, rdcc_w0=None, track_order=None,
                 fs_strategy=None, fs_persist=False, fs_threshold=1,
                 fs_page_size=None, page_buf_size=None, min_meta_keep=0,
                 min_raw_keep=0, locking=None, alignment_threshold=1,
                 alignment_interval=1, meta_block_size=None, **kwds):
        self.file = h5py.File(name, mode, driver=driver, libver=libver,
                              userblock_size=userblock_size, swmr=swmr,
                              rdcc_nslots=rdcc_nslots, rdcc_nbytes=rdcc_nbytes,
                              rdcc_w0=rdcc_w0, track_order=track_order,
                              fs_strategy=fs_strategy, fs_persist=fs_persist,
                              fs_threshold=fs_threshold,
                              fs_page_size=fs_page_size,
                              page_buf_size=page_buf_size,
                              min_meta_keep=min_meta_keep,
                              min_raw_keep=min_raw_keep, locking=locking,
                              alignment_threshold=alignment_threshold,
                              alignment_interval=alignment_interval,
                              meta_block_size=meta_block_size, **kwds)

    def __enter__(self):
        # Enable the use of the `with` statement.
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Close any resources if applicable.
        if self.file is not None:
            self.file.close()
            self.file = None

    def __getitem__(self, key):
        # Create a group if it doesn't already exist.
        if key not in self.keys():
            self.create_group(key)

        # Return a DotthzMeasurementWrapper for the group
        return DotthzMeasurementWrapper(self.file[key])

    def __setitem__(self, key, group):
        # group must be an h5py.Group or something copyable
        self.file.copy(group, key)

    def __iter__(self):
        return iter(self.file)

    def __len__(self):
        return len(self.file)

    def items(self):
        """
        Get a view object on member items
        """
        return ((name, DotthzMeasurementWrapper(group))
                for name, group
                in self.file.items())

    def keys(self):
        """
        Get a view object on member names
        """
        return self.file.keys()

    def values(self):
        """
        Get a view object on member objects
        """
        return self.file.values()

    def create_measurement(self, name: str):
        """
        create a new measurement / group in the `.thz` file.
        :param name:

        .. deprecated:: 1.0.0
            Use .items() instead.
        """
        warnings.warn(
            "create_measurement  is deprecated and will be removed "
            "in a future version. Use file[measurement_name] instead. If the measurement does not exist, it will be created.",
            DeprecationWarning,
            stacklevel=2
        )
        return self.create_group(name)

    def create_group(self, name: str):
        """
        create a new measurement / group in the `.thz` file.
        :param name:
        """
        return self.file.create_group(name)

    def get_measurement_names(self):
        """
        Return a list of all measurement names in the file object as strings.
        """
        return [str(name) for name in self.keys()]

    def get_measurements(self):
        """
        Return a dict of all measurements in the file object.

        .. deprecated:: 1.0.0
            Use .items() instead.
        """
        warnings.warn(
            "get_measurements  is deprecated and will be removed "
            "in a future version. Use .items() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self

    @property
    def measurements(self):
        warnings.warn(
            "measurements is deprecated and will be removed "
            "in a future version. Use self instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self

    def get(self, name):
        """
        Get a measurement / group in the `.thz` file by name
        :param name:
        :return: HDF5 group
        """
        return DotthzMeasurementWrapper(self.file[name])

    def get_measurement(self, name):
        """Return the specified measurement from the file object.

        .. deprecated:: 1.0.0
            Use `file[name]` or `file.get(name)` instead.
        """
        warnings.warn(
            "get_measurement is deprecated and will be removed"
            " in a future version. Use file[name] or file.get(name) instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self[name]


class DotthzMeasurementWrapper:
    def __init__(self, h5py_group):
        self.group = h5py_group

    @property
    def datasets(self):
        """
        Memory-mapped HDF5 Dataset objects
        """
        return DatasetProxy(self.group)

    @property
    def metadata(self):
        """
        Memory-mapped HDF5 Attributes / Metadata
        """
        return MetadataProxy(self.group.attrs)

    def set_metadata(self, metadata: DotthzMetaData):
        """Sets metadata in the HDF5 group based on the provided
        DotthzMetaData instance."""

        # Set general metadata
        self.group.attrs["description"] = metadata.description
        self.group.attrs["mode"] = metadata.mode
        self.group.attrs["instrument"] = metadata.instrument
        self.group.attrs["time"] = metadata.time
        self.group.attrs["date"] = metadata.date
        self.group.attrs["version"] = metadata.version

        # Handle user metadata
        user_info = "/".join((metadata.orcid,
                              metadata.user,
                              metadata.email,
                              metadata.institution))

        self.group.attrs["user"] = user_info

        # Set additional metadata fields (md1, md2, etc.)
        for key, value in metadata.md.items():
            self.group.attrs[key] = value

        # Optionally, add "mdDescription" to describe which fields are included
        md_description = ",".join(metadata.md.keys())
        self.group.attrs["mdDescription"] = md_description

    def __getitem__(self, key):
        return self.datasets[key]

    def __setitem__(self, key, value):
        self.datasets[key] = value


class MetadataProxy:
    def __init__(self, attrs):
        self.attrs = attrs
        self.mapping = {
            alias: f"md{i + 1}" for i, alias in enumerate(
                self._get_descriptions(attrs.get("mdDescription", [])))
        }
        for attr in attrs:
            if attr != "mdDescription" and not attr.startswith("md"):
                self.mapping[attr] = attr

    def __str__(self):
        return f"MetadataProxy({list(self.mapping.keys())})"

    def __getitem__(self, key):
        return self._sanatize(self.attrs[self.mapping[key]])

    def __iter__(self):
        return iter(self.mapping)

    def __len__(self):
        return len(self.mapping)

    def __contains__(self, key):
        return key in self.mapping

    def __setitem__(self, key, value):
        if key not in self.mapping:
            # Add new md to mdDescription and update the mapping
            self._add_new_md(key)

        self.attrs[self.mapping[key]] = value

    def _get_descriptions(self, desc_in):
        # Handles inconsistent formatting for metadata descriptions.
        desc_in = self._sanatize(desc_in)

        if isinstance(desc_in, str):
            desc_list = [desc.strip() for desc in desc_in.split(",")]
        else:
            if not isinstance(desc_in, Iterable):
                desc_in = [desc_in]

            try:
                desc_list = list(map(str, desc_in))
            except (TypeError, ValueError):
                desc_list = []
                warn("Could not import descriptions.")

        return desc_list

    def _sanatize(self, md_in):
        # Reduces redundant iterables to base data.
        if isinstance(md_in, np.ndarray) and len(md_in) == 1:
            return self._sanatize(md_in[0])
        else:
            return md_in

    def _add_new_md(self, key):
        """Add a new dataset to the 'dsDescription' attribute."""
        # Update the description list with the new dataset
        md_description = self._get_descriptions(self.attrs.get("mdDescription",
                                                               []))

        if key not in md_description:
            md_description.append(key)

        self.attrs["mdDescription"] = ",".join(md_description)

        # Update the mapping with the new dataset
        new_index = len(md_description)
        self.mapping[key] = f"md{new_index}"

    def keys(self):
        """
        Get a view object on metadata / attribute keys.
        """
        return self.mapping.keys()

    def items(self):
        """
        Get a view object on metadata / attribute items.
        """
        return ((k, self.attrs[v]) for k, v in self.mapping.items())

    def values(self):
        """
        Get a view object on metadata / attribute values.
        """
        return (self.attrs[v] for v in self.mapping.values())

    def get_metadata_names(self):
        """
        Return a list of all attributes/metadata fields of the group as
        strings.
        """
        return [str(name) for name in self.keys()]


class DatasetProxy:
    def __init__(self, group):
        self.group = group
        self._initialize_mapping()

    def __str__(self):
        return f"DatasetProxy({list(self.keys())})"

    def __iter__(self):
        """Iterate over the dataset keys."""
        return iter(self.mapping)

    def __len__(self):
        """Return the number of datasets."""
        return len(self.mapping)

    def __contains__(self, key):
        """Check if a dataset exists."""
        return key in self.mapping

    def __getitem__(self, key):
        """Retrieve the dataset corresponding to the key."""
        if key not in self.mapping:
            raise KeyError(
                f"Dataset name '{key}' not found in 'dsDescription'.")
        return self.group[self.mapping[key]]

    def __setitem__(self, key, value):
        """Create or update a dataset in the group."""
        # Check if the dataset already exists, otherwise add it
        if key not in self.mapping:
            # Add new dataset to dsDescription and update the mapping
            self._add_new_dataset(key)

        ds_name = self.mapping[key]
        if ds_name in self.group:
            del self.group[ds_name]

        self.group.create_dataset(ds_name, data=value)

    def _get_descriptions(self, desc_in):
        # Handles inconsistent formatting for metadata descriptions.
        desc_in = self._sanatize(desc_in)

        if isinstance(desc_in, str):
            desc_list = [desc.strip() for desc in desc_in.split(",")]
        else:
            if not isinstance(desc_in, Iterable):
                desc_in = [desc_in]

            try:
                desc_list = list(map(str, desc_in))
            except (TypeError, ValueError):
                desc_list = []
                warn("Could not import descriptions.")

        return desc_list

    def _sanatize(self, md_in):
        # Reduces redundant iterables to base data.
        if isinstance(md_in, np.ndarray) and len(md_in) == 1:
            return self._sanatize(md_in[0])
        else:
            return md_in

    def _initialize_mapping(self):
        """Initialize or update the mapping for dataset names."""
        aliases = [alias.strip() for alias in self._get_descriptions(
            self.group.attrs.get("dsDescription", []))]
        self.mapping = {alias: f"ds{i + 1}" for i, alias in enumerate(aliases)}

    def _add_new_dataset(self, key):
        """Add a new dataset to the 'dsDescription' attribute."""
        # Update the description list with the new dataset
        ds_description = self._get_descriptions(
            self.group.attrs.get("dsDescription", []))

        if key not in ds_description:
            ds_description.append(key)

        self.group.attrs["dsDescription"] = ",".join(ds_description)

        # Update the mapping with the new dataset
        new_index = len(ds_description)
        self.mapping[key] = f"ds{new_index}"

    def get(self, key):
        """Retrieve the dataset corresponding to the key."""
        if key not in self.mapping:
            raise KeyError(
                f"Dataset name '{key}' not found in 'dsDescription'.")
        return self.group[self.mapping[key]]

    def keys(self):
        """Return the dataset keys."""
        return self.mapping.keys()

    def items(self):
        """Return the dataset name-item pairs."""
        return ((k, self.group[v]) for k, v in self.mapping.items())

    def values(self):
        """Return the dataset values."""
        return (self.group[v] for v in self.mapping.values())

    def get_dataset_names(self):
        """
        Return a list of all dataset names of the group as strings.
        """
        return [str(name) for name in self.keys()]
