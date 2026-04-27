"""Generates one hold code HTML page per library."""

import os
from datetime import date
from html_utils import page, table, lib_nav

HEADERS = ['NAME', 'DESCRIPTION', 'LIBRARY', 'LOCATION', 'ITEM TYPE']

WYLD_LIBCODE = '115'


def generate(records, lookups, output_root, static_path=None):
    out_dir = os.path.join(output_root, 'Holdcode')
    os.makedirs(out_dir, exist_ok=True)

    today = date.today().strftime('%B %-d, %Y')
    all_hldc = records['HLDC']

    for libr in records['LIBR']:
        libcode = libr['libcode']
        lib = libr['lib']
        lib_name = libr['name']

        if libcode == WYLD_LIBCODE:
            relevant = all_hldc
            heading = 'All WYLD Holding Codes'
        else:
            relevant = [h for h in all_hldc if h.get('library_code') == libcode]
            heading = f'Holding Codes for {lib_name}'

        if not relevant:
            continue

        rows = []
        for hldc in relevant:
            lib_cell = lookups['libr'].get(hldc.get('library_code', ''), {}).get('lib', '')
            locn_cell = lookups['locn'].get(hldc.get('location_code', ''), {}).get('name', '')
            ityp_cell = lookups['ityp'].get(hldc.get('item_type_code', ''), {}).get('name', '')
            rows.append([
                hldc.get('name', ''),
                hldc.get('description', ''),
                lib_cell,
                locn_cell,
                ityp_cell,
            ])

        nav = lib_nav(lib, 'Holdcode')
        body = f'<h2>{heading}</h2>\n{nav}\n{table(HEADERS, rows)}'
        html = page(f'{lib} Holding Codes', body, today, static_path or '../static')

        with open(os.path.join(out_dir, f'{lib.lower()}.html'), 'w') as f:
            f.write(html)

    print(f"  holdcode: wrote pages to {out_dir}")
