#!/usr/bin/env python3

# Use the proper idiom in the main module ...
# NOTE: See https://docs.python.org/3.12/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
if __name__ == "__main__":
    # Import standard modules ...
    import glob
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
    if not os.path.exists("studyBalticConcentration/plots"):
        os.mkdir("studyBalticConcentration/plots")

    # **************************************************************************

    # Load trend CSV ...
    dates = []
    totals = []
    equivs = []
    labels_loc = []
    labels_txt = []
    with open("studyBalticConcentration/trends.csv", "rt", encoding = "utf-8") as fObj:
        for line in fObj:
            if line.startswith("date,"):
                continue
            yyyymmdd, total, equiv = line.strip().split(",")
            dates.append(yyyymmdd)
            yyyy, mm, dd = yyyymmdd.split("-")
            if int(mm) == 7 and int(dd) == 1:
                labels_loc.append(yyyymmdd)
                labels_txt.append(yyyy)
            totals.append(0.001 * float(total))                                 # [10^3 km2]
            equivs.append(0.001 * float(equiv))                                 # [10^3 km2]

    # **************************************************************************

    # Loop over dates ...
    for date, total, equiv in zip(dates, totals, equivs, strict = True):
        # Deduce plot name and skip if it already exists ...
        pName = f"studyBalticConcentration/plots/{date}.png"
        if os.path.exists(pName):
            continue

        print(f"Making \"{pName}\" ...")

        # Find histograms and maps ...
        cNames = sorted(glob.glob(f"studyBalticConcentration/histograms/{date}_??-??.csv"))
        pNames = sorted(glob.glob(f"studyBalticConcentration/maps/{date}_??-??.png"))

        # Skip this date if there isn't both a histogram and a map ...
        if len(cNames) == 0 or len(pNames) == 0:
            print(" > Skipping, no histogram/map.")
            continue

        # Load most up-to-date histogram for the day ...
        x, y = numpy.loadtxt(
            cNames[-1],
            delimiter = ",",
                dtype = numpy.float64,
             skiprows = 1,
               unpack = True,
        )                                                                       # [%], [km2]

        # Convert to useful units ...
        y *= 0.001                                                              # [10^3 km2]

        # Create figure ...
        fg = matplotlib.pyplot.figure(figsize = (4.1, 4.9))

        # Create axes ...
        ax = fg.subplots(2, 1)

        # Plot data ...
        ax[0].bar(
            dates,
            equivs,
            width = 1,
        )
        ax[0].bar(
            [date],
            [equiv],
            width = 10,
        )
        ax[1].bar(
            x,
            y,
            width = 1,
        )

        # Configure axis ...
        ax[0].grid()
        ax[0].set_xlim(dates[0], dates[-1])
        ax[0].set_xticks(
            labels_loc,
              labels = labels_txt,
                  ha = "right",
            rotation = 45,
        )
        ax[0].set_ylabel("100%-Concentration Equivalent\nSea Ice Area [10³ km²]")
        ax[0].set_ylim(0.0, 170.0)

        # Configure axis ...
        ax[1].grid()
        ax[1].set_xlabel("Concentration [%]")
        ax[1].set_xlim(0, 100)
        ax[1].set_ylabel("Sea Ice Area [10³ km²]")
        ax[1].set_ylim(0, 85)

        # Shade alternate years ...
        for yyyy in range(int(dates[0].split("-")[0]), int(dates[-1].split("-")[0]) + 1, 2):
            ax[0].axvspan(
                f"{yyyy}-01-01",
                f"{yyyy}-12-31",
                    alpha = 0.25,
                facecolor = "grey",
            )

        # Configure figure ...
        fg.tight_layout()

        # Save figure ...
        fg.savefig(pName)
        matplotlib.pyplot.close(fg)

        # Optimize PNG ...
        pyguymer3.image.optimise_image(
            pName,
            strip = True,
        )
