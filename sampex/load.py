# This program loads the HILT data and parses it into a nice format
import pathlib
import zipfile
import re
from datetime import datetime, date

import pandas as pd
import numpy as np

class HILT:
    """
    Load a day of HILT counts and convert the date and time to ``pd.Timestamp`` 
    objects. You need to explicitly call the ``.load()`` method to load the 
    file into memory.

    Once loaded, you can access the timestamps with HILT['time'] and
    counts array with HILT['counts']. Alternatively, the HILT.data
    attribute is a pd.DataFrame containing both the timestamps and 
    counts.

    Parameters
    ----------
    load_date: datetime.datetime, pd.Timestamp
        The date to load the data.
    verbose: bool
        If True, will notify you when data is loaded. This is useful when
        loading a lot of data and the computer seems unresponsive.

    Example
    -------
    | from datetime import datetime
    | 
    | import matplotlib.pyplot as plt
    | 
    | import sampex
    | 
    | day = datetime(2007, 1, 20)
    | 
    | h = sampex.HILT(day)
    | h.load()
    |
    | fig, ax = plt.subplots()
    | ax.step(h['time'], h['counts'], label='HILT', where='post')
    | plt.suptitle(f'SAMPEX-HILT | {day.date()}')
    | plt.show()
    """

    def __init__(self, load_date, verbose=False):
        self.load_date = load_date
        self.load_date_str = date2yeardoy(self.load_date)
        self.verbose = verbose

        # Get the filename and search for it. If multiple or no
        # unique files are found this will raise an assertion error.
        file_name_glob = f"hhrr{self.load_date_str}*"
        matched_files = list(pathlib.Path(config["sampex_data_dir"], "hilt").rglob(file_name_glob))
        # 1 if there is just one file, and 2 if there is a file.txt and
        # file.txt.zip files.
        assert len(matched_files) in [1, 2], (
            f"{len(matched_files)} matched HILT files found."
            f"\nSearch string: {file_name_glob}"
            f'\nSearch directory: {pathlib.Path(config["sampex_data_dir"], "hilt")}'
            f"\nmatched files: {matched_files}"
        )
        self.file_path = matched_files[0]
        self.state = self._get_state()
        return

    def load(self, extract=False):
        """
        Load the HILT data into memory

        Parameters
        ----------
        extract: bool
            Wether or not to extract the HILT file if it is zipped.

        Returns
        -------
        pd.DataFrame
            The HILT data that is also saved as a ``HILT.data`` attribute.
        """
        # Load the zipped data and extract if a zip file was found.
        if self.file_path.suffix == "zip":
            self.read_zip(self.file_path, extract=extract)
        else:
            self.read_csv(self.file_path)

        # Parse the seconds of day time column to datetime objects
        self.parse_time()

        if (self.state == 4) or (self.state == 2):
            self.data = self.reshape_20ms_state()
        else:
            raise NotImplementedError("State 1 and 3 are not implemented yet.")
        return self.data

    def __getitem__(self, _slice):
        """
        Allows you to access data via HILT['time'] or HILT['counts'] 
        """
        if isinstance(_slice, str):
            if "time" in _slice.lower():
                return self.data.index
            if "count" in _slice.lower():
                return self.data["counts"].to_numpy()
        else:
            raise IndexError('Slices other than "time" or "counts" is not allowed.')

    def read_zip(self, zip_path, extract=False):
        """
        Open the zip file and load in the csv file. If extract=False than the file
        will only be opened and not extracted to a text file in the 
        sampex/data/hilt directory. 
        """
        txt_name = zip_path.stem
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            if extract:
                zip_ref.extractall(zip_path.parent)
                self.read_csv(zip_path.parent / txt_name)
            else:
                with zip_ref.open(txt_name) as f:
                    self.read_csv(f)
        return

    def read_csv(self, path):
        """
        Reads in the CSV file given either the filename or the 
        zip file reference
        """
        if self.verbose:
            print(f"Loading SAMPEX-HILT data on {self.load_date.date()} from {path.name}")
        self._hilt_csv = pd.read_csv(path, sep=" ")
        return

    def parse_time(self):
        """ 
        Parse the seconds of day column to a datetime column. 
        """
        # Check if the seconds are monotonically increasing.
        np_time = self._hilt_csv["Time"].to_numpy()
        if np.any(np_time[1:] < np_time[:-1]):
            raise ValueError(f"The SAMPEX HILT data is not in order for {self.load_date_str}.")
        # Convert seconds of day to a datetime object.
        day_seconds_obj = pd.to_timedelta(self._hilt_csv["Time"], unit="s")
        self._hilt_csv["Time"] = pd.Timestamp(self.load_date.date()) + day_seconds_obj
        self._hilt_csv.index = self._hilt_csv["Time"]
        del (self._hilt_csv["Time"])
        return

    def _get_state(self):
        """
        Given the date, determine what state the HILT instrument was operating
        in.

        More info: https://izw1.caltech.edu/sampex/DataCenter/docs/HILThires.html
        """
        if ((int(self.load_date_str) >= 1992187) and (int(self.load_date_str) <= 1994069)) or (
            (int(self.load_date_str) >= 1996044) and (int(self.load_date_str) <= 1996220)
        ):
            state = 1
        elif (int(self.load_date_str) >= 1994137) and (int(self.load_date_str) <= 1994237):
            state = 2
        elif (int(self.load_date_str) >= 1994237) and (int(self.load_date_str) <= 1995322):
            state = 3
        elif (int(self.load_date_str) >= 1996220) and (int(self.load_date_str) <= 2012312):
            state = 4
        else:
            raise ValueError(f"{self.load_date_str} does not match any known HILT state.")
        return state

    def reshape_20ms_state(self):
        """ 
        This function reshapes the HILT counts to 20 ms resolution assuming 
        the data is in state 2 or 4. The counts represent the sum from the 4 SSDs.

        Returns
        -------
        DataFrame
            datetime index and "counts" column.
        """
        resolution_ms = 20E-3
        # Resolve the counts using numpy (most efficient way with
        # static memory allocation)
        self.counts = np.nan * np.zeros(5 * self._hilt_csv.shape[0], dtype=int)
        for i in [0, 1, 2, 3]:
            self.counts[i::5] = self._hilt_csv[f"Rate{i+1}"]
        # This line is different because rate5 is 100 ms SSD4 data.
        self.counts[4::5] = self._hilt_csv["Rate6"]

        # Resolve the time array.
        self.times = np.nan * np.zeros(5 * self._hilt_csv.shape[0], dtype=object)
        for i in [0, 1, 2, 3, 4]:
            self.times[i::5] = self._hilt_csv.index + pd.to_timedelta(resolution_ms * i, unit="s")
        return pd.DataFrame(data={"counts": self.counts}, index=self.times)


