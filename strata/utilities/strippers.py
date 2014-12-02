from strata.utilities import chars as __chars__


def filter(txt, *characters):
    assert txt, "The txt parameter is empty."
    assert len(characters) > 0, "The characters parameter is empty."
    buffer = []
    for c in characters:
        buffer.append(c)
    characters = "".join(buffer)
    table = __chars__.trans_table()
    try:
        return txt.translate(table, characters)
    except:
        return str(txt).translate(table, characters)

