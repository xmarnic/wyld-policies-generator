"""Generates a single WYLD-wide page listing all recirculating user profiles."""

import os
from datetime import date
from html_utils import page, table
from userprofile import HEADERS, _profile_row


def generate(records, lookups, output_root, static_path=None):
    out_dir = os.path.join(output_root, 'recircprofiles')
    os.makedirs(out_dir, exist_ok=True)

    today = date.today().strftime('%B %-d, %Y')
    locn_lookup = lookups['locn']

    recirculating = [u for u in records['UPRF'] if u.get('recirculating') == 'Y']
    recirculating.sort(key=lambda u: u['name'])

    rows = [_profile_row(u, locn_lookup) for u in recirculating]
    body = f'<h2>Recirculating User Profiles</h2>\n{table(HEADERS, rows)}'
    html = page('Recirculating User Profiles', body, today, static_path or '../static')

    with open(os.path.join(out_dir, 'wyld.html'), 'w') as f:
        f.write(html)
