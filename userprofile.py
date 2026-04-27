"""Generates one user profile HTML page per library."""

import json
import os
from datetime import date
from html_utils import page, table, lib_nav

PREFIXES_FILE = os.path.join(os.path.dirname(__file__), 'uprf_library_prefixes.json')

HEADERS = [
    'NAME', 'DESCRIPTION', 'CARD LIFE', 'CHARGES LIMIT', 'HOLD LIMIT',
    'OVERDUE THRESHOLD', 'BILL THRESHOLD', 'USES LIB PRECEDENCE',
    'INCREMENT CHARGE COUNTER', 'LOCATION', 'ALLOW EDIT EXPIRE',
]

CARD_LIFE_UNITS = {
    '0': None,
    '1': 'weeks',
    '2': 'months',
    '3': 'years',
    '4': 'special date',
    '5': 'days',
}


def _load_prefixes():
    with open(PREFIXES_FILE) as f:
        return json.load(f)


def _card_life(life_type, life_value):
    unit = CARD_LIFE_UNITS.get(life_type)
    if unit is None:
        return 'No expire date'
    if unit == 'special date':
        return 'Special date'
    return f'{life_value} {unit}'


def _yesno(val):
    return 'Yes' if val not in ('0', '', None) else 'No'


def _profile_row(uprf, locn_lookup):
    location_code = uprf.get('location_code', '')
    location = locn_lookup.get(location_code, {}).get('name', location_code) if location_code else ''

    return [
        uprf.get('name', ''),
        uprf.get('description', ''),
        _card_life(uprf.get('card_life_type', '0'), uprf.get('card_life_value', '')),
        uprf.get('charges_limit', ''),
        uprf.get('hold_limit', ''),
        uprf.get('overdue_threshold', ''),
        uprf.get('bill_threshold', ''),
        _yesno(uprf.get('uses_lib_precedence', '0')),
        _yesno(uprf.get('increment_charge_counter', '0')),
        location,
        _yesno(uprf.get('allow_edit_expire', '0')),
    ]


def generate(records, lookups, output_root, static_path=None):
    out_dir = os.path.join(output_root, 'userprofile')
    os.makedirs(out_dir, exist_ok=True)

    today = date.today().strftime('%B %-d, %Y')
    prefixes = _load_prefixes()
    all_uprfs = records['UPRF']
    locn_lookup = lookups['locn']

    for libr in records['LIBR']:
        lib = libr['lib']
        lib_name = libr['name']
        prefix = prefixes.get(lib)

        if prefix is None:
            continue

        if prefix == 'all':
            relevant = all_uprfs
        else:
            relevant = [u for u in all_uprfs if u['name'].startswith(prefix)]

        if not relevant:
            continue

        rows = [_profile_row(u, locn_lookup) for u in relevant]
        heading = 'All User Profiles' if prefix == 'all' else f'User Profiles for {lib_name}'
        nav = lib_nav(lib, 'userprofile')
        body = f'<h2>{heading}</h2>\n{nav}\n{table(HEADERS, rows)}'
        html = page(f'{lib} User Profiles', body, today, static_path or '../static')

        with open(os.path.join(out_dir, f'{lib.lower()}.html'), 'w') as f:
            f.write(html)

    print(f"  userprofile: wrote pages to {out_dir}")
