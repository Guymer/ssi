#!/usr/bin/env python3

# Use the proper idiom in the main module ...
# NOTE: See https://docs.python.org/3.12/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
if __name__ == "__main__":
    # Import standard modules ...
    import datetime
    import glob
    import json
    import os

    # Import special modules ...
    try:
        import matplotlib
        matplotlib.rcParams.update(
            {
                            "backend" : "Agg",                                  # NOTE: See https://matplotlib.org/stable/gallery/user_interfaces/canvasagg.html
                         "figure.dpi" : 300,
                     "figure.figsize" : (9.6, 7.2),                             # NOTE: See https://github.com/Guymer/misc/blob/main/README.md#matplotlib-figure-sizes
                          "font.size" : 8,
                "image.interpolation" : "none",
                     "image.resample" : False,
            }
        )
        import matplotlib.pyplot
    except:
        raise Exception("\"matplotlib\" is not installed; run \"pip install --user matplotlib\"") from None
    try:
        import numpy
    except:
        raise Exception("\"numpy\" is not installed; run \"pip install --user numpy\"") from None
    try:
        import scipy
    except:
        raise Exception("\"scipy\" is not installed; run \"pip install --user scipy\"") from None

    # Import my modules ...
    try:
        import pyguymer3
        import pyguymer3.image
    except:
        raise Exception("\"pyguymer3\" is not installed; run \"pip install --user PyGuymer3\"") from None

    # **************************************************************************

    # Make output directory ...
    if not os.path.exists("studyBalticConcentration"):
        os.mkdir("studyBalticConcentration")
    if not os.path.exists("studyBalticConcentration/histograms"):
        os.mkdir("studyBalticConcentration/histograms")

    # Load BIN files ...
    lat = numpy.fromfile(
        "studyBalticConcentration/lat.bin",
        dtype = numpy.float32,
    )                                                                           # [°]
    lon = numpy.fromfile(
        "studyBalticConcentration/lon.bin",
        dtype = numpy.float32,
    )                                                                           # [°]

    # Load area coefficients ...
    with open("studyBalticConcentration/areaCoef.json", "rt", encoding = "utf-8") as fObj:
        coef = json.load(fObj)                                                  # [km2], [km2/°], [km2/°2]

    # Calculate the area as a function of latitude ...
    lat2area = numpy.zeros(
        lat.size,
        dtype = numpy.float64,
    )                                                                           # [km2]
    for iLat in range(lat.size):
        lat2area[iLat] = coef[0] + coef[1] * lat[iLat] + coef[2] * lat[iLat] * lat[iLat]    # [km2]

    # **************************************************************************

    # Loop over NetCDF files ...
    for fname in sorted(glob.glob("Copernicus/SEAICE_BAL_SEAICE_L4_NRT_OBSERVATIONS_011_004/FMI-BAL-SEAICE_CONC-L4-NRT-OBS/????/??/ice_conc_baltic_????????????.nc")):
        # Deduce histogram name and skip if it already exists ...
        stub = fname.split("_")[-1].removesuffix(".nc")
        hname = f"studyBalticConcentration/histograms/{stub[0:4]}-{stub[4:6]}-{stub[6:8]}_{stub[8:10]}-{stub[10:12]}.csv"
        if os.path.exists(hname):
            continue

        print(f"Making \"{hname}\" ...")

        # Skip if there are errors ...
        try:
            # Open NetCDF file ...
            with scipy.io.netcdf_file(fname, mode = "r") as fObj:
                # Extract the first layer ...
                lvl = numpy.array(fObj.variables["ice_concentration"][0, :, :]).astype(numpy.int8)  # [%]
        except:
            print(" > Skipping, error loading NetCDF.")
            continue

        # Skip if there isn't any sea ice ...
        if lvl.max() <= 0:
            print(" > Skipping, no sea ice.")
            continue

        # Open CSV file ...
        with open(hname, "wt", encoding = "utf-8") as fObj:
            # Write header ...
            fObj.write("sea ice concentration [%],area [km²]\n")

            # Loop over concentrations ...
            for conc in range(101):
                # Calculate the total area which has this concentration ...
                totArea = 0.0                                                   # [km2]
                for iLat in range(lat.size):
                    totArea += lat2area[iLat] * (lvl[iLat, :] == conc).sum()    # [km2]

                # Write data ...
                fObj.write(f"{conc:d},{totArea:.15e}\n")

    # **************************************************************************

    print("Summarising ...")

    # Initialize maxima ...
    max1 = 0.0                                                                  # [km2]
    max2 = 0.0                                                                  # [km2]

    # Loop over histograms ...
    for hname in sorted(glob.glob("studyBalticConcentration/histograms/????-??-??_??-??.csv")):
        # Load histogram ...
        x, y = numpy.loadtxt(
            hname,
            delimiter = ",",
                dtype = numpy.float64,
             skiprows = 1,
               unpack = True,
        )                                                                       # [%], [km2]

        # Update maxima ...
        max1 = max(max1, y[1:101].max())                                        # [km2]
        max2 = max(max2, 0.01 * numpy.dot(x[1:101], y[1:101]))                  # [km2]

    # Print summary ...
    print(f"The highest single non-zero occurrence is {max1:,.1f} km².")
    print(f"The highest 100%-concentration equivalent occurrence is {max2:,.1f} km².")

    # **************************************************************************

    print("Saving trends ...")

    # Define the start of the dataset ...
    stub = datetime.date(2018, 1, 1)

    # Initialize totals ...
    tots = {}

    # Open CSV file ...
    with open("studyBalticConcentration/trends.csv", "wt", encoding = "utf-8") as fObj:
        # Write header ...
        fObj.write("date,total sea ice area [km²],100%-concentration equivalent sea ice area [km²]\n")

        # Loop over all dates since the start of the dataset ...
        while stub <= datetime.date.today():
            # Deduce key for the totals ...
            # NOTE: If the date is after the summer solstice then it is part of
            #       next year's winter.
            if stub < datetime.date(stub.year, 6, 21):
                key = stub.year
            else:
                key = stub.year + 1

            # Initialize the total for the year ...
            if key not in tots:
                tots[key] = 0.0                                                 # [km2.day]

            # Find histograms ...
            hnames = sorted(glob.glob(f"studyBalticConcentration/histograms/{stub.isoformat()}_??-??.csv"))

            # Check what to do ...
            if len(hnames) == 0:
                # Write data ...
                fObj.write(f"{stub.isoformat()},{0:d},{0.0:e}\n")
            else:
                # Load most up-to-date histogram for the day ...
                x, y = numpy.loadtxt(
                    hnames[-1],
                    delimiter = ",",
                        dtype = numpy.float64,
                     skiprows = 1,
                       unpack = True,
                )                                                               # [%], [km2]

                # Increment total ...
                tots[key] += 0.01 * numpy.dot(x[1:101], y[1:101])               # [km2.day]

                # Write data ...
                fObj.write(f"{stub.isoformat()},{y[1:101].sum():.15e},{0.01 * numpy.dot(x[1:101], y[1:101]):.15e}\n")

            # Increment date stub ...
            stub = stub + datetime.timedelta(days = 1)

    # Initialize lists ...
    x = []
    y = []                                                                      # [km2.day]

    # Loop over years ...
    for year in sorted(tots.keys()):
        # Append values to lists ...
        x.append(year)
        y.append(tots[year])                                                    # [km2.day]

        # Print total ...
        print(f"{year:d} = {tots[year]:,.1f} km².day")

    # Convert lists to arrays ...
    x = numpy.array(x)
    y = numpy.array(y)                                                          # [km2.day]

    # **************************************************************************

    # Create figure ...
    fg = matplotlib.pyplot.figure()

    # Create axis ...
    ax = fg.add_subplot()

    # Plot data ...
    ax.plot(
        x,
        y,
        marker = "d",
    )

    # Fit a straight line to the data ...
    assert x.size == y.size
    n = x.size
    xbar = x.sum() / n
    ybar = y.sum() / n
    top = 0.0
    bot = 0.0
    for i in range(n):
        top += (x[i] - xbar) * y[i]
        bot += pow(x[i] - xbar, 2)
    m = top / bot
    c = ybar - m * xbar

    # Plot data ...
    ax.plot(
        x,
        m * x + c,
    )

    # Configure axis ...
    ax.grid()
    ax.set_xlabel("Year")
    ax.set_ylabel("Total 100%-Concentration Equivalent Sea Ice [km².day]")
    ax.set_ylim(0.0)

    # Configure figure ...
    fg.tight_layout()

    # Save figure ...
    fg.savefig("studyBalticConcentration/tots.png")
    matplotlib.pyplot.close(fg)

    # Optimize PNG ...
    pyguymer3.image.optimise_image(
        "studyBalticConcentration/tots.png",
        strip = True,
    )
