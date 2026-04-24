"""Generates one holdmap HTML page per library."""

import os
from datetime import date
from policy_parser import ALL_CODE
from html_utils import page, table

HEADERS = ['NAME', 'DESCRIPTION', 'LIBRARY', 'ITEM TYPE', 'USER PROFILE', 'PERMISSION', 'PRIORITY']

PERMISSION_LABELS = {
    '0': 'NO_HOLDS',
    '1': 'OWN_LIBRARY',
    '2': 'OWN_GROUP',
    '3': 'ALL_LIBS',
}

PRIORITY_LABELS = {
    '0': 'NONE',
    '1': 'OWN_GROUP',
    '2': 'OWN_LIBRARY',
    '3': 'OWNLIBGRP',
}


def _resolve_codes(codes, lookup, all_label='All'):
    if ALL_CODE in codes:
        return all_label
    names = [lookup.get(c, {}).get('name', c) for c in codes]
    return ', '.join(names)


def _library_name(library_codes, libr_lookup):
    if ALL_CODE in library_codes:
        return 'All'
    names = [libr_lookup.get(c, {}).get('lib', c) for c in library_codes]
    return ', '.join(names)


def generate(records, lookups, output_root, static_path=None):
    out_dir = os.path.join(output_root, 'Holdmap')
    os.makedirs(out_dir, exist_ok=True)

    today = date.today().strftime('%B %-d, %Y')
    hmaps = records['HMAP']

    for libr in records['LIBR']:
        libcode = libr['libcode']
        lib = libr['lib']
        lib_name = libr['name']

        if libcode == '115':
            relevant = hmaps
        else:
            relevant = [h for h in hmaps if libcode in h['library_codes']]

        rows = []
        for hmap in relevant:
            library_cell = _library_name(hmap['library_codes'], lookups['libr'])
            item_type = _resolve_codes(hmap['item_type_codes'], lookups['ityp'])
            user_profile = _resolve_codes(hmap['user_profile_codes'], lookups['uprf'])
            permission = PERMISSION_LABELS.get(hmap['permission'], hmap['permission'])
            priority = PRIORITY_LABELS.get(hmap['priority'], hmap['priority'])

            rows.append([
                hmap['name'],
                hmap['description'],
                library_cell,
                item_type,
                user_profile,
                permission,
                priority,
            ])

        note = ('<div class="alert alert-info small">'
                '<strong>NOTE:</strong> The order of the Hold Map is important. '
                'Symphony reads from most specific to most general. Read this table from the bottom up.'
                '</div>')

        heading = 'Hold Map Policy' if libcode == '115' else f'Hold Map Policy for {lib_name}'
        nav = (f'<div class="page-nav">'
               f'<a href="../Libindex/{lib.lower()}.html">← {lib}</a>'
               f'<a href="../Circmap/{lib.lower()}.html">Circ Map</a>'
               f'<a href="../userprofile/{lib.lower()}.html">User Profiles</a>'
               f'</div>')
        body = f'<h2>{heading}</h2>\n{nav}\n{note}\n{table(HEADERS, rows)}'
        html = page(f'{lib} Hold Map', body, today, static_path or '../static')

        with open(os.path.join(out_dir, f'{lib.lower()}.html'), 'w') as f:
            f.write(html)

    print(f"  holdmap: wrote {len(records['LIBR'])} pages to {out_dir}")
