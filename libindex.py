"""Generates one hub page per library linking to all its policy pages."""

import json
import os
from datetime import date
from html_utils import page

PREFIXES_FILE = os.path.join(os.path.dirname(__file__), 'uprf_library_prefixes.json')


def _load_prefixes():
    with open(PREFIXES_FILE) as f:
        return json.load(f)


def _link_item(href, label):
    return f'<li><a href="{href}">{label}</a></li>'


def generate(records, lookups, output_root, static_path=None):
    out_dir = os.path.join(output_root, 'Libindex')
    os.makedirs(out_dir, exist_ok=True)

    today = date.today().strftime('%B %-d, %Y')
    prefixes = _load_prefixes()

    for libr in records['LIBR']:
        lib = libr['lib']
        lib_lower = lib.lower()
        lib_name = libr['name']

        items = [
            _link_item(f'../Libinfo/{lib_lower}.html', 'Library Information'),
            _link_item(f'../Circmap/{lib_lower}.html', 'Circ Map'),
            _link_item(f'../Circrule/{lib_lower}.html', 'Circ Rules'),
            _link_item(f'../Holdmap/{lib_lower}.html', 'Hold Map'),
            _link_item(f'../Holdcode/{lib_lower}.html', 'Holding Codes'),
            _link_item(f'../Defprice/{lib_lower}.html', 'Default Prices'),
        ]

        if lib in prefixes:
            items.append(_link_item(f'../userprofile/{lib_lower}.html', 'User Profiles'))

        links_html = '\n'.join(f'  {item}' for item in items)

        body = f'''<h2>{lib_name}</h2>
<ul class="list-unstyled policy-links">
{links_html}
</ul>'''

        html = page(f'{lib} — Library Policies', body, today, static_path or '../static')

        with open(os.path.join(out_dir, f'{lib_lower}.html'), 'w') as f:
            f.write(html)

    print(f"  libindex: wrote {len(records['LIBR'])} pages to {out_dir}")
