"""Generates one library info HTML page per library."""

import os
from datetime import datetime, date
from html_utils import page, lib_nav

WYLD_LIBCODE = '115'

DAYS = [
    ('closed_sun', 'Sunday'),
    ('closed_mon', 'Monday'),
    ('closed_tue', 'Tuesday'),
    ('closed_wed', 'Wednesday'),
    ('closed_thu', 'Thursday'),
    ('closed_fri', 'Friday'),
    ('closed_sat', 'Saturday'),
]


def _closed_days(libr):
    closed = [label for field, label in DAYS if libr.get(field) == '1']
    return ', '.join(closed) if closed else 'Open all days'


def _closed_dates(libr):
    starts = libr.get('closed_date_starts', '').split()
    ends = libr.get('closed_date_ends', '').split()
    if not starts:
        return 'None'
    rows = []
    for s, e in zip(starts, ends):
        try:
            sd = datetime.fromtimestamp(int(s)).strftime('%b %-d, %Y')
            ed = datetime.fromtimestamp(int(e)).strftime('%b %-d, %Y')
            rows.append(f'<li>{sd} – {ed}</li>')
        except (ValueError, OSError):
            pass
    return f'<ul class="list-unstyled mb-0">{"".join(rows)}</ul>' if rows else 'None'


def _fixed_due_date(libr, lprd_lookup):
    code = libr.get('fixed_due_date_code', '')
    if not code or code == '1':
        return 'No fixed date'
    rec = lprd_lookup.get(code)
    return rec['name'] if rec else code


def _row(label, value):
    return (f'<tr>'
            f'<th class="text-end pe-3 text-nowrap fw-semibold" style="width:1%">{label}</th>'
            f'<td>{value}</td>'
            f'</tr>')


def generate(records, lookups, output_root, static_path=None):
    out_dir = os.path.join(output_root, 'Libinfo')
    os.makedirs(out_dir, exist_ok=True)

    today = date.today().strftime('%B %-d, %Y')

    for libr in records['LIBR']:
        lib = libr['lib']
        lib_name = libr['name']

        hold_loc_code = libr.get('hold_location_code', '')
        hold_loc = lookups['locn'].get(hold_loc_code, {}).get('name', hold_loc_code) if hold_loc_code else '—'

        rows_html = ''.join([
            _row('Library Code', lib),
            _row('Name', lib_name),
            _row('User ID', libr.get('user_id', '')),
            _row('Closed Days', _closed_days(libr)),
            _row('Closed Dates', _closed_dates(libr)),
            _row('Fixed Due Date', _fixed_due_date(libr, lookups['lprd'])),
            _row('Hold Location', hold_loc),
            _row('Accrue Fines on Closed Days', 'Yes' if libr.get('accrue_fines_closed') == '1' else 'No'),
            _row('Days for Holds to Expire', libr.get('hold_expire_days', '')),
            _row('Days for Available Holds to Expire', libr.get('avail_hold_expire_days', '')),
            _row('OCLC Code', libr.get('oclc_code', '')),
        ])

        nav = lib_nav(lib, 'Libinfo', lookups)
        body = (f'<h2>Library Information — {lib_name}</h2>'
                f'{nav}'
                f'<table class="table table-bordered table-sm w-auto">'
                f'<tbody>{rows_html}</tbody>'
                f'</table>')

        html = page(f'Library Info — {lib}', body, today, static_path or '../static')

        with open(os.path.join(out_dir, f'{lib.lower()}.html'), 'w') as f:
            f.write(html)

