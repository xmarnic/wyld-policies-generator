"""Single source of truth for which policy pages exist per library.

Used both by libindex.py (hub page cards) and html_utils.py's lib_nav
(per-page subnav buttons), so the two stay in sync automatically.
"""

WYLD_LIBCODE = '115'

# (directory, title, condition) — condition(lib, libcode, lookups) -> bool
_CARDS = [
    ('Circmap',            'Circ Map',                lambda lib, libcode, lookups: True),
    ('Circrule',           'Circ Rules',               lambda lib, libcode, lookups: True),
    ('Holdmap',            'Hold Map',                 lambda lib, libcode, lookups: True),
    ('Holdcode',           'Holding Codes',            lambda lib, libcode, lookups:
        libcode == WYLD_LIBCODE or libcode in lookups.get('libs_with_holdcodes', set())),
    ('Defprice',           'Default Prices',           lambda lib, libcode, lookups: True),
    ('userprofile',        'User Profiles',            lambda lib, libcode, lookups:
        lib in lookups.get('libs_with_userprofile', set())),
    ('recircprofiles',     'Recirculating Profiles',   lambda lib, libcode, lookups: libcode == WYLD_LIBCODE),
    ('libraryuseprofiles', 'Library-Use Profiles',     lambda lib, libcode, lookups: libcode == WYLD_LIBCODE),
    ('itemtype',           'Item Types',               lambda lib, libcode, lookups: libcode == WYLD_LIBCODE),
    ('location',           'Item Locations',           lambda lib, libcode, lookups: libcode == WYLD_LIBCODE),
    ('itemcategory',       'Item Categories',          lambda lib, libcode, lookups: libcode == WYLD_LIBCODE),
    ('usercategory',       'User Categories',          lambda lib, libcode, lookups: libcode == WYLD_LIBCODE),
]


def available_cards(lib, libcode, lookups):
    """Return (directory, title) pairs applicable to this library, alphabetized by title."""
    lookups = lookups or {}
    cards = [(d, t) for d, t, condition in _CARDS if condition(lib, libcode, lookups)]
    return sorted(cards, key=lambda c: c[1])