class PET:
    """
    Load a day of PET counts and convert the date and time to ``pd.Timestamp`` 
    objects. You need to explicitly call the ``.load()`` method to load the 
    file into memory.

    Once loaded, you can access the timestamps with PET['time'] and
    counts array with PET['counts']. Alternatively, the PET.data
    attribute is a pd.DataFrame containing both the timestamps and 
    counts (called P1_Rate in the original data).

    Parameters
    ----------
    load_date: datetime.datetime, pd.Timestamp
        The date to load the data.
    verbose: bool
        If True, will notify you when data is loaded. This is useful when
        loading a lot of data and the computer seems unresponsive.

    Example
    -------
    | from datetime import datetime
    | 
    | import matplotlib.pyplot as plt
    | 
    | import sampex
    | 
    | day = datetime(2007, 1, 20)
    | 
    | p = sampex.PET(day)
    | p.load()
    | 
    | fig, ax = plt.subplots()
    | ax.step(p['time'], p['counts'], label='PET', where='post')
    | plt.suptitle(f'SAMPEX-PET | {day.date()}')
    | plt.show()
    """

    def __init__(self, load_date, verbose=False) -> None:
        self.load_date = load_date
        self.load_date_str = date2yeardoy(self.load_date)
        self.verbose = verbose
        return

    def load(self):
        """
        Loads the PET data into self.data.
        """
        pet_path = self._find_file(self.load_date)
        if self.verbose:
            print(
                f"Loading SAMPEX-PET data on {self.load_date.date()} from"
                f" {pet_path.name}"
            )
        self.data = pd.read_csv(pet_path, sep=" ")
        self.data = self.data.rename(columns={"P1_Rate": "counts"})
        self.parse_time()
        return self.data

    def parse_time(self):
        """ 
        Parse the seconds of day column to a datetime column. 
        """
        # Check if the seconds are monotonically increasing.
        np_time = self.data["Time"].to_numpy()
        if np.any(np_time[1:] < np_time[:-1]):
            raise ValueError(f"The SAMPEX PET data is not in order for {self.load_date_str}.")
        # Convert seconds of day to a datetime object.
        day_seconds_obj = pd.to_timedelta(self.data["Time"], unit="s")
        self.data["Time"] = pd.Timestamp(self.load_date.date()) + day_seconds_obj
        self.data.index = self.data["Time"]
        del (self.data["Time"])
        return

    def __getitem__(self, _slice):
        """
        Allows you to access data via PET['time'] or PET['counts'] 
        """
        if isinstance(_slice, str):
            if "time" in _slice.lower():
                return self.data.index
            if "count" in _slice.lower():
                return self.data["counts"].to_numpy()
        else:
            raise IndexError('Slices other than "time" or "counts" is not allowed.')

    def _find_file(self, day):
        """
        Recursively searches the config['sampex_data_dir']/pet/ directory for the file.
        """
        file_name_glob = f"phrr{self.load_date_str}*"
        matched_files = list(pathlib.Path(config["sampex_data_dir"], "pet").rglob(file_name_glob))
        # 1 if there is just one file, and 2 if there is a file.txt and
        # file.txt.zip files.
        assert len(matched_files) == 1, (
            f"{len(matched_files)} matched PET files found."
            f"\nSearch string: {file_name_glob}"
            f'\nSearch directory: {pathlib.Path(config["sampex_data_dir"], "pet")}'
            f"\nmatched files: {matched_files}"
        )
        return matched_files[0]


