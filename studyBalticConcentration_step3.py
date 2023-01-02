#!/usr/bin/env python3

# Import standard modules ...
import glob
import os

# Import special modules ...
try:
    import matplotlib
    matplotlib.use("Agg")                                                       # NOTE: See https://matplotlib.org/stable/gallery/user_interfaces/canvasagg.html
    import matplotlib.pyplot
    matplotlib.pyplot.rcParams.update({"font.size" : 8})
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
    raise Exception("\"pyguymer3\" is not installed; you need to have the Python module from https://github.com/Guymer/PyGuymer3 located somewhere in your $PYTHONPATH") from None

# ******************************************************************************

# Make output directory ...
if not os.path.exists("studyBalticConcentration"):
    os.mkdir("studyBalticConcentration")
if not os.path.exists("studyBalticConcentration/plots"):
    os.mkdir("studyBalticConcentration/plots")

# ******************************************************************************

# Define month name abbreviations ...
months = {
    "03" : "Mar",
    "06" : "Jun",
    "09" : "Sep",
    "12" : "Dec",
}

# Load trend CSV ...
dates = []
totals = []
equivs = []
labels_loc = []
labels_txt = []
with open("studyBalticConcentration/trends.csv", "rt", encoding = "utf-8") as fobj:
    for line in fobj:
        if line.startswith("date,"):
            continue
        parts = line.strip().split(",")
        dates.append(parts[0])
        yyyy, mm, dd = parts[0].split("-")
        if int(mm) % 3 == 0 and int(dd) == 1:
            labels_loc.append(parts[0])
            labels_txt.append(f"{months[mm]}/{yyyy[2:]}")
        totals.append(0.001 * float(parts[1]))                                  # [10^3 km2]
        equivs.append(0.001 * float(parts[2]))                                  # [10^3 km2]

# ******************************************************************************

# Loop over dates ...
for date, total, equiv in zip(dates, totals, equivs):
    # Deduce plot name and skip if it already exists ...
    pname = f"studyBalticConcentration/plots/{date}.png"
    if os.path.exists(pname):
        continue

    print(f"Making \"{pname}\" ...")

    # Find histograms and maps ...
    hnames = sorted(glob.glob(f"studyBalticConcentration/histograms/{date}_??-??.csv"))
    inames = sorted(glob.glob(f"studyBalticConcentration/maps/{date}_??-??.png"))

    # Skip this date if there isn't both a histogram and a map ...
    if len(hnames) == 0 or len(inames) == 0:
        print(" > Skipping, no histogram/map.")
        continue

    # Load most up-to-date histogram for the day ...
    x, y = numpy.loadtxt(hnames[-1], delimiter = ",", dtype = numpy.int32, skiprows = 1, unpack = True) # [%], [km2]

    # Convert to useful units ...
    y = y.astype(numpy.float32) * 0.001                                         # [10^3 km2]

    # Create plot ...
    fg = matplotlib.pyplot.figure(figsize = (4, 5.7), dpi = 300)
    ax = fg.subplots(2, 1)

    # Plot data ...
    ax[0].bar(dates, equivs, width = 1)
    ax[0].bar([date], [equiv], width = 10)
    ax[1].bar(x, y, width = 1)

    # Configure plot ...
    ax[0].grid()
    ax[0].set_xlim(dates[0], dates[-1])
    # ax[0].set_xticks(                                                           # MatPlotLib ≥ 3.5.0
    #     labels_loc,                                                             # MatPlotLib ≥ 3.5.0
    #       labels = labels_txt,                                                  # MatPlotLib ≥ 3.5.0
    #           ha = "right",                                                     # MatPlotLib ≥ 3.5.0
    #     rotation = 45,                                                          # MatPlotLib ≥ 3.5.0
    # )                                                                           # MatPlotLib ≥ 3.5.0
    ax[0].set_xticks(labels_loc)                                                # MatPlotLib < 3.5.0
    ax[0].set_xticklabels(                                                      # MatPlotLib < 3.5.0
        labels_txt,                                                             # MatPlotLib < 3.5.0
              ha = "right",                                                     # MatPlotLib < 3.5.0
        rotation = 45,                                                          # MatPlotLib < 3.5.0
    )                                                                           # MatPlotLib < 3.5.0
    ax[0].set_ylabel("100%-Concentration Equivalent\nSea Ice Area [10³ km²]")
    ax[0].set_ylim(0.0, 170.0)
    ax[1].grid()
    ax[1].set_xlabel("Concentration [%]")
    ax[1].set_xlim(0, 100)
    ax[1].set_ylabel("Sea Ice Area [10³ km²]")
    ax[1].set_ylim(0, 85)

    # Save plot ...
    fg.savefig(pname, bbox_inches = "tight", dpi = 300, pad_inches = 0.1)
    matplotlib.pyplot.close(fg)
    pyguymer3.image.optimize_image(pname, strip = True)
