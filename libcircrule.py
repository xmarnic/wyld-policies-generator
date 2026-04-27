"""Generates a per-library circ rules page showing rules used in that library's circ map."""

import os
from datetime import date
from html_utils import page, table, lib_nav

HEADERS = [
    'NAME', 'DESCRIPTION', 'LOAN PERIOD', 'BILL STRUCTURE',
    'RENEW LIMIT', 'CHARGEABLE', 'GRACE PERIOD', 'RECALL DUE',
    'OVERDUE', 'MAX LOAN', 'RECALL PERIOD', 'ALT LOAN PERIOD',
]

PERIOD_UNITS = {'0': 'days', '1': 'hours', '2': 'minutes'}
WYLD_LIBCODE = '115'


def _resolve(code, lookup):
    if not code:
        return ''
    rec = lookup.get(code)
    return rec['name'] if rec else code


def _circ_row(circ, lookups):
    grace = circ.get('grace_period', '')
    unit = PERIOD_UNITS.get(circ.get('period_unit', ''), '')
    grace_cell = f'{grace} {unit}'.strip() if grace else ''

    name_link = f'<a href="../Circrules/{circ["code"]}.html">{circ["name"]}</a>'

    return [
        name_link,
        circ.get('description', ''),
        _resolve(circ.get('loan_period_code'), lookups['lprd']),
        _resolve(circ.get('bill_structure_code'), lookups['bstr']),
        circ.get('renew_limit', ''),
        'Yes' if circ.get('chargeable', '0') not in ('0', '') else 'No',
        grace_cell,
        circ.get('recall_due', ''),
        'Yes' if circ.get('overdue_flag', '0') not in ('0', '') else 'No',
        circ.get('max_loan', ''),
        _resolve(circ.get('recall_loan_period_code'), lookups['lprd']),
        _resolve(circ.get('alt_loan_period_code'), lookups['lprd']),
    ]


def generate(records, lookups, output_root, static_path=None):
    out_dir = os.path.join(output_root, 'Circrule')
    os.makedirs(out_dir, exist_ok=True)

    today = date.today().strftime('%B %-d, %Y')
    circ_lookup = lookups['circ']
    cmaps = records['CMAP']

    for libr in records['LIBR']:
        libcode = libr['libcode']
        lib = libr['lib']
        lib_name = libr['name']

        if libcode == WYLD_LIBCODE:
            relevant_circs = list(records['CIRC'])
            heading = 'All WYLD Circ Rules'
        else:
            used_codes = {c['circ_rule_code'] for c in cmaps if libcode in c['library_codes']}
            relevant_circs = [circ_lookup[code] for code in used_codes if code in circ_lookup]
            relevant_circs.sort(key=lambda c: c['name'])
            heading = f'Circ Rules for {lib_name}'

        if not relevant_circs:
            continue

        rows = [_circ_row(c, lookups) for c in relevant_circs]
        nav = lib_nav(lib, 'Circrule')
        body = f'<h2>{heading}</h2>\n{nav}\n{table(HEADERS, rows)}'
        html = page(f'{lib} Circ Rules', body, today, static_path or '../static')

        with open(os.path.join(out_dir, f'{lib.lower()}.html'), 'w') as f:
            f.write(html)

    print(f"  libcircrule: wrote pages to {out_dir}")
