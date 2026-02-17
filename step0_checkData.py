#!/usr/bin/env python3

# Use the proper idiom in the main module ...
# NOTE: See https://docs.python.org/3.12/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
if __name__ == "__main__":
    # Import standard modules ...
    import argparse
    import copy
    import glob
    import os

    # Import special modules ...
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
    except:
        raise Exception("\"pyguymer3\" is not installed; run \"pip install --user PyGuymer3\"") from None

    # **************************************************************************

    # Create argument parser and parse the arguments ...
    parser = argparse.ArgumentParser(
           allow_abbrev = False,
            description = "Check Baltic sea ice data.",
        formatter_class = argparse.ArgumentDefaultsHelpFormatter,
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
    args = parser.parse_args()

    # **************************************************************************

    # Make output directory ...
    if not os.path.exists("studyBalticConcentration"):
        os.mkdir("studyBalticConcentration")

    # **************************************************************************

    # Check if the BIN file needs making ...
    if not os.path.exists("studyBalticConcentration/lat.bin"):
        # Create short-hand ...
        lat = None
    else:
        # Load BIN file ...
        lat = numpy.fromfile(
            "studyBalticConcentration/lat.bin",
            dtype = numpy.float32,
        )                                                                       # [°]

    # Check if the BIN file needs making ...
    if not os.path.exists("studyBalticConcentration/lon.bin"):
        # Create short-hand ...
        lon = None
    else:
        # Load BIN file ...
        lon = numpy.fromfile(
            "studyBalticConcentration/lon.bin",
            dtype = numpy.float32,
        )                                                                       # [°]

    # Loop over NetCDF files ...
    for nName in sorted(glob.glob("Copernicus/SEAICE_BAL_SEAICE_L4_NRT_OBSERVATIONS_011_004/FMI-BAL-SEAICE_CONC-L4-NRT-OBS/????/??/ice_conc_baltic_????????????.nc")):
        print(f"Checking \"{nName}\" ...")

        # Skip if there are errors ...
        try:
            # Open NetCDF file ...
            with scipy.io.netcdf_file(nName, mode = "r") as fObj:
                # Create short-hands ...
                tmpLat = numpy.array(fObj.variables["lat"][:]).astype(numpy.float32)    # [°]
                tmpLon = numpy.array(fObj.variables["lon"][:]).astype(numpy.float32)    # [°]
        except:
            print(" > Skipping, error loading NetCDF.")
            continue

        # Check if the short-hands have been populated ...
        if lat is None and lon is None:
            # Check if the BIN file needs making ...
            if not os.path.exists("studyBalticConcentration/lat.bin"):
                # Save BIN file ...
                tmpLat.tofile("studyBalticConcentration/lat.bin")

            # Check if the BIN file needs making ...
            if not os.path.exists("studyBalticConcentration/lon.bin"):
                # Save BIN file ...
                tmpLon.tofile("studyBalticConcentration/lon.bin")

            # Populate short-hands ...
            lat = copy.copy(tmpLat)                                             # [°]
            lon = copy.copy(tmpLon)                                             # [°]

            # Skip to the next NetCDF ...
            continue

        # Check values ...
        assert numpy.all(numpy.isclose(tmpLat, lat))
        assert numpy.all(numpy.isclose(tmpLon, lon))

        break

    # **************************************************************************

    # Check if the BIN file needs making ...
    if not os.path.exists("studyBalticConcentration/areas.bin"):
        print("Calculating the area of the pixels ...")

        # Calculate the area of each pixel assuming that the data is point-wise ...
        # NOTE: The progress string needs padding with extra spaces so that the
        #       line is fully overwritten when it inevitably gets shorter (as
        #       the remaining time gets shorter). Assume that the longest it
        #       will ever be is "???.???% (~??h ??m ??.?s still to go)" (which
        #       is 37 characters).
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
        areas.tofile("studyBalticConcentration/areas.bin")
    else:
        # Load BIN file ...
        areas = numpy.fromfile(
            "studyBalticConcentration/areas.bin",
            dtype = numpy.float32,
        ).reshape(lat.size - 1, lon.size - 1)                                   # [km2]

    print(f"The areas vary from {areas.min():.6f} km² to {areas.max():.6f} km².")

    # **************************************************************************

    # Create temporary array to hold the flattened latitudes ...
    tmpArr = numpy.zeros(
        (lat.size - 1, lon.size - 1),
        dtype = numpy.float32,
    )
    for iLat in range(lat.size - 1):
        tmpArr[iLat, :] = 0.5 * (lat[iLat] + lat[iLat + 1])                     # [°]

    # Fit a polynomial degree 2 to the areas as a function of latitude ...
    coef = numpy.polynomial.polynomial.Polynomial.fit(
        tmpArr.flatten(),
        areas.flatten(),
        2,
    ).convert().coef                                                            # [km2], [km2/°], [km2/°2]
    del tmpArr

    # Save polynomial degree 2 as a JSON (manually, because I really want to
    # specify the format/precision of the coefficients) ...
    with open("studyBalticConcentration/areaCoef.json", "wt", encoding = "utf-8") as fObj:
        fObj.write("[\n")
        fObj.write(f"    {coef[0]:.15e},\n")
        fObj.write(f"    {coef[1]:.15e},\n")
        fObj.write(f"    {coef[2]:.15e}\n")
        fObj.write("]")
