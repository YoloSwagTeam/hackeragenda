from .color import rgba, add_alpha

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
