"""Generates one circmap HTML page per library."""

import os
from datetime import date
from policy_parser import ALL_CODE
from html_utils import page, table

HEADERS = ['NAME', 'LIBRARY', 'PATRON', 'ITEM TYPE', 'CIRC RULE']

HARDCODED_ROWS = [
    ['DEFAULT',    'ALL', 'ALL',                                        'ALL', 'NONCIRC-Y'],
    ['DISPLAY-AL', 'ALL', 'BINDERY, DISPLAY',                          'ALL', '<a href="../Circrules/53.html">D120-RULE1</a>'],
    ['LIB-USE',    'ALL', 'DISP_NEW, DISPLAY, LIBRARYUSE, LL, LOST, MISSING', 'ALL', '<a href="../Circrules/3.html">UNLIMITED</a>'],
    ['LOSTCARD',   'ALL', 'LOSTCARD',                                  'ALL', 'NONCIRC-N'],
    ['FDILL-ALL',  'ALL', 'FDILL',                                     'ALL', '<a href="../Circrules/36.html">D28-RULE2</a>'],
    ['REPAIR-ALL', 'ALL', 'REPAIR',                                    'ALL', '<a href="../Circrules/53.html">D120-RULE1</a>'],
]


def _resolve_codes(codes, lookup, all_label='All'):
    if ALL_CODE in codes:
        return all_label
    names = [lookup.get(c, {}).get('name', c) for c in codes]
    return ', '.join(names)


def _circ_rule_cell(circ_rule_code, circ_lookup):
    record = circ_lookup.get(circ_rule_code)
    name = record['name'] if record else circ_rule_code
    return f'<a href="../Circrules/{circ_rule_code}.html">{name}</a>'


def _build_rows(cmaps, libcode, lib_name, lookups):
    rows = []
    for cmap in cmaps:
        if libcode not in cmap['library_codes']:
            continue

        if ALL_CODE in cmap['library_codes']:
            library_cell = 'All'
        else:
            library_cell = lib_name

        patron = _resolve_codes(cmap['patron_profile_codes'], lookups['uprf'])
        item_type = _resolve_codes(cmap['item_type_codes'], lookups['ityp'])
        circ_rule = _circ_rule_cell(cmap['circ_rule_code'], lookups['circ'])

        rows.append([cmap['name'], library_cell, patron, item_type, circ_rule])
    return rows


def generate(records, lookups, output_root, static_path=None):
    out_dir = os.path.join(output_root, 'Circmap')
    os.makedirs(out_dir, exist_ok=True)

    today = date.today().strftime('%B %-d, %Y')
    cmaps = records['CMAP']

    for libr in records['LIBR']:
        libcode = libr['libcode']
        lib = libr['lib']
        lib_name = libr['name']

        if libcode == '115':
            heading = 'Complete Circ Map Policy'
            relevant = [c for c in cmaps if not c['library_codes']]
        else:
            heading = f'Circ Map Policy for {lib_name}'
            relevant = [c for c in cmaps if libcode in c['library_codes']]

        rows = _build_rows(relevant, libcode, lib, lookups)
        all_rows = rows + HARDCODED_ROWS

        note = ('<div class="alert alert-info small">'
                '<strong>NOTE:</strong> The order of the Circ Map is important. '
                'Unicorn reads from most specific to most general — read this table from the bottom up.'
                '</div>')

        nav = (f'<div class="page-nav">'
               f'<a href="../Libindex/{lib.lower()}.html">← {lib}</a>'
               f'<a href="../Holdmap/{lib.lower()}.html">Hold Map</a>'
               f'<a href="../userprofile/{lib.lower()}.html">User Profiles</a>'
               f'</div>')
        body = f'<h2>{heading}</h2>\n{nav}\n{note}\n{table(HEADERS, all_rows)}'
        html = page(f'Circ Map — {lib}', body, today, static_path or '../static')

        with open(os.path.join(out_dir, f'{lib.lower()}.html'), 'w') as f:
            f.write(html)

    print(f"  circmap: wrote {len(records['LIBR'])} pages to {out_dir}")
