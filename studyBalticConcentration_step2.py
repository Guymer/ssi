#!/usr/bin/env python3

# Import standard modules ...
import datetime
import glob
import os

# Import special modules ...
try:
    import numpy
except:
    raise Exception("\"numpy\" is not installed; run \"pip install --user numpy\"") from None
try:
    import scipy
    import scipy.io
except:
    raise Exception("\"scipy\" is not installed; run \"pip install --user scipy\"") from None

# ******************************************************************************

# Make output directory ...
if not os.path.exists("studyBalticConcentration"):
    os.mkdir("studyBalticConcentration")
if not os.path.exists("studyBalticConcentration/histograms"):
    os.mkdir("studyBalticConcentration/histograms")

# ******************************************************************************

# Loop over NetCDF files ...
for fname in sorted(glob.glob("Copernicus/SEAICE_BAL_SEAICE_L4_NRT_OBSERVATIONS_011_004/FMI-BAL-SEAICE_CONC-L4-NRT-OBS/????/??/ice_conc_baltic_????????????.nc")):
    # Deduce histogram name and skip if it already exists ...
    stub = fname.split("_")[-1][:-3]
    hname = f"studyBalticConcentration/histograms/{stub[0:4]}-{stub[4:6]}-{stub[6:8]}_{stub[8:10]}-{stub[10:12]}.csv"
    if os.path.exists(hname):
        continue

    print(f"Making \"{hname}\" ...")

    # Skip if there are errors ...
    try:
        # Open NetCDF file ...
        with scipy.io.netcdf_file(fname, mode = "r") as fobj:
            # Extract the first layer from a copy of the dataset ...
            lvl = fobj.variables["ice_concentration"].data.copy()[0, :, :].astype(numpy.int8)
    except:
        print(" > Skipping, error loading NetCDF.")
        continue

    # Skip if there isn't any sea ice ...
    if lvl.max() <= 0:
        # Clean up ...
        del lvl

        print(" > Skipping, no sea ice.")
        continue

    # Open CSV file ...
    with open(hname, "wt", encoding = "utf-8") as fobj:
        # Write header ...
        fobj.write("sea ice concentration [%],area [km2]\n")

        # Loop over concentrations ...
        for conc in range(101):
            # Write data ...
            # NOTE: This only works because the web site for the dataset states
            #       that the grid is 1km x 1km.
            fobj.write(f"{conc:d},{(lvl == conc).sum():d}\n")

    # Clean up ...
    del lvl

# ******************************************************************************

print("Summarising ...")

# Initialize maxima ...
max1 = 0                                                                        # [km2]
max2 = 0.0                                                                      # [km2]

# Loop over histograms ...
for hname in sorted(glob.glob("studyBalticConcentration/histograms/????-??-??_??-??.csv")):
    # Load histogram ...
    x, y = numpy.loadtxt(
        hname,
        delimiter = ",",
            dtype = numpy.int32,
         skiprows = 1,
           unpack = True,
    )                                                                           # [km2], [km2]

    # Update maxima ...
    max1 = max(max1, y[1:101].max())                                            # [km2]
    max2 = max(max2, 0.01 * numpy.dot(x[1:101], y[1:101]))                      # [km2]

# Print summary ...
print(f"The highest single non-zero occurrence is {max1} km2.")
print(f"The highest 100%-concentration equivalent occurrence is {max2} km2.")

# ******************************************************************************

print("Saving trends ...")

# Define the start of the dataset ...
stub = datetime.date(2018, 1, 1)

# Initialize totals ...
tots = {}

# Open CSV file ...
with open("studyBalticConcentration/trends.csv", "wt", encoding = "utf-8") as fobj:
    # Write header ...
    fobj.write("date,total sea ice area [km2],100%-concentration equivalent sea ice area [km2]\n")

    # Loop over all dates since the start of the dataset ...
    while stub <= datetime.date.today():
        # Initialize the totals and the year ...
        if stub.year not in tots:
            tots[stub.year] = 0.0                                               # [km2.day]

        # Find histograms ...
        hnames = sorted(glob.glob(f"studyBalticConcentration/histograms/{stub.isoformat()}_??-??.csv"))

        # Check what to do ...
        if len(hnames) == 0:
            # Write data ...
            fobj.write(f"{stub.isoformat()},{0:d},{0.0:e}\n")
        else:
            # Load most up-to-date histogram for the day ...
            x, y = numpy.loadtxt(
                hnames[-1],
                delimiter = ",",
                    dtype = numpy.int32,
                 skiprows = 1,
                   unpack = True,
            )                                                                   # [km2], [km2]

            # Increment total ...
            tots[stub.year] += 0.01 * numpy.dot(x[1:101], y[1:101])             # [km2.day]

            # Write data ...
            fobj.write(f"{stub.isoformat()},{y[1:101].sum():d},{0.01 * numpy.dot(x[1:101], y[1:101]):e}\n")

        # Increment date stub ...
        stub = stub + datetime.timedelta(days = 1)

# Loop over years ...
for year in sorted(tots.keys()):
    # Print total ...
    print(f"{year:d} = {tots[year]:,.1f} km².day")