class LICA:
    """
    Load a day of LICA counts and convert the date and time to ``pd.Timestamp`` 
    objects. You need to explicitly call the ``.load()`` method to load the 
    file into memory.

    Once loaded, you can access the timestamps with LICA['time']
    You can access the counts similarly, but the column names 
    must be one of these: D4+D3 D2+D1 Stop Start Low_Pri, or High_Pri.
    Alternatively, the LICA.data attribute is a pd.DataFrame containing 
    both the timestamps and counts.

    Parameters
    ----------
    load_date: datetime.datetime, pd.Timestamp
        The date to load the data.
    verbose: bool
        If True, will notify you when data is loaded. This is useful when
        loading a lot of data and the computer seems unresponsive.

    Example
    -------
    | from datetime import datetime
    | 
    | import matplotlib.pyplot as plt
    | 
    | import sampex
    | 
    | day = datetime(2007, 1, 20)
    | 
    | l = sampex.LICA(day)
    | l.load()
    | 
    | fig, ax = plt.subplots()
    | ax.step(l['time'], l['stop'], label='PET', where='post')
    | plt.suptitle(f'SAMPEX-LICA (stop) | {day.date()}')
    | plt.show()
    """

    def __init__(self, load_date, verbose=False) -> None:
        self.load_date = load_date
        self.load_date_str = date2yeardoy(self.load_date)
        self.verbose = verbose
        return

    def load(self):
        """
        Loads the LICA data into self.data.
        """
        lica_path = self._find_file()
        if self.verbose:
            print(
                f"Loading SAMPEX-LICA data on {self.load_date.date()} from"
                f" {lica_path.name}"
            )
        self.data = pd.read_csv(lica_path, sep=" ")
        self.parse_time()
        return self.data

    def parse_time(self, time_index=True):
        """ 
        Parse the seconds of day column to a datetime column. 
        If time_index=True, the time column will become the index.
        """
        # Check if the seconds are monotonically increasing.
        np_time = self.data["Time"].to_numpy()
        if np.any(np_time[1:] < np_time[:-1]):
            raise ValueError(f"The SAMPEX LICA data is not in order for {self.load_date_str}.")
        # Convert seconds of day to a datetime object.
        day_seconds_obj = pd.to_timedelta(self.data["Time"], unit="s")
        self.data["Time"] = pd.Timestamp(self.load_date.date()) + day_seconds_obj
        if time_index:
            self.data.index = self.data["Time"]
            del (self.data["Time"])
        return

    def _find_file(self):
        """
        Recursively searches the config['sampex_data_dir']/pet/ directory for the file.
        """
        file_name_glob = f"lhrr{self.load_date_str}*"
        matched_files = list(pathlib.Path(config["sampex_data_dir"], "lica").rglob(file_name_glob))
        # 1 if there is just one file, and 2 if there is a file.txt and
        # file.txt.zip files.
        assert len(matched_files) == 1, (
            f"{len(matched_files)} matched LICA files found."
            f"\nSearch string: {file_name_glob}"
            f'\nSearch directory: {pathlib.Path(config["sampex_data_dir"], "lica")}'
            f"\nmatched files: {matched_files}"
        )
        return matched_files[0]

    def __getitem__(self, _slice):
        """
        Allows you to access data via, for example, LICA['time'].
        """
        if isinstance(_slice, str):
            if "time" in _slice.lower():
                return self.data.index
            else:
                for column in self.data.columns:
                    if _slice.lower() in column.lower():
                        return self.data[column].to_numpy()
        else:
            raise IndexError(f'Slices other than "time" or {self.data.columns} are unsupported')


