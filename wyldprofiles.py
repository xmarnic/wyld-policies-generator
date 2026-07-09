"""Generates WYLD-wide admin report pages for record types that aren't
library-scoped: UPRF-derived profile reports (all profiles, recirculating
profiles, library-use profiles), and reference policy reports (item types,
locations, item categories, user categories)."""

import os
import re
from datetime import date
from html_utils import page, table, lib_nav
from userprofile import HEADERS, _profile_row

WYLD_LIB = 'WYLD'
WYLD_LIBCODE = '115'

REF_HEADERS = ['SHORT-CODE', 'DESCRIPTION']
LOCN_HEADERS = REF_HEADERS + ['AVAILABLE', 'HOLDABLE', 'SHADOWED']

_MSG_TOKEN_RE = re.compile(r'^\$<.*>$')


def _clean_description(description):
    """Blank out unresolved Symphony message-catalog tokens like $<LOCN_desc_checkedout>."""
    return '' if _MSG_TOKEN_RE.match(description) else description


def _yesno(flag):
    return 'Yes' if flag == '1' else 'No'


def _write_profiles_page(uprfs, heading, title, out_dir, locn_lookup, static_path, nav=''):
    os.makedirs(out_dir, exist_ok=True)
    today = date.today().strftime('%B %-d, %Y')

    rows = [_profile_row(u, locn_lookup) for u in sorted(uprfs, key=lambda u: u['name'])]
    body = f'<h2>{heading}</h2>\n{nav}{table(HEADERS, rows)}'
    html = page(title, body, today, static_path or '../static')

    with open(os.path.join(out_dir, 'wyld.html'), 'w') as f:
        f.write(html)


def _write_flat_report(rows, heading, title, out_dir, static_path, nav='', headers=REF_HEADERS):
    os.makedirs(out_dir, exist_ok=True)
    today = date.today().strftime('%B %-d, %Y')

    body = f'<h2>{heading}</h2>\n{nav}{table(headers, rows)}'
    html = page(title, body, today, static_path or '../static')

    with open(os.path.join(out_dir, 'wyld.html'), 'w') as f:
        f.write(html)


def _write_sectioned_report(records_by_number, label, heading, title, out_dir, static_path, nav=''):
    os.makedirs(out_dir, exist_ok=True)
    today = date.today().strftime('%B %-d, %Y')

    sections = ''
    for n in sorted(records_by_number):
        recs = records_by_number[n]
        if not recs:
            continue
        rows = [[r['name'], _clean_description(r['description'])] for r in sorted(recs, key=lambda r: r['name'])]
        sections += f'<h3>{label} {n}</h3>\n{table(REF_HEADERS, rows)}\n'

    body = f'<h2>{heading}</h2>\n{nav}{sections}'
    html = page(title, body, today, static_path or '../static')

    with open(os.path.join(out_dir, 'wyld.html'), 'w') as f:
        f.write(html)


def generate(records, lookups, output_root, static_path=None):
    locn_lookup = lookups['locn']
    all_uprfs = records['UPRF']

    _write_profiles_page(
        all_uprfs, 'All User Profiles', f'{WYLD_LIB} User Profiles',
        os.path.join(output_root, 'userprofile'), locn_lookup, static_path,
        lib_nav(WYLD_LIB, WYLD_LIBCODE, 'userprofile', lookups))

    recirculating = [u for u in all_uprfs if u.get('recirculating') == 'Y']
    _write_profiles_page(
        recirculating, 'Recirculating User Profiles', 'Recirculating User Profiles',
        os.path.join(output_root, 'recircprofiles'), locn_lookup, static_path,
        lib_nav(WYLD_LIB, WYLD_LIBCODE, 'recircprofiles', lookups))

    library_use = [u for u in all_uprfs if u.get('increment_charge_counter') == '0']
    _write_profiles_page(
        library_use, 'Library-Use User Profiles', 'Library-Use User Profiles',
        os.path.join(output_root, 'libraryuseprofiles'), locn_lookup, static_path,
        lib_nav(WYLD_LIB, WYLD_LIBCODE, 'libraryuseprofiles', lookups))

    ityp_rows = [[r['name'], _clean_description(r['description'])]
                 for r in sorted(records['ITYP'], key=lambda r: r['name'])]
    _write_flat_report(
        ityp_rows, 'Item Types', 'Item Types',
        os.path.join(output_root, 'itemtype'), static_path,
        lib_nav(WYLD_LIB, WYLD_LIBCODE, 'itemtype', lookups))

    locn_rows = [[r['name'], _clean_description(r['description']),
                  _yesno(r.get('available')), _yesno(r.get('holdable')), _yesno(r.get('shadowed'))]
                 for r in sorted(records['LOCN'], key=lambda r: r['name'])]
    _write_flat_report(
        locn_rows, 'Item Locations', 'Item Locations',
        os.path.join(output_root, 'location'), static_path,
        lib_nav(WYLD_LIB, WYLD_LIBCODE, 'location', lookups),
        headers=LOCN_HEADERS)

    item_categories = {n: records[f'ICT{n}'] for n in range(1, 11)}
    _write_sectioned_report(
        item_categories, 'Item Category', 'Item Categories', 'Item Categories',
        os.path.join(output_root, 'itemcategory'), static_path,
        lib_nav(WYLD_LIB, WYLD_LIBCODE, 'itemcategory', lookups))

    user_categories = {n: records[f'CAT{n}'] for n in range(1, 11)}
    _write_sectioned_report(
        user_categories, 'User Category', 'User Categories', 'User Categories',
        os.path.join(output_root, 'usercategory'), static_path,
        lib_nav(WYLD_LIB, WYLD_LIBCODE, 'usercategory', lookups))
