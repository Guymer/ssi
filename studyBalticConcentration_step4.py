#!/usr/bin/env python3

# Import standard modules ...
import glob
import os

# Import special modules ...
try:
    import PIL
    import PIL.Image
except:
    raise Exception("\"PIL\" is not installed; run \"pip install --user Pillow\"") from None

# Import my modules ...
try:
    import pyguymer3
except:
    raise Exception("\"pyguymer3\" is not installed; you need to have the Python module from https://github.com/Guymer/PyGuymer3 located somewhere in your $PYTHONPATH") from None

# Configure PIL to open images up to 1 GiP ...
PIL.Image.MAX_IMAGE_PIXELS = 1024 * 1024 * 1024                                 # [px]

# ******************************************************************************

# Make output directory ...
if not os.path.exists("studyBalticConcentration"):
    os.mkdir("studyBalticConcentration")
if not os.path.exists("studyBalticConcentration/frames"):
    os.mkdir("studyBalticConcentration/frames")

# ******************************************************************************

# Loop over plots ...
for pname in sorted(glob.glob("studyBalticConcentration/plots/????-??-??.png")):
    # Extract date ...
    date = os.path.splitext(os.path.basename(pname))[0]

    # Deduce frame name and skip if it already exists ...
    fname = f"studyBalticConcentration/frames/{date}.png"
    if os.path.exists(fname):
        continue

    print(f"Making \"{fname}\" ...")

    # Find maps ...
    inames = sorted(glob.glob(f"studyBalticConcentration/maps/{date}_??-??.png"))

    # Load images ...
    im1 = PIL.Image.open(inames[-1]).convert("RGB")
    im2 = PIL.Image.open(pname).convert("RGB")

    # Create empty frame ...
    im0 = PIL.Image.new("RGB", (im1.width + im2.width + 30, max(im1.height, im2.height) + 20), (242, 242, 242))

    # Add the map and the plot ...
    im0.paste(im1, (10, 10 + ((im0.height - 20) - im1.height) // 2))
    im0.paste(im2, (20 + im1.width, 10 + ((im0.height - 20) - im2.height) // 2))

    # Clean up ...
    im1.close()
    im2.close()
    del im1, im2

    # Save frame ...
    im0.save(fname)
    pyguymer3.optimize_image(fname, strip = True)

    # Clean up ...
    im0.close()
    del im0

# ******************************************************************************

print("Making \"studyBalticConcentration/trends.gif\" ...")

# Initialize list ...
images = []

# Loop over frames ...
for fname in sorted(glob.glob("studyBalticConcentration/frames/????-??-??.png")):
    # Append image to list ...
    images.append(PIL.Image.open(fname).convert("RGB"))

# Save 25fps GIF ...
images[0].save("studyBalticConcentration/trends.gif", save_all = True, append_images = images[1:], duration = 40, loop = 0)
pyguymer3.optimize_image("studyBalticConcentration/trends.gif", strip = True)

# Clean up ...
for image in images:
    image.close()
del images

# ******************************************************************************

# Set widths ...
# NOTE: By inspection, the PNG frames are 2412 wide.
widths = [512, 1024, 2048]                                                      # [px]

# Loop over widths ...
for width in widths:
    print("Making \"studyBalticConcentration/trends{:04d}px.gif\" ...".format(width))

    # Initialize list ...
    images = []

    # Loop over frames ...
    for fname in sorted(glob.glob("studyBalticConcentration/frames/????-??-??.png")):
        # Load image ...
        image = PIL.Image.open(fname).convert("RGB")

        # Calculate height ...
        ratio = float(image.width) / float(image.height)                        # [px/px]
        height = round(float(width) / ratio)                                    # [px]

        # Downscale the image and append it to the list ...
        images.append(image.resize((width, height), resample = PIL.Image.LANCZOS))

    # Save 25fps GIF ...
    images[0].save("studyBalticConcentration/trends{:04d}px.gif".format(width), save_all = True, append_images = images[1:], duration = 40, loop = 0)
    pyguymer3.optimize_image("studyBalticConcentration/trends{:04d}px.gif".format(width), strip = True)

    # Clean up ...
    for image in images:
        image.close()
    del images
