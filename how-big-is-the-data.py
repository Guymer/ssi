#!/usr/bin/env python3

# Use the proper idiom in the main module ...
# NOTE: See https://docs.python.org/3.12/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
if __name__ == "__main__":
    # Import standard modules ...
    import argparse
    import glob
    import json
    import os

    # Import special modules ...
    try:
        import matplotlib
        matplotlib.rcParams.update(
            {
                       "axes.xmargin" : 0.01,
                       "axes.ymargin" : 0.01,
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
    try:
        import shapely
        import shapely.geometry
    except:
        raise Exception("\"shapely\" is not installed; run \"pip install --user Shapely\"") from None

    # Import my modules ...
    try:
        import pyguymer3
        import pyguymer3.geo
        import pyguymer3.image
    except:
        raise Exception("\"pyguymer3\" is not installed; run \"pip install --user PyGuymer3\"") from None

    # **************************************************************************

    # Create argument parser and parse the arguments ...
    parser = argparse.ArgumentParser(
           allow_abbrev = False,
            description = "A script to investigate the size of the data.",
        formatter_class = argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--debug",
        action = "store_true",
          help = "print debug messages",
    )
    parser.add_argument(
        "--eps",
        default = 1.0e-12,
           dest = "eps",
           help = "the tolerance of the Vincenty formula iterations",
           type = float,
    )
    parser.add_argument(
        "--level",
        default = 1,
           dest = "level",
           help = "the number of levels to split shapes into when calculating their area",
           type = int,
    )
    parser.add_argument(
        "--nIter",
        default = 1000000,
           dest = "nIter",
           help = "the maximum number of iterations (particularly the Vincenty formula)",
           type = int,
    )
    parser.add_argument(
        "--timeout",
        default = 60.0,
           help = "the timeout for any requests/subprocess calls (in seconds)",
           type = float,
    )
    args = parser.parse_args()

    # **************************************************************************

    # Load colour tables and create short-hand ...
    with open(f"{pyguymer3.__path__[0]}/data/json/colourTables.json", "rt", encoding = "utf-8") as fObj:
        colourTables = json.load(fObj)
    coolwarm = numpy.array(colourTables["coolwarm"]).astype(numpy.uint8)

    # **************************************************************************

    # Create short-hands ...
    bName = f'{__file__.removesuffix(".py")}_areas_level={args.level:d}.bin'
    nName = "ice_conc_baltic_202602021400.nc"
    pName1 = f'{__file__.removesuffix(".py")}_areas_level={args.level:d}.png'
    pName2 = f'{__file__.removesuffix(".py")}_areas.png'
    pName3 = f'{__file__.removesuffix(".py")}_points.png'

    # Open NetCDF file ...
    with scipy.io.netcdf_file(nName, mode = "r") as fObj:
        # Create short-hands ...
        lat = numpy.array(fObj.variables["lat"][:])                             # [°]
        lon = numpy.array(fObj.variables["lon"][:])                             # [°]
        conc = numpy.array(fObj.variables["ice_concentration"][:, :, :])        # [%]

    # Demonstrate how the data is arranged ...
    assert len(lat.shape) == 1
    assert len(lon.shape) == 1
    assert len(conc.shape) == 3
    assert conc.shape == (1, lat.size, lon.size)

    print("The axes are the same length as the data. This means that the longitude/latitude values are either:")
    print(" * The pixel centres *not* the pixel edges. The extent of the pixels can never be known.")
    print(" * The upper-left corners and it is left as an exercise to the reader to calculate the other three corners. The lower corners of the lowest row can never be known. The right corners of the rightmost column can never be known.")
    print("Neither of these possibilities are good - or, the documentation is a lie, and it is not grid-wise data but it is actually point-wise data.")
    print(f"The latitude values extend from {lat[0]:.6f} ° to {lat[-1]:.6f} °.")
    print(f"The longitude values extend from {lon[0]:.6f} ° to {lon[-1]:.6f} °.")

    # Create short-hands ...
    dLat = 0.000001                                                             # [°]
    dLon = 0.000001                                                             # [°]
    nomLat = 0.009                                                              # [°]
    nomLon = 0.018                                                              # [°]
    latDiff = numpy.abs(numpy.diff(lat))                                        # [°]
    lonDiff = numpy.abs(numpy.diff(lon))                                        # [°]
    latPerc = 100.0 * ((latDiff / nomLat) - 1.0)                                # [%]
    lonPerc = 100.0 * ((lonDiff / nomLon) - 1.0)                                # [%]

    print(f"The latitude heights vary from {latDiff.min():.6f} ° to {latDiff.max():.6f} °.")
    print(f"The longitude widths vary from {lonDiff.min():.6f} ° to {lonDiff.max():.6f} °.")

    print(f"The latitude percentage differences vary from {latPerc.min():+.4f} % to {latPerc.max():+.4f} %.")
    print(f"The longitude percentage differences vary from {lonPerc.min():+.4f} % to {lonPerc.max():+.4f} %.")

    # Check if the BIN file needs making ...
    if not os.path.exists(bName):
        # Calculate the area of each pixel assuming that the data is point-wise ...
        # NOTE: The progress string needs padding with extra spaces so that the
        #       line is fully overwritten when it inevitably gets shorter (as
        #       the remaining time gets shorter). Assume that the longest it
        #       will ever be is "???.???% (~??h ??m ??.?s still to go)" (which
        #       is 37 characters).
        print("Calculating the area of the pixels ...")
        areas = numpy.zeros(
            (lat.size - 1, lon.size - 1),
            dtype = numpy.float32,
        )                                                                       # [km2]
        start = pyguymer3.now()
        for iLat in range(lat.size - 1):
            for iLon in range(lon.size - 1):
                pixel = shapely.geometry.polygon.Polygon(
                    shapely.geometry.polygon.LinearRing(
                        [
                            (lon[iLon    ], lat[iLat    ]),
                            (lon[iLon    ], lat[iLat + 1]),
                            (lon[iLon + 1], lat[iLat + 1]),
                            (lon[iLon + 1], lat[iLat    ]),
                            (lon[iLon    ], lat[iLat    ]),
                        ]
                    )
                )
                areas[iLat, iLon] = pyguymer3.geo.area(
                    pixel,
                      eps = args.eps,
                    level = args.level,
                    nIter = args.nIter,
                ) / 1.0e6                                                       # [km2]
            fraction = float(iLat + 1) / float(lat.size - 1)
            durationSoFar = pyguymer3.now() - start
            totalDuration = durationSoFar / fraction
            remaining = (totalDuration - durationSoFar).total_seconds()         # [s]
            progress = f"{100.0 * fraction:.3f}% (~{pyguymer3.convert_seconds_to_pretty_time(remaining)} still to go)"
            print(f"  {progress:37s}", end = "\r")
        print()

        # Save BIN file ...
        areas.tofile(bName)
    else:
        # Load BIN file ...
        areas = numpy.fromfile(
            bName,
            dtype = numpy.float32,
        ).reshape(lat.size - 1, lon.size - 1)                                   # [km2]

    print(f"The areas vary from {areas.min():.6f} km² to {areas.max():.6f} km².")

    # Check if the PNG file needs making ...
    if not os.path.exists(pName1):
        # Make a NumPy array suitable for saving as a PNG (from 0.8 km2 to 1.2
        # km2) ...
        tmpArr = 255.0 * (areas.astype(numpy.float64) - 0.8) / 0.4
        numpy.place(tmpArr, tmpArr <   0.0,   0.0)
        numpy.place(tmpArr, tmpArr > 255.0, 255.0)
        tmpArr = tmpArr.astype(numpy.uint8)
        tmpArr = tmpArr.reshape(lat.size - 1, lon.size - 1, 1)

        # Save PNG ...
        tmpSrc = pyguymer3.image.makePng(
            tmpArr,
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
                palUint8 = coolwarm,
              strategies = None,
                  wbitss = [15,],
        )
        del tmpArr
        with open(pName1, "wb") as fObj:
            fObj.write(tmpSrc)
        del tmpSrc

    # Calculate histogram ...
    latHistX = numpy.linspace(nomLat - 15 * dLat, nomLat + 15 * dLat, num = 31) # [°]
    latHistY = numpy.zeros(latHistX.size, dtype = numpy.uint32)                 # [#]
    keys = numpy.floor((latDiff - latHistX[0]) / dLat).astype(numpy.uint32)
    for key in keys:
        latHistY[key] += 1                                                      # [#]
    del keys

    # Calculate histogram ...
    lonHistX = numpy.linspace(nomLon - 15 * dLon, nomLon + 15 * dLon, num = 31) # [°]
    lonHistY = numpy.zeros(lonHistX.size, dtype = numpy.uint32)                 # [#]
    keys = numpy.floor((lonDiff - lonHistX[0]) / dLon).astype(numpy.uint32)
    for key in keys:
        lonHistY[key] += 1                                                      # [#]
    del keys

    # **************************************************************************

    # Create figure ...
    fg = matplotlib.pyplot.figure(figsize = (9.6, 7.2))

    # Create axis ...
    ax = fg.add_subplot()

    # Create temporary arrays to hold the flattened indexes ...
    tmpArr1D = numpy.zeros(
        lat.size - 1,
        dtype = numpy.uint32,
    )
    tmpArr2D = numpy.zeros(
        (lat.size - 1, lon.size - 1),
        dtype = numpy.uint32,
    )
    for iLat in range(lat.size - 1):
        tmpArr1D[iLat] = iLat
        tmpArr2D[iLat, :] = iLat

    # Loop over generated binary files ...
    for bName in sorted(glob.glob(f'{__file__.removesuffix(".py")}_areas_level=?.bin')):
        # Create short-hands ...
        jName = f'{bName.removesuffix(".bin")}.json'
        label = bName.removesuffix(".bin").split("_")[-1]

        # Load BIN file ...
        areas = numpy.fromfile(
            bName,
            dtype = numpy.float32,
        ).reshape(lat.size - 1, lon.size - 1)                                   # [km2]

        # Fit a polynomial degree 2 to the data ...
        coef = numpy.polynomial.polynomial.Polynomial.fit(
            tmpArr2D.flatten(),
            areas.flatten(),
            2,
        ).convert().coef

        # Save polynomial degree 2 as a JSON (manually, because I really want to
        # specify the format/precision of the coefficients) ...
        with open(jName, "wt", encoding = "utf-8") as fObj:
            fObj.write("[\n")
            fObj.write(f"    {coef[0]:.15e},\n")
            fObj.write(f"    {coef[1]:.15e},\n")
            fObj.write(f"    {coef[2]:.15e}\n")
            fObj.write("]")

        print(f"  {label} : {coef[0]:.3e} + {coef[1]:.3e} x + {coef[2]:.3e} x²")

        # Plot data ...
        ax.scatter(
            tmpArr2D.flatten(),
            areas.flatten(),
             label = label,
            marker = ".",
        )
        ax.plot(
            tmpArr1D,
            coef[0] + coef[1] * tmpArr1D + coef[2] * tmpArr1D * tmpArr1D,
            label = f"{label} (fit)",
        )

    # Configure axis ...
    ax.grid()
    ax.legend(loc = "upper left")
    ax.set_xlabel("Latitude Index [#]")
    ax.set_xlim(0, latDiff.size - 2)
    ax.set_ylabel("Area [km²]")

    # Configure figure ...
    fg.tight_layout()

    # Save figure ...
    fg.savefig(pName2)
    matplotlib.pyplot.close(fg)

    # Optimize PNG ...
    pyguymer3.image.optimise_image(
        pName2,
          debug = args.debug,
           pool = None,
          strip = True,
        timeout = args.timeout,
    )

    # **************************************************************************

    # Create figure ...
    fg = matplotlib.pyplot.figure(figsize = (2 * 9.6, 2 * 7.2))

    # Create axes ...
    ax = fg.subplots(2, 2)

    # Plot data ...
    ax[0, 0].plot(
        range(latPerc.size),
        latPerc,
        color = "C0",
    )
    ax[0, 1].bar(
        latHistX,
        latHistY,
        color = "C0",
        width = dLat,
    )
    ax[0, 1].plot(
        [nomLat, nomLat],
        [0.0, latHistY.max()],
        color = "C1",
    )

    # Plot data ...
    ax[1, 0].plot(
        range(lonPerc.size),
        lonPerc,
        color = "C0",
    )
    ax[1, 1].bar(
        lonHistX,
        lonHistY,
        color = "C0",
        width = dLat,
    )
    ax[1, 1].plot(
        [nomLon, nomLon],
        [0.0, lonHistY.max()],
        color = "C1",
    )

    # Configure axis ...
    ax[0, 0].grid()
    ax[0, 0].set_xlabel("Latitude Index [#]")
    ax[0, 0].set_xlim(0, latDiff.size - 1)
    ax[0, 0].set_ylabel("Difference From Stated Value [%]")
    ax[0, 0].set_ylim(-0.12, +0.12)

    # Configure axis ...
    ax[0, 1].grid()
    ax[0, 1].set_xlabel("Latitude Height [°]")
    ax[0, 1].set_ylabel("Histogram [#]")
    ax[0, 1].set_ylim(0)

    # Configure axis ...
    ax[1, 0].grid()
    ax[1, 0].set_xlabel("Longitude Index [#]")
    ax[1, 0].set_xlim(0, lonDiff.size - 1)
    ax[1, 0].set_ylabel("Difference From Stated Value [%]")
    ax[1, 0].set_ylim(-0.12, +0.12)

    # Configure axis ...
    ax[1, 1].grid()
    ax[1, 1].set_xlabel("Longitude Width [°]")
    ax[1, 1].set_ylabel("Histogram [#]")
    ax[1, 1].set_ylim(0)

    # Configure figure ...
    fg.tight_layout()

    # Save figure ...
    fg.savefig(pName3)
    matplotlib.pyplot.close(fg)

    # Optimize PNG ...
    pyguymer3.image.optimise_image(
        pName3,
          debug = args.debug,
           pool = None,
          strip = True,
        timeout = args.timeout,
    )
