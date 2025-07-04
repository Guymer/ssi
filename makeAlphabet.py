#!/usr/bin/env python3

# Use the proper idiom in the main module ...
# NOTE: See https://docs.python.org/3.12/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
if __name__ == "__main__":
    # Import standard modules ...
    import string

    # Import special modules ...
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

    # Define character spacing ...
    sp = 12                                                                     # [px]

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
    pyguymer3.image.optimise_image("makeAlphabet.png", strip = True)
