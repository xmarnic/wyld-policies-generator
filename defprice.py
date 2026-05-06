"""Generates one default price HTML page per library."""

import os
from datetime import date
from html_utils import page, table, lib_nav

HEADERS = [
    'NAME', 'DESCRIPTION', 'LIBRARY', 'ITEM TYPE',
    'PROCESSING FEE (¢)', 'DEFAULT PRICE (¢)',
    'REMOVE PRO FEE', 'USE DEFAULT ALWAYS', 'AUTO REFUND', 'DEDUCT OVERDUE FINE',
]

WYLD_LIBCODE = '115'
ALL_ITEM_TYPE = '25000'


def _yesno(val):
    return 'Yes' if val == '1' else 'No'


def generate(records, lookups, output_root, static_path=None):
    out_dir = os.path.join(output_root, 'Defprice')
    os.makedirs(out_dir, exist_ok=True)

    today = date.today().strftime('%B %-d, %Y')
    all_defp = records['DEFP']

    for libr in records['LIBR']:
        libcode = libr['libcode']
        lib = libr['lib']
        lib_name = libr['name']

        if libcode == WYLD_LIBCODE:
            relevant = all_defp
            heading = 'Complete Default Price Policy'
        else:
            relevant = [d for d in all_defp if d.get('library_code') == libcode]
            heading = f'Default Price Policy for {lib_name}'

        if not relevant:
            continue

        note = ('<div class="alert alert-info small">'
                '<strong>NOTE:</strong> The default price policy is read from the top down.'
                '</div>')

        rows = []
        for defp in relevant:
            lib_cell = lookups['libr'].get(defp.get('library_code', ''), {}).get('lib', '')
            ityp_code = defp.get('item_type_code', '')
            ityp_cell = 'All' if ityp_code == ALL_ITEM_TYPE else lookups['ityp'].get(ityp_code, {}).get('name', ityp_code)
            rows.append([
                defp.get('name', ''),
                defp.get('description', ''),
                lib_cell,
                ityp_cell,
                defp.get('processing_fee', ''),
                defp.get('default_price', ''),
                _yesno(defp.get('remove_profee', '0')),
                _yesno(defp.get('use_default_always', '0')),
                _yesno(defp.get('auto_refund', '0')),
                _yesno(defp.get('deduct_overdue_fine', '0')),
            ])

        nav = lib_nav(lib, 'Defprice', lookups)
        body = f'<h2>{heading}</h2>\n{nav}\n{note}\n{table(HEADERS, rows)}'
        html = page(f'Default Prices — {lib}', body, today, static_path or '../static')

        with open(os.path.join(out_dir, f'{lib.lower()}.html'), 'w') as f:
            f.write(html)

