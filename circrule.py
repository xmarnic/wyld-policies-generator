"""Generates one Thiscircrule HTML page per circ rule."""

import os
from datetime import date
from html_utils import page, table

HEADERS = [
    'NAME', 'DESCRIPTION', 'LOAN PERIOD', 'BILL STRUCTURE',
    'RENEW LIMIT', 'CHARGEABLE', 'GRACE PERIOD', 'RECALL DUE',
    'OVERDUE', 'MAX LOAN', 'RECALL PERIOD', 'ALT LOAN PERIOD',
]

PERIOD_UNITS = {'0': 'days', '1': 'hours', '2': 'minutes'}


def _resolve(code, lookup):
    if not code:
        return ''
    rec = lookup.get(code)
    return rec['name'] if rec else code


def generate(records, lookups, output_root, static_path=None):
    out_dir = os.path.join(output_root, 'Circrules')
    os.makedirs(out_dir, exist_ok=True)

    today = date.today().strftime('%B %-d, %Y')

    for circ in records['CIRC']:
        code = circ['code']
        name = circ['name']

        grace = circ.get('grace_period', '')
        unit = PERIOD_UNITS.get(circ.get('period_unit', ''), '')
        grace_cell = f"{grace} {unit}".strip() if grace else ''

        row = [
            name,
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

        body = f'<h2>Circ Rule: {name}</h2>\n{table(HEADERS, [row])}'
        html = page(f'Circ Rule — {name}', body, today, static_path or '../static')

        with open(os.path.join(out_dir, f'{code}.html'), 'w') as f:
            f.write(html)

    print(f"  circrule: wrote {len(records['CIRC'])} pages to {out_dir}")
