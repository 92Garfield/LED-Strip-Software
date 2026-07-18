# Color helpers for NeoPixel/WS2812 strips.
# Identical to firmware/GEdge/glib/color.py.


def hsv_to_rgb(h, s=1.0, v=1.0):
    """Convert HSV to an (r, g, b) tuple of ints 0-255.

    h: hue in degrees, any value (wraps around 360)
    s: saturation 0.0 - 1.0
    v: value/brightness 0.0 - 1.0
    """
    h = h % 360.0
    c = v * s  # chroma
    x = c * (1.0 - abs((h / 60.0) % 2.0 - 1.0))
    m = v - c

    if h < 60:
        r, g, b = c, x, 0.0
    elif h < 120:
        r, g, b = x, c, 0.0
    elif h < 180:
        r, g, b = 0.0, c, x
    elif h < 240:
        r, g, b = 0.0, x, c
    elif h < 300:
        r, g, b = x, 0.0, c
    else:
        r, g, b = c, 0.0, x

    return (
        int((r + m) * 255 + 0.5),
        int((g + m) * 255 + 0.5),
        int((b + m) * 255 + 0.5),
    )
