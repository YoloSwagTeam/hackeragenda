colors_lookup = {
    "black": (0, 0, 0),
    "white": (1, 1, 1),
    "red": (1, 0, 0),
    "green": (0, 1, 0),
    "blue": (0, 0, 1),
    "coral": (1, 0.5, 0.314),
    "darkblue": (0, 0, 0.545),
    "darkgoldenrod": (0.722, 0.525, 0.043),
    "pink": (1, 0.753, 0.796),
    "indigo": (0.294, 0.0, 0.510),
    "purple": (0.128, 0.0, 0.128),
    "darkorchid": (0.6, 0.196, 0.8),
}


def format_rgba_for_css(r, g, b, a):
    return "rgba(%d,%d,%d,%s)" % (255 * r, 255 * g, 255 * b, str(a))


def add_alpha(color, a=1):
    assert type(color) in (bytes, str), "%s (%s) should be a string" % (
        color,
        type(color),
    )
    if color[0] == "#":
        if len(color[1:]) == 3:
            r, g, b = tuple(int(x, 16) / 15.0 for x in color[1:])
        elif len(color[1:]) == 6:
            r, g, b = tuple(int(color[i : i + 2], 16) / 255.0 for i in [1, 3, 5])
        else:
            r, g, b = tuple(
                int(color.rjust(6, "0")[i : i + 2], 16) / 255.0 for i in [1, 3, 5]
            )
    else:
        r, g, b = colors_lookup[color.lower()]
    return format_rgba_for_css(r, g, b, a)