class Attitude:
    """ 
    Load a SAMEX attitude file that contains the desired day and convert 
    the date and time to ``pd.Timestamp``. You need to explicitly call 
    the ``.load()`` method to load the file into memory.

    Once loaded, you can access the timestamps with Attitude['time']
    You can access the other variables similarly. Alternatively, the 
    Attitude.data attribute is a pd.DataFrame containing both the 
    timestamps and attitude variables.

    Parameters
    ----------
    load_date: datetime.datetime, pd.Timestamp
        The date to load the data.
    verbose: bool
        If True, will notify you when data is loaded. This is useful when
        loading a lot of data and the computer seems unresponsive.

    Notes
    -----
    Attitude files span multiple days.

    Longitudes are transformed from (0 -> 360) to (-180 -> 180).
    

    Example
    -------
    | from datetime import datetime
    | 
    | import matplotlib.pyplot as plt
    | 
    | import sampex
    | 
    | day = datetime(2007, 1, 20)
    | 
    | a = sampex.Attitude(day)
    | a.load()
    | 
    | fig, ax = plt.subplots()
    | ax.step(a['time'], a['Altitude'], label='SAMPEX Altitude', where='post')
    | plt.suptitle(f'SAMPEX Altitude | {day.date()}')
    | plt.show()
    """

    def __init__(self, load_date, verbose=False):
        self.load_date = load_date
        self.load_date_str = date2yeardoy(load_date)
        self.verbose = verbose

        # Find the appropriate attitude file.
        self._find_attitude_file()
        return

    def load(self, columns="default", remove_old_time_cols=True):
        """ 
        Loads the attitude file. Only columns specified in the columns arg are 
        loaded to conserve memory.

        Notes
        -----
        The other than ``time``, the loaded columns are: GEO_Radius, GEO_Long, 
        GEO_Lat, Altitude, L_Shell, MLT, Mirror_Alt, Pitch, and Att_Flag

        Longitudes are transformed from (0 -> 360) to (-180 -> 180).
        """
        if self.verbose:
            print(
                f"Loading SAMPEX attitude data on {self.load_date.date()} from"
                f" {self.attitude_file.name}"
            )
        # A default set of hard-coded list of columns to load
        if columns == "default":
            columns = {
                0: "Year",
                1: "Day-of-year",
                2: "Sec_of_day",
                6: "GEO_Radius",
                7: "GEO_Long",
                8: "GEO_Lat",
                9: "Altitude",
                20: "L_Shell",
                22: "MLT",
                42: "Mirror_Alt",
                68: "Pitch",
                71: "Att_Flag",
            }
        # Open the attitude file stream
        with open(self.attitude_file) as f:
            # Skip the long header until the "BEGIN DATA" line
            self._skip_header(f)
            # Save the rest to a file using columns specified by the columns.keys() with the
            # columns values for the column names.
            self.data = pd.read_csv(
                f, delim_whitespace=True, names=columns.values(), usecols=columns.keys()
            )
        self._parse_attitude_datetime(remove_old_time_cols)
        # Transform the longitudes from (0 -> 360) to (-180 -> 180).
        self.data["GEO_Long"] = np.mod(self.data["GEO_Long"] + 180, 360) - 180
        return self.data

    def __getitem__(self, _slice):
        """
        Allows you to access data via, for example, Attitude['time'].
        """
        if isinstance(_slice, str):
            if "time" in _slice.lower():
                return self.data.index
            else:
                for column in self.data.columns:
                    if _slice.lower() in column.lower():
                        return self.data[column].to_numpy()
                raise KeyError(
                    f"{_slice} is an invalid column: Valid columns are: {self.data.columns} "
                )
        else:
            raise IndexError(f'Slices other than "time" or {self.data.columns} are unsupported')

    def _find_attitude_file(self):
        """ 
        Use pathlib.rglob to find the attitude file that contains 
        the DOY from self.load_date
        """
        attitude_files = sorted(
            list(pathlib.Path(config["sampex_data_dir"], "attitude").rglob("PSSet_6sec_*_*.txt"))
        )
        start_end_dates = [re.findall(r"\d+", str(f.name))[1:] for f in attitude_files]

        current_date_int = int(self.load_date_str)
        self.attitude_file = None

        for f, (start_date, end_date) in zip(attitude_files, start_end_dates):
            if (int(start_date) <= current_date_int) and (int(end_date) >= current_date_int):
                self.attitude_file = f
        if self.attitude_file is None:
            raise ValueError(
                f'A matched file not found in {pathlib.Path(config["sampex_data_dir"], "attitude")} '
                f"for YEARDOY={self.load_date_str}"
            )
        return self.attitude_file

    def _skip_header(self, f):
        """ 
        Read in the "f" attitude file stream line by line until the 
        "BEGIN DATA" line is reached. Then return the row index to the
        names from the parsed header.
        """
        for i, line in enumerate(f):
            if "BEGIN DATA" in line:
                # because for some reason the first attitude row has
                # an extra column so skip the first "normal" row.
                next(f)
                return
        return None

    def _parse_attitude_datetime(self, remove_old_time_cols):
        """
        Parse the attitude year, DOY, and second of day columns 
        into datetime objects. 
        """
        # Parse the dates by first making YYYY-DOY strings.
        year_doy = [f"{year}-{doy}" for year, doy in self.data[["Year", "Day-of-year"]].values]
        # Convert to date objects
        attitude_dates = pd.to_datetime(year_doy, format="%Y-%j")
        # Now add the seconds of day to complete the date and time.
        self.data.index = attitude_dates + pd.to_timedelta(self.data["Sec_of_day"], unit="s")
        # Optionally remove duplicate columns to conserve memory.
        if remove_old_time_cols:
            self.data.drop(["Year", "Day-of-year", "Sec_of_day"], axis=1, inplace=True)
        return


