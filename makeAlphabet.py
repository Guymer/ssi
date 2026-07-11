#!/usr/bin/env python3

# Use the proper idiom in the main module ...
# NOTE: See https://docs.python.org/3.13/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
if __name__ == "__main__":
    # Import standard modules ...
    import argparse
    import shutil
    import string

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
                "image.interpolation" : "none",                                 # NOTE: See https://matplotlib.org/stable/gallery/images_contours_and_fields/interpolation_methods.html
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
        import PIL
        import PIL.Image
        PIL.Image.MAX_IMAGE_PIXELS = 1024 * 1024 * 1024                         # [px]
        import PIL.ImageDraw
        import PIL.ImageFont
    except:
        raise Exception("\"PIL\" is not installed; run \"pip install --user Pillow\"") from None

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
            description = "Make an image of the ASCII characters which are considered printable by Python.",
        formatter_class = argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--chunksize",
        default = 1048576,
           help = "the size of the chunks of any files which are read in (in bytes)",
           type = int,
    )
    parser.add_argument(
        "--debug",
        action = "store_true",
          help = "print debug messages",
    )
    parser.add_argument(
        "--exiftool-path",
        default = shutil.which("exiftool"),
           dest = "exiftoolPath",
           help = "the path to the \"exiftool\" binary",
           type = str,
    )
    parser.add_argument(
        "--gifsicle-path",
        default = shutil.which("gifsicle"),
           dest = "gifsiclePath",
           help = "the path to the \"gifsicle\" binary",
           type = str,
    )
    parser.add_argument(
        "--jpegtran-path",
        default = shutil.which("jpegtran"),
           dest = "jpegtranPath",
           help = "the path to the \"jpegtran\" binary",
           type = str,
    )
    parser.add_argument(
        "--optipng-path",
        default = shutil.which("optipng"),
           dest = "optipngPath",
           help = "the path to the \"optipng\" binary",
           type = str,
    )
    parser.add_argument(
        "--timeout",
        default = 60.0,
           help = "the timeout for any requests/subprocess calls (in seconds)",
           type = float,
    )
    args = parser.parse_args()

    # **************************************************************************

    # Define the anti-aliasing, the character spacing, the image height and then
    # deduce the image width ...
    aa = 16                                                                     # [×]
    charSpacing = 12                                                            # [px]
    imgHeight = 21                                                              # [px]
    imgWidth = charSpacing * len(string.printable)                              # [px]

    print(f"The user has requested {imgWidth:d} px × {imgHeight:d} px.")

    print(f"The temporary image will be {aa * imgWidth:d} px × {aa * imgHeight:d} px.")

    # Create short-hands ...
    fontPath = matplotlib.font_manager.findfont("DejaVu Sans Mono")
    fontSize = 16                                                               # [px]
    font = PIL.ImageFont.truetype(fontPath, aa * fontSize)

    # **************************************************************************

    # Create empty white image and initialize the drawing object ...
    img = PIL.Image.new(
        "RGB",
        (aa * imgWidth, aa * imgHeight),
        (255, 255, 255),
    )
    draw = PIL.ImageDraw.Draw(img)

    # Loop over characters in the alphabet ...
    for pos, char in enumerate(string.printable):
        # Draw character ...
        draw.text(
            (pos * aa * charSpacing, 0),
            char,
            (0, 0, 0),
            font = font,
        )

    # Reduce the image down to the requested size ...
    img = img.reduce(aa)

    # Save image ...
    img.save("makeAlphabet.png")

    # Optimize PNG ...
    pyguymer3.image.optimise_image(
        "makeAlphabet.png",
           chunksize = args.chunksize,
               debug = args.debug,
        exiftoolPath = args.exiftoolPath,
        gifsiclePath = args.gifsiclePath,
        jpegtranPath = args.jpegtranPath,
         optipngPath = args.optipngPath,
               strip = True,
             timeout = args.timeout,
    )

    # **************************************************************************

    # Make a copy of the image as an array ...
    imgArr = numpy.array(img)

    # Loop over height ...
    for iy in range(imgHeight):
        if imgArr[iy, :, :].sum() == imgWidth * 3 * 255:
            print(f"Row {iy:2d} is empty.")
        else:
            print(f"Row {iy:2d} has characters.")
