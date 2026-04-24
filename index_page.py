"""Generates the index.html landing page."""

import json
import os
from datetime import date
from html_utils import STATIC_PATH

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'index_config.json')

_CSS = """
:root {
  --brand:   #1b3a5c;
  --accent:  #1a5fa8;
  --border:  #d0d7de;
}
body {
  background: #edf1f7;
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
  font-size: .875rem;
  margin: 0;
}
.site-header {
  background: var(--brand);
  padding: .85rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 8px rgba(0,0,0,.25);
}
.site-header h1 { color: #fff; font-size: 1.3rem; font-weight: 700; margin: 0; }
.site-header .tagline { color: rgba(255,255,255,.55); font-size: .73rem; margin-top: .2rem; }
.hdr-right { text-align: right; }
.hdr-right a {
  color: #fff;
  font-weight: 500;
  text-decoration: none;
  font-size: .85rem;
  border: 1px solid rgba(255,255,255,.45);
  padding: .3rem .85rem;
  border-radius: .3rem;
  white-space: nowrap;
  display: inline-block;
}
.hdr-right a:hover { background: rgba(255,255,255,.12); }
.hdr-right .date { color: rgba(255,255,255,.45); font-size: .72rem; margin-top: .35rem; }
.columns-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.25rem;
  padding: 1.5rem;
}
@media (max-width: 1000px) { .columns-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 550px)  { .columns-grid { grid-template-columns: 1fr; } }
.col-card {
  background: #fff;
  border: 1px solid var(--border);
  border-radius: .4rem;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0,0,0,.08);
}
.col-card-header {
  background: var(--brand);
  color: #fff;
  padding: .55rem .9rem;
  font-size: .72rem;
  font-weight: 700;
  letter-spacing: .07em;
  text-transform: uppercase;
}
.col-card-body { padding: .6rem .9rem; }
.lib-group { border-top: 1px solid #e8ecf0; }
.lib-group:first-child { border-top: none; }
.lib-group-label {
  font-size: .67rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .07em;
  color: #8a96a3;
  padding: .5rem 0 .15rem;
}
.lib-group ul { margin: 0; padding: 0 0 .5rem; list-style: none; }
.lib-group li { line-height: 1.1; }
.lib-group a {
  color: var(--accent);
  text-decoration: none;
  font-size: .82rem;
  display: block;
  padding: .22rem 0;
}
.lib-group a:hover { text-decoration: underline; color: #0f3d7a; }
"""


def _load_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)


def _member_link(member, base_path):
    lib = member['lib'].lower()
    return f'<a href="{base_path}Libindex/{lib}.html">{member["label"]}</a>'


def _render_group(group, base_path):
    links = '\n'.join(f'<li>{_member_link(m, base_path)}</li>' for m in group['members'])
    if not group['label']:
        return f'<div class="lib-group"><ul>\n{links}\n</ul></div>'
    return (
        f'<div class="lib-group">'
        f'<div class="lib-group-label">{group["label"]}</div>'
        f'<ul>\n{links}\n</ul>'
        f'</div>'
    )


def _render_column(column, base_path):
    groups_html = '\n'.join(_render_group(g, base_path) for g in column['groups'])
    return (
        f'<div class="col-card">'
        f'<div class="col-card-header">{column["label"]}</div>'
        f'<div class="col-card-body">{groups_html}</div>'
        f'</div>'
    )


def generate(records, lookups, output_root, static_path=None):
    config = _load_config()
    sp = static_path or STATIC_PATH
    today = date.today().strftime('%B %-d, %Y')
    base_path = '/new-map/' if static_path is None else ''

    standalone = config['standalone']
    standalone_link = _member_link(standalone, base_path)

    columns_html = '\n'.join(_render_column(col, base_path) for col in config['columns'])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>WYLD Policy Map</title>
  <link rel="stylesheet" href="{sp}/bootstrap.min.css">
  <style>{_CSS}</style>
</head>
<body>
  <div class="site-header">
    <div>
      <h1>WYLD Policy Map</h1>
      <div class="tagline">Static pages &middot; refreshed nightly</div>
    </div>
    <div class="hdr-right">
      {standalone_link}
      <div class="date">{today}</div>
    </div>
  </div>

  <div class="columns-grid">
{columns_html}
  </div>

  <script src="{sp}/bootstrap.bundle.min.js"></script>
</body>
</html>"""

    out_path = os.path.join(output_root, 'index.html')
    with open(out_path, 'w') as f:
        f.write(html)

    print(f"  index: wrote {out_path}")