def date2yeardoy(day):
    """
    Converts a date into the "YYYYDOY" string format used extensively 
    for the SAMPEX file names.

    Parameters
    ----------
    day: str, datetime.datetime, pd.Timestamp
         A date.

    Returns
    -------
    str
        The corresponding YYYDOY string.
    """
    if isinstance(day, str):
        day = pd.to_datetime(day)

    # Figure out how to calculate the day of year (DOY)
    if isinstance(day, pd.Timestamp):
        doy = str(day.dayofyear).zfill(3)
    elif isinstance(day, (datetime, date)):
        doy = str(day.timetuple().tm_yday).zfill(3)
    return f"{day.year}{doy}"


def yeardoy2date(yeardoy: str):
    """
    Converts a date in the (year day-of-year) format (YEARDOY)
    into a datetime.datetime object.

    Parameters
    ----------
    yeardoy: str
        The date in the YYYDOY format

    Returns
    -------
    datetime.datetime
        The corresponding datetime object 
    """
    return datetime.strptime(yeardoy, "%Y%j")


if __name__ == "__main__":
    from datetime import datetime

    import matplotlib.pyplot as plt

    import sampex

    day = datetime(2007, 1, 20)

    h = sampex.HILT(day)
    h.load()

    fig, ax = plt.subplots()
    ax.step(h["time"], h["counts"], label="HILT", where="post")
    plt.suptitle(f"SAMPEX-HILT | {day.date()}")
    plt.show()
