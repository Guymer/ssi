#!/usr/bin/env python3

# Import standard modules ...
import string

# Import special modules ...
try:
    import PIL
    import PIL.Image
    import PIL.ImageDraw
    import PIL.ImageFont
except:
    raise Exception("\"PIL\" is not installed; run \"pip install --user Pillow\"") from None

# Import my modules ...
try:
    import pyguymer3
    import pyguymer3.image
except:
    raise Exception("\"pyguymer3\" is not installed; you need to have the Python module from https://github.com/Guymer/PyGuymer3 located somewhere in your $PYTHONPATH") from None

# Configure PIL to open images up to 1 GiP ...
PIL.Image.MAX_IMAGE_PIXELS = 1024 * 1024 * 1024                                 # [px]

# Define character spacing ...
sp = 12                                                                         # [px]

# Create empty white image and initialize the drawing and font objects ...
im = PIL.Image.new("RGB", (sp * len(string.printable), 21), (255, 255, 255))
dw = PIL.ImageDraw.Draw(im)
ft = PIL.ImageFont.truetype("SFNSMono.ttf", 16)

# Loop over characters in the alphabet ...
for i, char in enumerate(string.printable):
    # Draw character ...
    dw.text((i * sp, 0), char, (0, 0, 0), font = ft)

# Save image ...
im.save("makeAlphabet.png")
pyguymer3.image.optimize_image("makeAlphabet.png", strip = True)
