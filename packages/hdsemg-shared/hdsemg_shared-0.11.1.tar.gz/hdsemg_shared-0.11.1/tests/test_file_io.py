import pytest
import numpy as np
from hdsemg_shared.fileio.file_io import EMGFile
from pathlib import Path

ROOT = Path(__file__).parent

MAT_PATH = ROOT / "data" / "PeHaOf20241107163930_Ramp01.mat"
OTB4_PATH = ROOT / "data" / "CE13_TibAnt_AM_04062025_Trap3.otb4"
OTB_PLUS_PATH = ROOT / "data" / "PeHaOf20241107163930_Ramp01.otb+"

def extract_str(value):
    """Flatten deeply nested array-like objects to extract a scalar string."""
    try:
        while isinstance(value, (np.ndarray, list)) and value.size > 0:
            value = value[0]
        if isinstance(value, np.generic):  # unwrap numpy string scalars
            value = value.item()
        return str(value)
    except Exception:
        return None

@pytest.mark.parametrize("path", [MAT_PATH, OTB4_PATH, OTB_PLUS_PATH])
def test_load_file_structure(path):
    """
    Test that the loaded file has the correct structure.
    """
    emg = EMGFile.load(path)

    # Check data shape
    assert emg.data.ndim == 2, "Data should be a 2D array."
    assert emg.time.ndim == 1, "Time should be a 1D array."

    # Check that data and time have compatible shapes
    assert emg.data.shape[0] == emg.time.shape[0], "Data and time must have the same number of samples."

    assert isinstance(extract_str(emg.description), str), "Description should a array of strings."

    # Check sampling frequency is a number
    assert isinstance(emg.sampling_frequency, (int, float)), "Sampling frequency should be a number."

    # Check file name is a string
    assert isinstance(emg.file_name, str), "File name should be a string."

    # Check file size is an integer
    assert isinstance(emg.file_size, int), "File size should be an integer."