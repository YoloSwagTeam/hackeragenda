colors_lookup = {
    "black": (0, 0, 0), "white": (1, 1, 1),
    "red": (1, 0, 0), "green": (0, 1, 0), "blue": (0, 0, 1),
    "coral": (1, .5, .314), "darkblue": (0, 0, .545),
    "darkgoldenrod": (.722, .525, .043), "pink": (1, .753, .796),
    "darkorchid": (.6, .196, .8)
}

def rgba(r, g, b, a):
    return 'rgba(%d,%d,%d,%s)'%(255*r, 255*g, 255*b, str(a))

def add_alpha(color, a=1):
    assert type(color) in (unicode, str)
    if color[0] == "#":
        if len(color) == 4:
            r, g, b = tuple(int(x, 16)/15. for x in color[1:])
        elif len(color) == 7:
            r, g, b = tuple(int(color[i:i+2], 16)/255. for i in range(1, 7, 2))
    else:
        r, g, b = colors_lookup[color.lower()]
    return rgba(r, g, b, a)

def test_rgba():
    assert rgba(1, 1, 1, 1) == "rgba(255,255,255,1)"
    assert rgba(0.342125, 0.5, 1, 0) == "rgba(87,127,255,0)"

def test_from_hex():
    assert add_alpha("#30f") == rgba(0.2, 0, 1, 1)
    assert add_alpha("#3300ff") == rgba(0.2, 0, 1, 1)

def test_from_name():
    assert add_alpha("black") == rgba(0, 0, 0, 1)
    assert add_alpha("white") == rgba(1, 1, 1, 1)
    assert add_alpha("red") == rgba(1, 0, 0, 1)
    assert add_alpha("green") == rgba(0, 1, 0, 1)
    assert add_alpha("blue") == rgba(0, 0, 1, 1)

def test_all_organisations():
    from .management.commands.fetch_events import load_agendas, SOURCES_OPTIONS
    load_agendas()

    for name, options in SOURCES_OPTIONS.iteritems():
        # Should raise if color not found
        bg = add_alpha(options['bg'])
        fg = add_alpha(options['fg'])
