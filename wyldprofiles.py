"""Generates WYLD-wide admin report pages derived from UPRF: all profiles,
recirculating profiles, and library-use profiles."""

import os
from datetime import date
from html_utils import page, table, lib_nav
from userprofile import HEADERS, _profile_row

WYLD_LIB = 'WYLD'


def _write_profiles_page(uprfs, heading, title, out_dir, locn_lookup, static_path, nav=''):
    os.makedirs(out_dir, exist_ok=True)
    today = date.today().strftime('%B %-d, %Y')

    rows = [_profile_row(u, locn_lookup) for u in sorted(uprfs, key=lambda u: u['name'])]
    body = f'<h2>{heading}</h2>\n{nav}{table(HEADERS, rows)}'
    html = page(title, body, today, static_path or '../static')

    with open(os.path.join(out_dir, 'wyld.html'), 'w') as f:
        f.write(html)


def generate(records, lookups, output_root, static_path=None):
    locn_lookup = lookups['locn']
    all_uprfs = records['UPRF']

    nav = lib_nav(WYLD_LIB, 'userprofile', lookups)
    _write_profiles_page(
        all_uprfs, 'All User Profiles', f'{WYLD_LIB} User Profiles',
        os.path.join(output_root, 'userprofile'), locn_lookup, static_path, nav)

    recirculating = [u for u in all_uprfs if u.get('recirculating') == 'Y']
    _write_profiles_page(
        recirculating, 'Recirculating User Profiles', 'Recirculating User Profiles',
        os.path.join(output_root, 'recircprofiles'), locn_lookup, static_path)

    library_use = [u for u in all_uprfs if u.get('increment_charge_counter') == '0']
    _write_profiles_page(
        library_use, 'Library Use User Profiles', 'Library Use User Profiles',
        os.path.join(output_root, 'libraryuseprofiles'), locn_lookup, static_path)
