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
except:
    raise Exception("\"pyguymer3\" is not installed; you need to have the Python module from https://github.com/Guymer/PyGuymer3 located somewhere in your $PYTHONPATH") from None

# Configure PIL to open images up to 1 GiP ...
PIL.Image.MAX_IMAGE_PIXELS = 1024 * 1024 * 1024                                 # [px]

# Define alphabet ...
alphabet = string.printable + "©"

# Define character spacing ...
sp = 11                                                                         # [px]

# Create empty white image and initialize the drawing and font objects ...
im = PIL.Image.new("RGB", (sp * len(alphabet), 20), (255, 255, 255))
dw = PIL.ImageDraw.Draw(im)
ft = PIL.ImageFont.truetype("SFNSMono.ttf", 16)

# Loop over characters in the alphabet ...
for i, char in enumerate(alphabet):
    # Draw character ...
    dw.text((i * 11, 0), char, (0, 0, 0), font = ft)

# Save image ...
im.save("makeAlphabet.png")
pyguymer3.optimize_image("makeAlphabet.png", strip = True)
