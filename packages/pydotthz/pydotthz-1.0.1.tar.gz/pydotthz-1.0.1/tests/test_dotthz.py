import unittest
from pydotthz import DotthzFile, DotthzMetaData
import numpy as np
from tempfile import NamedTemporaryFile
from pathlib import Path
import os


class TestDotthzFile(unittest.TestCase):

    def test_copy_and_compare_dotthz_files(self):
        root = Path(__file__).resolve().parent
        paths = [root / "test_files" / "PVDF_520um.thz", root / "test_files" / "2_VariableTemperature.thz"]
        for path in paths:
            # Create a temporary file to save the copy
            with NamedTemporaryFile(delete=False) as temp_file:
                copy_file_path = temp_file.name

            # Load data from the original file
            with DotthzFile(path) as original_dotthz_file, DotthzFile(copy_file_path, "w") as copied_dotthz_file:
                # test writing all measurements at once
                for group_name, group in original_dotthz_file.items():
                    copied_dotthz_file[group_name] = group.group  # Access the raw h5py.Group

            # Load data from the new copy file
            with DotthzFile(path) as original_dotthz_file, DotthzFile(copy_file_path) as copied_dotthz_file:
                original_measurements = original_dotthz_file
                # Compare the original and copied Dotthz structures
                self.assertEqual(len(original_measurements), len(copied_dotthz_file))

                for group_name, original_measurement in original_measurements.items():
                    copied_measurement = copied_dotthz_file[group_name]
                    self.assertIsNotNone(copied_measurement)

                    # Compare metadata fields
                    self.assertEqual(original_measurement.metadata["user"], copied_measurement.metadata["user"])
                    self.assertEqual(original_measurement.metadata["description"],
                                     copied_measurement.metadata["description"])
                    self.assertEqual(original_measurement.metadata["thzVer"], copied_measurement.metadata["thzVer"])
                    self.assertEqual(original_measurement.metadata["mode"], copied_measurement.metadata["mode"])
                    self.assertEqual(original_measurement.metadata["instrument"],
                                     copied_measurement.metadata["instrument"])
                    self.assertEqual(original_measurement.metadata["time"], copied_measurement.metadata["time"])

                    # Compare datasets
                    self.assertEqual(len(original_measurement.datasets), len(copied_measurement.datasets))
                    for dataset_name, original_dataset in original_measurement.datasets.items():
                        copied_dataset = copied_measurement.datasets[dataset_name]
                        self.assertIsNotNone(copied_dataset)
                        np.testing.assert_array_equal(original_dataset, copied_dataset)

            # Clean up temporary file
            os.remove(copy_file_path)

    def test_dotthz_save_and_load(self):
        with NamedTemporaryFile(delete=False) as temp_file:
            path = temp_file.name

        # Initialize test data for Dotthz
        datasets = {
            "ds1": np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
        }

        # create deep copy
        original_datasets = {key: val for key, val in datasets.items()}

        metadata = DotthzMetaData(
            user="Test User",
            email="test@example.com",
            orcid="0000-0001-2345-6789",
            institution="Test Institute",
            description="Test description",
            md={"md1": "Thickness (mm)"},
            version="1.00",
            mode="Test mode",
            instrument="Test instrument",
            time="12:34:56",
            date="2024-11-08"
        )

        with DotthzFile(path, "w") as file_to_write:
            # test writing measurement by measurement
            file_to_write["Measurement 1"].set_metadata(metadata)
            file_to_write["Measurement 1"]["ds1"] = datasets["ds1"]

        # Load from the temporary file
        with DotthzFile(path) as loaded_file:
            # Compare original and loaded data
            self.assertEqual(1, len(loaded_file))

            loaded_measurement = loaded_file.get("Measurement 1")
            self.assertIsNotNone(loaded_measurement)

            # Compare metadata fields
            self.assertEqual(metadata.description, loaded_measurement.metadata["description"])
            self.assertEqual(metadata.version, loaded_measurement.metadata["version"])
            self.assertEqual(metadata.mode, loaded_measurement.metadata["mode"])
            self.assertEqual(metadata.instrument, loaded_measurement.metadata["instrument"])
            self.assertEqual(metadata.time, loaded_measurement.metadata["time"])

            # Compare datasets
            self.assertEqual(len(original_datasets), len(loaded_measurement.datasets))
            for dataset_name, dataset in original_datasets.items():
                loaded_dataset = loaded_measurement.datasets.get(dataset_name)
                self.assertIsNotNone(loaded_dataset)
                np.testing.assert_array_equal(dataset, loaded_dataset)

        # Clean up temporary file
        os.remove(path)

    def test_dotthz_key(self):
        with NamedTemporaryFile(delete=False) as temp_file:
            path = temp_file.name

        # Initialize test data for Dotthz
        datasets = {
            "ds1": np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
        }

        # create deep copy
        original_datasets = {key: val for key, val in datasets.items()}

        metadata = DotthzMetaData(
            user="Test User",
            email="test@example.com",
            orcid="0000-0001-2345-6789",
            institution="Test Institute",
            description="Test description",
            md={"md1": "Thickness (mm)"},
            version="1.00",
            mode="Test mode",
            instrument="Test instrument",
            time="12:34:56",
            date="2024-11-08"
        )

        with DotthzFile(path, "w") as file_to_write:
            # test writing measurement by measurement
            file_to_write["Measurement 1"].set_metadata(metadata)
            file_to_write["Measurement 1"]["ds1"] = datasets["ds1"]

        # Load from the temporary file
        with DotthzFile(path) as loaded_file:
            # Compare original and loaded data
            self.assertEqual(1, len(loaded_file))

            loaded_measurement = loaded_file["Measurement 1"]
            self.assertIsNotNone(loaded_measurement)

            # Compare metadata fields
            self.assertEqual(metadata.description, loaded_measurement.metadata["description"])
            self.assertEqual(metadata.version, loaded_measurement.metadata["version"])
            self.assertEqual(metadata.mode, loaded_measurement.metadata["mode"])
            self.assertEqual(metadata.instrument, loaded_measurement.metadata["instrument"])
            self.assertEqual(metadata.time, loaded_measurement.metadata["time"])

            # Compare datasets
            self.assertEqual(len(original_datasets), len(loaded_measurement.datasets))
            for dataset_name, dataset in original_datasets.items():
                loaded_dataset = loaded_measurement.datasets[dataset_name]
                self.assertIsNotNone(loaded_dataset)
                np.testing.assert_array_equal(dataset, loaded_dataset)

        # Clean up temporary file
        os.remove(path)

    def test_dotthz_extend_existing_dataset(self):
        with NamedTemporaryFile(delete=False) as temp_file:
            path = temp_file.name

        # Initialize test data for Dotthz
        metadata = DotthzMetaData(
            user="Test User",
            email="test@example.com",
            orcid="0000-0001-2345-6789",
            institution="Test Institute",
            description="Test description",
            md={"md1": "Thickness (mm)"},
            version="1.00",
            mode="Test mode",
            instrument="Test instrument",
            time="12:34:56",
            date="2024-11-08"
        )

        with DotthzFile(path, "w") as file_to_write:
            file_to_write["Measurement 1"].set_metadata(metadata)
            file_to_write["Measurement 1"]["ds1"] = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
            file_to_write["Measurement 1"]["ds1"][0, 0] = 0.0

        # Load from the temporary file
        with DotthzFile(path) as loaded_file:
            # Compare original and loaded data
            self.assertEqual(1, len(loaded_file))

            group_name = "Measurement 1"
            loaded_measurement = loaded_file[group_name]

            self.assertIsNotNone(loaded_measurement)

            # Compare metadata fields
            self.assertEqual(metadata.description, loaded_measurement.metadata["description"])
            self.assertEqual(metadata.version, loaded_measurement.metadata["version"])
            self.assertEqual(metadata.mode, loaded_measurement.metadata["mode"])
            self.assertEqual(metadata.instrument, loaded_measurement.metadata["instrument"])
            self.assertEqual(metadata.time, loaded_measurement.metadata["time"])

            # Compare datasets
            self.assertEqual(1, len(loaded_measurement.datasets))

            dataset_name = "ds1"
            loaded_dataset = loaded_measurement.datasets[dataset_name]
            self.assertIsNotNone(loaded_dataset)
            np.testing.assert_array_equal(loaded_dataset, np.array([[0.0, 2.0], [3.0, 4.0]], dtype=np.float32))

        # Clean up temporary file
        os.remove(path)

    def test_dotthz_extend_existing_file_with_measurement(self):
        with NamedTemporaryFile(delete=False) as temp_file:
            path = temp_file.name

        # Initialize test data for Dotthz

        metadata = DotthzMetaData(
            user="Test User",
            email="test@example.com",
            orcid="0000-0001-2345-6789",
            institution="Test Institute",
            description="Test description",
            md={"md1": "Thickness (mm)"},
            version="1.00",
            mode="Test mode",
            instrument="Test instrument",
            time="12:34:56",
            date="2024-11-08"
        )

        with DotthzFile(path, "w") as file_to_write:
            file_to_write["Measurement 1"].set_metadata(metadata)
            file_to_write["Measurement 1"]["ds1"] = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
            file_to_write["Measurement 1"]["ds2"] = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)

        with DotthzFile(path, "r+") as file_to_extend:
            file_to_extend["Measurement 2"].set_metadata(metadata)
            file_to_extend["Measurement 2"]["ds1"] = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
            file_to_extend["Measurement 2"]["ds2"] = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)

        # Load from the temporary file
        with DotthzFile(path) as loaded_file:
            # Compare original and loaded data
            self.assertEqual(2, len(loaded_file))

            for measurement_name, loaded_measurement in loaded_file.items():
                self.assertIsNotNone(loaded_measurement)

                # Compare metadata fields
                self.assertEqual(metadata.description, loaded_measurement.metadata["description"])
                self.assertEqual(metadata.version, loaded_measurement.metadata["version"])
                self.assertEqual(metadata.mode, loaded_measurement.metadata["mode"])
                self.assertEqual(metadata.instrument, loaded_measurement.metadata["instrument"])
                self.assertEqual(metadata.time, loaded_measurement.metadata["time"])

                # Compare datasets
                self.assertEqual(2, len(loaded_measurement.datasets))

                dataset_name = "ds1"
                loaded_dataset = loaded_measurement.datasets[dataset_name]
                self.assertIsNotNone(loaded_dataset)
                np.testing.assert_array_equal(loaded_dataset, np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32))

        # Clean up temporary file
        os.remove(path)

    def test_dotthz_extend_existing_measurement_with_dataset(self):
        with NamedTemporaryFile(delete=False) as temp_file:
            path = temp_file.name

        # Initialize test data for Dotthz

        metadata = DotthzMetaData(
            user="Test User",
            email="test@example.com",
            orcid="0000-0001-2345-6789",
            institution="Test Institute",
            description="Test description",
            md={"md1": "Thickness (mm)"},
            version="1.00",
            mode="Test mode",
            instrument="Test instrument",
            time="12:34:56",
            date="2024-11-08"
        )

        with DotthzFile(path, "w") as file_to_write:
            file_to_write["Measurement 1"].set_metadata(metadata)
            file_to_write["Measurement 1"]["ds1"] = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
            file_to_write["Measurement 1"]["ds2"] = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)

        with DotthzFile(path, "r+") as file_to_extend:
            file_to_extend["Measurement 1"]["ds3"] = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)

        # Load from the temporary file
        with DotthzFile(path) as loaded_file:
            # Compare original and loaded data
            self.assertEqual(1, len(loaded_file))

            loaded_measurement = loaded_file["Measurement 1"]
            self.assertIsNotNone(loaded_measurement)

            # Compare metadata fields
            self.assertEqual(metadata.description, loaded_measurement.metadata["description"])
            self.assertEqual(metadata.version, loaded_measurement.metadata["version"])
            self.assertEqual(metadata.mode, loaded_measurement.metadata["mode"])
            self.assertEqual(metadata.instrument, loaded_measurement.metadata["instrument"])
            self.assertEqual(metadata.time, loaded_measurement.metadata["time"])

            # Compare datasets
            self.assertEqual(3, len(loaded_measurement.datasets))

            for dataset_name, dataset in loaded_measurement.datasets.items():
                self.assertIsNotNone(dataset)
                np.testing.assert_array_equal(np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32), dataset)

        # Clean up temporary file
        os.remove(path)

    def test_dotthz_extend_existing_measurement_with_existing_metadata_attribute(self):
        with NamedTemporaryFile(delete=False) as temp_file:
            path = temp_file.name

        # Initialize test data for Dotthz

        metadata = DotthzMetaData(
            user="Test User",
            email="test@example.com",
            orcid="0000-0001-2345-6789",
            institution="Test Institute",
            description="Test description",
            md={"md1": "Thickness (mm)"},
            version="1.00",
            mode="Test mode",
            instrument="Test instrument",
            time="12:34:56",
            date="2024-11-08"
        )

        with DotthzFile(path, "w") as file_to_write:
            file_to_write["Measurement 1"].set_metadata(metadata)
            file_to_write["Measurement 1"]["ds1"] = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
            file_to_write["Measurement 1"]["ds2"] = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)

        with DotthzFile(path, "r+") as file_to_extend:
            file_to_extend["Measurement 1"].metadata["mode"] = "New Mode"

        # Load from the temporary file
        with DotthzFile(path) as loaded_file:
            # Compare original and loaded data
            self.assertEqual(1, len(loaded_file))

            loaded_measurement = loaded_file["Measurement 1"]
            self.assertIsNotNone(loaded_measurement)

            # Compare metadata fields
            self.assertEqual(metadata.description, loaded_measurement.metadata["description"])
            self.assertEqual(metadata.version, loaded_measurement.metadata["version"])
            self.assertEqual("New Mode", loaded_measurement.metadata["mode"])
            self.assertEqual(metadata.instrument, loaded_measurement.metadata["instrument"])
            self.assertEqual(metadata.time, loaded_measurement.metadata["time"])

            # Compare datasets
            self.assertEqual(2, len(loaded_measurement.datasets))

            for dataset_name, dataset in loaded_measurement.datasets.items():
                self.assertIsNotNone(dataset)
                np.testing.assert_array_equal(np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32), dataset)

        # Clean up temporary file
        os.remove(path)

    def test_dotthz_extend_existing_measurement_with_new_metadata_attribute(self):
        with NamedTemporaryFile(delete=False) as temp_file:
            path = temp_file.name

        # Initialize test data for Dotthz

        metadata = DotthzMetaData(
            user="Test User",
            email="test@example.com",
            orcid="0000-0001-2345-6789",
            institution="Test Institute",
            description="Test description",
            md={"md1": "Thickness (mm)"},
            version="1.00",
            mode="Test mode",
            instrument="Test instrument",
            time="12:34:56",
            date="2024-11-08"
        )

        with DotthzFile(path, "w") as file_to_write:
            file_to_write["Measurement 1"].set_metadata(metadata)
            file_to_write["Measurement 1"]["ds1"] = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
            file_to_write["Measurement 1"]["ds2"] = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)

        with DotthzFile(path, "r+") as file_to_extend:
            file_to_extend["Measurement 1"].metadata["new meta data"] = "Test"

        # Load from the temporary file
        with DotthzFile(path) as loaded_file:
            # Compare original and loaded data
            self.assertEqual(1, len(loaded_file))

            loaded_measurement = loaded_file["Measurement 1"]
            self.assertIsNotNone(loaded_measurement)

            # Compare metadata fields
            self.assertEqual(metadata.description, loaded_measurement.metadata["description"])
            self.assertEqual(metadata.version, loaded_measurement.metadata["version"])
            self.assertEqual(metadata.mode, loaded_measurement.metadata["mode"])
            self.assertEqual(metadata.instrument, loaded_measurement.metadata["instrument"])
            self.assertEqual(metadata.time, loaded_measurement.metadata["time"])
            self.assertEqual("Test", loaded_measurement.metadata["new meta data"])

            # Compare datasets
            self.assertEqual(2, len(loaded_measurement.datasets))

            for dataset_name, dataset in loaded_measurement.datasets.items():
                self.assertIsNotNone(dataset)
                np.testing.assert_array_equal(np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32), dataset)

        # Clean up temporary file
        os.remove(path)


if __name__ == "__main__":
    unittest.main()
