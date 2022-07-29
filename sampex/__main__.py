import sys
import pathlib
import configparser

import sampex

# Run the configuration script with
# python3 -m sampex [init, initialize, config, or configure]

here = pathlib.Path(__file__).parent.resolve()

if (len(sys.argv) > 1) and (sys.argv[1] in ["init", "initialize", "config", "configure"]):
    print("Running the configuration script.")
    s = (
        f"What is your sampex data directory? Press enter for the default "
        f"directory at ~/sampex/ folder will be created if it doesn't exist.\n"
    )
    data_dir = input(s)

    # If the user specified the directory, check that the directory already exists
    # and make that directory if it does not.
    if data_dir != "":
        if not pathlib.Path(data_dir).exists():
            pathlib.Path(data_dir).mkdir(parents=True)
            print(f"Made sampex data directory at {pathlib.Path(data_dir)}.")
        else:
            print(f"The sampex data directory at {pathlib.Path(data_dir)} already exists.")
    else:
        # If the user did not specify the directory, make one at ~/sampex/.
        data_dir = pathlib.Path.home() / "sampex"
        if not data_dir.exists():
            data_dir.mkdir(parents=True)
            print(f"sampex directory at {data_dir} created.")
        else:
            print(f"sampex directory at {data_dir} already exists.")

    # Create a configparser object and add the user configuration.
    config = configparser.ConfigParser()
    config["Paths"] = {"data_dir": data_dir}

    with open(here / "config.ini", "w") as f:
        config.write(f)

else:
    print(
        "This is a configuration script to set up config.ini file. The config "
        "file contains the top-level sampex data directory, ~/sampex/ by "
        "default. To configure this package, run python3 -m sampex config."
    )
