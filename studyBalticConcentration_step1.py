#!/usr/bin/env python3

# Use the proper idiom in the main module ...
# NOTE: See https://docs.python.org/3.12/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
if __name__ == "__main__":
    # Import standard modules ...
    import argparse
    import glob
    import json
    import os
    import string

    # Import special modules ...
    try:
        import matplotlib
        matplotlib.rcParams.update(
            {
                       "backend" : "Agg",                                       # NOTE: See https://matplotlib.org/stable/gallery/user_interfaces/canvasagg.html
                    "figure.dpi" : 300,
                "figure.figsize" : (9.6, 7.2),                                  # NOTE: See https://github.com/Guymer/misc/blob/main/README.md#matplotlib-figure-sizes
                     "font.size" : 8,
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
        import PIL
        import PIL.Image
        PIL.Image.MAX_IMAGE_PIXELS = 1024 * 1024 * 1024                         # [px]
    except:
        raise Exception("\"PIL\" is not installed; run \"pip install --user Pillow\"") from None
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

    # Create argument parser and parse the arguments ...
    parser = argparse.ArgumentParser(
           allow_abbrev = False,
            description = "Make maps of Baltic sea ice.",
        formatter_class = argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--debug",
        action = "store_true",
          help = "print debug messages",
    )
    args = parser.parse_args()

    # **************************************************************************

    # Define character spacing ...
    sp = 12                                                                     # [px]

    # Open image as RGB (even if it is paletted) and convert it to a NumPy array ...
    with PIL.Image.open("makeAlphabet.png") as iObj:
        charsImg = iObj.convert("RGB")
    charsArr = numpy.array(charsImg)
    del charsImg

    # Load colour tables and create short-hand ...
    with open(f"{pyguymer3.__path__[0]}/data/json/colourTables.json", "rt", encoding = "utf-8") as fObj:
        colourTables = json.load(fObj)
    turbo = numpy.array(colourTables["turbo"]).astype(numpy.uint8)

    # **************************************************************************

    # Make output directory ...
    if not os.path.exists("studyBalticConcentration"):
        os.mkdir("studyBalticConcentration")
    if not os.path.exists("studyBalticConcentration/maps"):
        os.mkdir("studyBalticConcentration/maps")

    # **************************************************************************

    # Loop over NetCDF files ...
    for fname in sorted(glob.glob("Copernicus/SEAICE_BAL_SEAICE_L4_NRT_OBSERVATIONS_011_004/FMI-BAL-SEAICE_CONC-L4-NRT-OBS/????/??/ice_conc_baltic_????????????.nc")):
        # Deduce image name and skip if it already exists ...
        stub = fname.split("_")[-1].removesuffix(".nc")
        iname = f"studyBalticConcentration/maps/{stub[0:4]}-{stub[4:6]}-{stub[6:8]}_{stub[8:10]}-{stub[10:12]}.png"
        if os.path.exists(iname):
            continue

        print(f"Making \"{iname}\" ...")

        # Skip if there are errors ...
        try:
            # Open NetCDF file ...
            with scipy.io.netcdf_file(fname, mode = "r") as fObj:
                # Extract the first layer from the dataset ...
                lvl = fObj.variables["ice_concentration"].data[0, :, :].astype(numpy.float32)
        except:
            print(" > Skipping, error loading NetCDF.")
            continue

        # Skip if there isn't any sea ice ...
        if lvl.max() <= 0.0:
            print(" > Skipping, no sea ice.")
            continue

        # Find the pixels which are land ...
        isLand = numpy.transpose(numpy.where(lvl < 0.0))

        # Scale data from 0 to 255, mapping it from 0 % to 100 % ...
        lvl = 255.0 * (lvl / 100.0)
        numpy.place(lvl, lvl <   0.0,   0.0)
        numpy.place(lvl, lvl > 255.0, 255.0)
        lvl = lvl.astype(numpy.uint8)

        # Make image ...
        # NOTE: If I just wanted to make an image of the Baltic sea ice then I
        #       could skip this step and just make a paletted image. However, as
        #       I also want to use the colour white (for land) and the colour
        #       black (for overlaid text) then there would be more than 256
        #       colours in the palette. Therefore, it must be an RGB image.
        img = numpy.zeros(
            (lvl.shape[0], lvl.shape[1], 3),
            dtype = numpy.uint8,
        )
        for iy in range(lvl.shape[0]):
            for ix in range(lvl.shape[1]):
                img[iy, ix, :] = turbo[lvl[iy, ix], :]
        del lvl
        for i in range(isLand.shape[0]):
            img[isLand[i, 0], isLand[i, 1], :] = 255
        del isLand

        # Declare overlays ...
        overlays = [
            "Baltic Sea - Sea Ice Concentration",
            "Credits: E.U. Copernicus Marine Service Information",
            "",
            f"{stub[0:4]}-{stub[4:6]}-{stub[6:8]} {stub[8:10]}:{stub[10:12]}",
        ]

        # Loop over overlays ...
        for i, overlay in enumerate(overlays):
            # Loop over characters in overlay ...
            for j, char in enumerate(overlay):
                # Find the location of this character in the alphabet ...
                idx = string.printable.index(char)

                # Overlay this character ...
                iy = 1 + i * charsArr.shape[0]                                  # [px]
                ix = 1 + j * sp                                                 # [px]
                img[iy:iy + charsArr.shape[0], ix:ix + sp, :] = charsArr[:, idx * sp:(idx + 1) * sp, :]

        # Make PNG ...
        src = pyguymer3.image.makePng(
            img,
            calcAdaptive = True,
             calcAverage = True,
                calcNone = True,
               calcPaeth = True,
                 calcSub = True,
                  calcUp = True,
                 choices = "all",
                   debug = args.debug,
                     dpi = None,
                  levels = [9,],
               memLevels = [9,],
                 modTime = None,
                palUint8 = None,
              strategies = None,
                  wbitss = [15,],
        )
        with open(iname, "wb") as fObj:
            fObj.write(src)
        del img
