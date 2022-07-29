import pathlib
import configparser

__version__ = "0.3.1"

# Load the configuration settings.
here = pathlib.Path(__file__).parent.resolve()
settings = configparser.ConfigParser()
settings.read(here / "config.ini")

# Go here if config.ini exists (don't crash if the project is not yet configured.)
if "Paths" in settings:
    try:
        data_dir = settings["Paths"]["data_dir"]
    except KeyError as err:
        continue

    config = {"data_dir": data_dir}
else:
    config = {"data_dir": pathlib.Path.home() / 'sampex-data'}

from sampex.load import HILT
from sampex.load import PET
from sampex.load import LICA
from sampex.load import Attitude
from sampex.download import Downloader
from sampex.load import date2yeardoy
from sampex.load import yeardoy2date