#!/usr/bin/env python3

# Import standard modules ...
import glob
import os

# Import special modules ...
try:
    import matplotlib
    matplotlib.use("Agg")                                                       # NOTE: https://matplotlib.org/gallery/user_interfaces/canvasagg.html
    import matplotlib.pyplot
except:
    raise Exception("\"matplotlib\" is not installed; run \"pip install --user matplotlib\"") from None
try:
    import numpy
except:
    raise Exception("\"numpy\" is not installed; run \"pip install --user numpy\"") from None
try:
    import PIL
    import PIL.Image
except:
    raise Exception("\"PIL\" is not installed; run \"pip install --user Pillow\"") from None
try:
    import scipy
    import scipy.io
except:
    raise Exception("\"scipy\" is not installed; run \"pip install --user scipy\"") from None

# Import my modules ...
try:
    import pyguymer3
except:
    raise Exception("\"pyguymer3\" is not installed; you need to have the Python module from https://github.com/Guymer/PyGuymer3 located somewhere in your $PYTHONPATH") from None

# Configure PIL to open images up to 1 GiP ...
PIL.Image.MAX_IMAGE_PIXELS = 1024 * 1024 * 1024                                 # [px]

# ******************************************************************************

# Define alphabet ...
alphabet = "1234567890-: "

# Define character spacing ...
sp = 11                                                                         # [px]

# Load alphabet ...
chars = numpy.array(PIL.Image.open("makeAlphabet.png").convert("RGB"))

# ******************************************************************************

# Create short-hand ...
cm = matplotlib.pyplot.get_cmap("jet")

# Make output directory ...
if not os.path.exists("studyBalticConcentration"):
    os.mkdir("studyBalticConcentration")

# Loop over NetCDF files ...
for fname in sorted(glob.glob("Copernicus/SEAICE_BAL_SEAICE_L4_NRT_OBSERVATIONS_011_004/FMI-BAL-SEAICE_CONC-L4-NRT-OBS/????/??/ice_conc_baltic_????????????.nc")):
    # Deduce image name and skip if it already exists ...
    stub = fname.split("_")[-1][:-3]
    iname = os.path.join("studyBalticConcentration", f"{stub[0:4]}-{stub[4:6]}-{stub[6:8]}_{stub[8:10]}-{stub[10:12]}.png")
    if os.path.exists(iname):
        continue

    print(f"Making \"{iname}\" ...")

    # Catch errors ...
    try:
        # Open NetCDF file ...
        with scipy.io.netcdf_file(fname, mode = "r") as fobj:
            # Extract the first layer from a copy of the dataset and scale it
            # from 0 to 1 ...
            lvl = 0.01 * fobj.variables["ice_concentration"].data.copy()[0, :, :].astype(numpy.float32)
    except:
        # Print warning and skip ...
        print(" > Error loading NetCDF.")
        continue

    # Make image ...
    img = numpy.zeros((lvl.shape[0], lvl.shape[1], 3), dtype = numpy.uint8)
    img[:, :, :] = 255
    for iy in range(lvl.shape[0]):
        for ix in range(lvl.shape[1]):
            if lvl[iy, ix] < 0.0:
                img[iy, ix, :] = 255
            else:
                r, g, b, a = cm(lvl[iy, ix])
                img[iy, ix, 0] = 255.0 * r
                img[iy, ix, 1] = 255.0 * g
                img[iy, ix, 2] = 255.0 * b

    # Clean up ...
    del lvl

    # Add date/time overlay ...
    for i, char in enumerate(f"{stub[0:4]}-{stub[4:6]}-{stub[6:8]} {stub[8:10]}:{stub[10:12]}"):
        # Find the location of this character in the alphabet ...
        idx = alphabet.index(char)

        # Overlay this character ...
        img[0:chars.shape[0], i * sp:(i + 1) * sp, :] = chars[:, idx * sp:(idx + 1) * sp, :]

    # Save image ...
    pyguymer3.save_array_as_PNG(img, iname, ftype_req = 0)
    pyguymer3.optimize_image(iname, strip = True)

    # Clean up ...
    del img
