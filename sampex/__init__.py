import warnings
import pathlib
import configparser

__version__ = "0.2.1"

# Load the configuration settings.
here = pathlib.Path(__file__).parent.resolve()
settings = configparser.ConfigParser()
settings.read(here / "config.ini")

# Go here if config.ini exists (don't crash if the project is not yet configured.)
if "Paths" in settings:
    try:
        sampex_code_dir = settings["Paths"]["sampex_code_dir"]
        sampex_data_dir = settings["Paths"]["sampex_data_dir"]
    except KeyError as err:
        warnings.warn(
            "The sampex package did not find the config.ini file. "
            'Did you run "python3 -m sampex config"?'
        )

    config = {"sampex_code_dir": sampex_code_dir, "sampex_data_dir": sampex_data_dir}

else:
    warnings.warn('sampex is not configured. Run "python3 -m sampex config"')
    config = {}

from sampex.load import HILT
from sampex.load import PET
from sampex.load import LICA
from sampex.load import Attitude
from sampex.load import date2yeardoy
from sampex.load import yeardoy2date