import argparse
from datetime import datetime

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import matplotlib.dates
import numpy as np

from sampex import HILT, PET, LICA, Attitude

def main():
    parser = argparse.ArgumentParser(description=("This script plots the " "SAMPEX data"))
    parser.add_argument(
        "date", nargs=3, type=int, help=("The date to plot the data. Must be in the YYYY MM DD format.")
    )
    parser.add_argument(
        "--yscale",
        type=str,
        default="linear",
        help=('Set the yscale. Can be either "linear" (default) or "log".'),
    )
    args = parser.parse_args()

    day = datetime(*args.date)

    # Load data
    p = PET(day)
    p.load()
    h = HILT(day)
    h.load()
    a = Attitude(day)
    a.load()
    l = LICA(day)
    l.load()

    # Plot it
    def format_fn(tick_val, tick_pos):
        """
        The tick magic happens here. pyplot gives it a tick time, and this function 
        returns the closest label to that time. Read docs for FuncFormatter().
        """
        # Find the nearest time within 6 seconds (the cadence of the SAMPEX attitude files)
        tick_time = matplotlib.dates.num2date(tick_val).replace(tzinfo=None)
        i_min_time = np.argmin(np.abs(a["time"] - tick_time))
        if np.abs(a["time"][i_min_time] - tick_time).total_seconds() > 6:
            raise ValueError(f"Nearest timestamp to tick_time is more than 6 seconds away")
        pd_index = a["time"][i_min_time]
        # Cast np.array as strings so that it can insert the time string.
        values = a.data.loc[pd_index, x_labels.values()].to_numpy().round(2).astype(str)
        values = np.insert(values, 0, pd_index.strftime("%H:%M:%S"))
        label = "\n".join(values)
        return label


    fig, ax = plt.subplots(3, sharex=True, figsize=(7, 7))
    ax[0].step(h["time"], h["counts"], label="HILT", where="post")
    ax[1].step(p["time"], p.data["counts"], label="PET", where="post")
    ax[2].step(l["time"], l["Stop"], label="LICA-Stop", where="post")

    ax[0].set(ylabel="HILT")
    ax[1].set(ylabel="PET")
    ax[2].set(ylabel="LICA/Stop")
    ax[-1].set_xlabel("Time")

    x_labels = {"L": "L_Shell", "MLT": "MLT", "Geo Lat": "GEO_Lat", "Geo Lon": "GEO_Long"}
    ax[-1].xaxis.set_major_formatter(FuncFormatter(format_fn))
    ax[-1].set_xlabel("\n".join(["Time"] + list(x_labels.keys())))
    # ax[-1].xaxis.set_minor_locator(matplotlib.dates.SecondLocator())
    ax[-1].xaxis.set_label_coords(-0.1, -0.06)

    for ax_i in ax:
        ax_i.format_coord = lambda x, y: "{}, {}".format(
            matplotlib.dates.num2date(x).replace(tzinfo=None).isoformat(), round(y)
        )
        ax_i.set_yscale(args.yscale)

    plt.suptitle(f"SAMPEX | {day.date()}")
    plt.subplots_adjust(hspace=0.1, wspace=0.01, top=0.95, bottom=0.15, left=0.13, right=0.95)
    plt.show()
