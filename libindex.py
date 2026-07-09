"""Generates one hub page per library: library info + policy navigation cards."""

import json
import os
from datetime import datetime, date
from html_utils import page

PREFIXES_FILE = os.path.join(os.path.dirname(__file__), 'uprf_library_prefixes.json')

DAYS = [
    ('closed_sun', 'Sunday'), ('closed_mon', 'Monday'), ('closed_tue', 'Tuesday'),
    ('closed_wed', 'Wednesday'), ('closed_thu', 'Thursday'),
    ('closed_fri', 'Friday'), ('closed_sat', 'Saturday'),
]

WYLD_LIBCODE = '115'

POLICY_CARDS = [
    ('Circmap',     'Circ Map'),
    ('Circrule',    'Circ Rules'),
    ('Holdmap',     'Hold Map'),
    ('Holdcode',    'Holding Codes'),
    ('Defprice',    'Default Prices'),
]

PROFILE_CARD = ('userprofile', 'User Profiles')
RECIRC_CARD = ('recircprofiles', 'Recirculating Profiles')
LIBRARY_USE_CARD = ('libraryuseprofiles', 'Library Use Profiles')
ITEMTYPE_CARD = ('itemtype', 'Item Type Policies')
LOCATION_CARD = ('location', 'Location Policies')
ITEMCATEGORY_CARD = ('itemcategory', 'Item Category Policies')
USERCATEGORY_CARD = ('usercategory', 'User Category Policies')

HUB_CSS = """
.info-table { margin-bottom: 1.5rem; }
.info-table th {
  text-align: right;
  padding-right: .75rem;
  font-weight: 600;
  white-space: nowrap;
  width: 1%;
  color: #1b3a5c;
}
.info-table td { color: #212529; }
.info-table ul { margin: 0; padding: 0; list-style: none; }

.policy-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(175px, 1fr));
  gap: .75rem;
  margin-top: .25rem;
}
.policy-card {
  border: 1px solid #d0d7de;
  border-radius: .4rem;
  padding: .75rem 1rem;
  text-decoration: none;
  color: #1b3a5c;
  background: #fff;
  display: block;
  transition: background .12s, border-color .12s;
}
.policy-card:hover {
  background: #e9eff7;
  border-color: #1b3a5c;
  text-decoration: none;
}
.policy-card-title { font-weight: 700; font-size: .88rem; }

h3.section-label {
  font-size: .68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .07em;
  color: #8a96a3;
  margin: 1.25rem 0 .5rem;
  border-top: 1px solid #e8ecf0;
  padding-top: .75rem;
}
"""


def _load_prefixes():
    with open(PREFIXES_FILE) as f:
        return json.load(f)


def _closed_days(libr):
    closed = [label for field, label in DAYS if libr.get(field) == '1']
    return ', '.join(closed) if closed else 'Open all days'


def _closed_dates(libr):
    starts = libr.get('closed_date_starts', '').split()
    ends = libr.get('closed_date_ends', '').split()
    if not starts:
        return 'None'
    items = []
    for s, e in zip(starts, ends):
        try:
            sd = datetime.fromtimestamp(int(s)).strftime('%b %-d, %Y')
            ed = datetime.fromtimestamp(int(e)).strftime('%b %-d, %Y')
            items.append(f'<li>{sd} – {ed}</li>')
        except (ValueError, OSError):
            pass
    return f'<ul>{"".join(items)}</ul>' if items else 'None'


def _fixed_due_date(libr, lprd_lookup):
    code = libr.get('fixed_due_date_code', '')
    if not code or code == '1':
        return 'No fixed date'
    rec = lprd_lookup.get(code)
    return rec['name'] if rec else code


def _info_row(label, value):
    return f'<tr><th>{label}</th><td>{value}</td></tr>'


def _policy_card(directory, title, lib_lower):
    return (f'<a href="../{directory}/{lib_lower}.html" class="policy-card">'
            f'<div class="policy-card-title">{title}</div>'
            f'</a>')


def generate(records, lookups, output_root, static_path=None):
    out_dir = os.path.join(output_root, 'Libindex')
    os.makedirs(out_dir, exist_ok=True)

    today = date.today().strftime('%B %-d, %Y')
    prefixes = _load_prefixes()
    libs_with_holdcodes = {h.get('library_code') for h in records.get('HLDC', [])}

    for libr in records['LIBR']:
        lib = libr['lib']
        lib_lower = lib.lower()
        lib_name = libr['name']
        libcode = libr['libcode']

        info_rows = ''.join([
            _info_row('Library Code', lib),
            _info_row('Closed Days', _closed_days(libr)),
            _info_row('Closed Dates', _closed_dates(libr)),
            _info_row('Fixed Due Date', _fixed_due_date(libr, lookups['lprd'])),
            _info_row('Accrue Fines on Closed Days',
                      'Yes' if libr.get('accrue_fines_closed') == '1' else 'No'),
            _info_row('Hold Group Libraries', lookups['libg'].get(libr.get('hold_group', ''), '')),
            _info_row('Hold Expire Days', libr.get('hold_expire_days', '')),
            _info_row('Avail Hold Expire Days', libr.get('avail_hold_expire_days', '')),
            _info_row('Onshelf Holds Selected on Closed Dates',
                      'True' if libr.get('skip_onshelf_holds_closed') == '0' else 'False'),
            _info_row('OCLC Code', libr.get('oclc_code', '')),
        ])

        cards = [
            _policy_card(d, t, lib_lower)
            for d, t in POLICY_CARDS
            if d != 'Holdcode' or libcode == WYLD_LIBCODE or libcode in libs_with_holdcodes
        ]
        if lib in prefixes:
            d, t = PROFILE_CARD
            cards.append(_policy_card(d, t, lib_lower))
        if libcode == WYLD_LIBCODE:
            for card in (RECIRC_CARD, LIBRARY_USE_CARD, ITEMTYPE_CARD, LOCATION_CARD,
                         ITEMCATEGORY_CARD, USERCATEGORY_CARD):
                d, t = card
                cards.append(_policy_card(d, t, lib_lower))

        body = (f'<h2>{lib_name}</h2>'
                f'<table class="table table-sm info-table w-auto">'
                f'<tbody>{info_rows}</tbody></table>'
                f'<h3 class="section-label">Policy Pages</h3>'
                f'<div class="policy-grid">{"".join(cards)}</div>'
                f'<style>{HUB_CSS}</style>')

        html = page(f'{lib} Policies', body, today, static_path or '../static')

        with open(os.path.join(out_dir, f'{lib_lower}.html'), 'w') as f:
            f.write(html)

