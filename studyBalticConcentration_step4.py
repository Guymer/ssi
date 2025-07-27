#!/usr/bin/env python3

# Use the proper idiom in the main module ...
# NOTE: See https://docs.python.org/3.12/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
if __name__ == "__main__":
    # Import standard modules ...
    import glob
    import os
    import shutil

    # Import special modules ...
    try:
        import PIL
        import PIL.Image
        PIL.Image.MAX_IMAGE_PIXELS = 1024 * 1024 * 1024                         # [px]
    except:
        raise Exception("\"PIL\" is not installed; run \"pip install --user Pillow\"") from None

    # Import my modules ...
    try:
        import pyguymer3
        import pyguymer3.image
        import pyguymer3.media
    except:
        raise Exception("\"pyguymer3\" is not installed; run \"pip install --user PyGuymer3\"") from None

    # **************************************************************************

    # Make output directory ...
    if not os.path.exists("studyBalticConcentration"):
        os.mkdir("studyBalticConcentration")
    if not os.path.exists("studyBalticConcentration/frames"):
        os.mkdir("studyBalticConcentration/frames")

    # **************************************************************************

    # Loop over plots ...
    for pname in sorted(glob.glob("studyBalticConcentration/plots/????-??-??.png")):
        # Extract date ...
        date = os.path.basename(pname).removesuffix(".png")

        # Deduce frame name and skip if it already exists ...
        fname = f"studyBalticConcentration/frames/{date}.png"
        if os.path.exists(fname):
            continue

        print(f"Making \"{fname}\" ...")

        # Find maps ...
        inames = sorted(glob.glob(f"studyBalticConcentration/maps/{date}_??-??.png"))

        # Open image as RGB (even if it is paletted) ...
        with PIL.Image.open(inames[-1]) as iObj:
            im1 = iObj.convert("RGB")

        # Open image as RGB (even if it is paletted) ...
        with PIL.Image.open(pname) as iObj:
            im2 = iObj.convert("RGB")

        # Calculate width (ensuring that it is even) ...
        w = im1.width + im2.width + 30                                          # [px]
        if w % 2 == 1:
            w += 1                                                              # [px]

        # Calculate height (ensuring that it is even) ...
        h = max(im1.height, im2.height) + 20                                    # [px]
        if h % 2 == 1:
            h += 1                                                              # [px]

        # Create empty frame ...
        assert (w * h) <= PIL.Image.MAX_IMAGE_PIXELS, f"image size is larger than maximum number of pixels allowed in Pillow ({w:,d} px × {h:,d} px > {PIL.Image.MAX_IMAGE_PIXELS:,d} px)"
        im0 = PIL.Image.new("RGB", (w, h), (242, 242, 242))

        # Add the map and the plot ...
        im0.paste(im1, (10, 10 + ((im0.height - 20) - im1.height) // 2))
        im0.paste(im2, (20 + im1.width, 10 + ((im0.height - 20) - im2.height) // 2))

        # Save frame ...
        im0.save(fname)
        pyguymer3.image.optimise_image(fname, strip = True)

    # **************************************************************************

    # Find the frames ...
    frames = sorted(glob.glob("studyBalticConcentration/frames/????-??-??.png"))

    # **************************************************************************

    print("Making \"studyBalticConcentration/trends.mp4\" ...")

    # Save 25fps MP4 ...
    vname = pyguymer3.media.images2mp4(
        frames,
    )
    shutil.move(vname, "studyBalticConcentration/trends.mp4")

    # **************************************************************************

    print("Making \"studyBalticConcentration/trends.webp\" ...")

    # Save 25fps WEBP ...
    pyguymer3.media.images2webp(
        frames,
        "studyBalticConcentration/trends.webp",
    )

    # **************************************************************************

    # Set maximum sizes ...
    # NOTE: By inspection, the PNG frames are 2,484 px wide.
    maxSizes = [512, 1024, 2048]                                                # [px]

    # Loop over maximum sizes ...
    for maxSize in maxSizes:
        print(f"Making \"studyBalticConcentration/trends{maxSize:04d}px.mp4\" ...")

        # Save 25fps MP4 ...
        vname = pyguymer3.media.images2mp4(
            frames,
             screenWidth = maxSize,
            screenHeight = maxSize,
        )
        shutil.move(vname, f"studyBalticConcentration/trends{maxSize:04d}px.mp4")

        # **********************************************************************

        print(f"Making \"studyBalticConcentration/trends{maxSize:04d}px.webp\" ...")

        # Save 25fps WEBP ...
        pyguymer3.media.images2webp(
            frames,
            f"studyBalticConcentration/trends{maxSize:04d}px.webp",
             screenWidth = maxSize,
            screenHeight = maxSize,
        )
