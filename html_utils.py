"""Shared HTML helpers used by all generators."""

STATIC_PATH = "/new-map/static"

_CSS = """
:root {
  --brand:    #1e66f5;
  --accent:   #1e66f5;
  --border:   #ccd0da;
  --row-alt:  #e6e9ef;
  --text:     #4c4f69;
  --hdr-h:    52px;
}
*, *::before, *::after { box-sizing: border-box; }
body {
  background: #eff1f5;
  font-family: 'Geist', system-ui, sans-serif;
  font-size: 1rem;
  color: var(--text);
  margin: 0;
  padding: 0;
}
.site-header {
  background: var(--brand);
  height: var(--hdr-h);
  display: flex;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 8px rgba(30,102,245,.35);
}
.site-header .inner {
  display: flex;
  align-items: center;
  gap: .6rem;
  width: 100%;
  padding: 0 1.25rem;
}
.site-back {
  color: rgba(255,255,255,.75);
  text-decoration: none;
  font-size: .78rem;
  white-space: nowrap;
  flex-shrink: 0;
}
.site-back:hover { color: #fff; }
.site-title {
  color: #fff;
  font-size: 1.05rem;
  font-weight: 600;
  margin: 0;
  padding-left: .65rem;
  border-left: 1px solid rgba(255,255,255,.35);
}
.site-date {
  margin-left: auto;
  color: rgba(255,255,255,.6);
  font-size: .75rem;
  white-space: nowrap;
}
.main-content { padding: 1.25rem; }
h2 { font-size: 1.1rem; font-weight: 600; color: var(--brand); margin-bottom: .75rem; }
.policy-links { margin-top: .5rem; }
.policy-links li { margin-bottom: .5rem; }
.policy-links a {
  color: var(--accent);
  font-size: .95rem;
  text-decoration: none;
}
.policy-links a:hover { text-decoration: underline; }
.page-nav {
  display: flex;
  gap: .5rem;
  margin-bottom: 1rem;
  font-size: .8rem;
}
.page-nav a {
  color: var(--accent);
  text-decoration: none;
  border: 1px solid var(--border);
  padding: .2rem .6rem;
  border-radius: .25rem;
  background: #e6e9ef;
}
.page-nav a:hover { background: #ccd0da; }
.alert-info {
  background: #dce0e8;
  border-color: var(--border);
  color: var(--text);
  font-size: .8rem;
}
.table-responsive {
  border-radius: .4rem;
  border: 1px solid var(--border);
  box-shadow: 0 1px 4px rgba(30,102,245,.1);
  max-height: calc(100vh - var(--hdr-h) - 8rem);
  overflow-y: auto;
}
.table { margin-bottom: 0; font-size: .82rem; font-family: 'Monaspace Neon', ui-monospace, monospace; }
.table thead th {
  background: var(--brand) !important;
  color: #fff !important;
  font-size: .7rem;
  font-weight: 600;
  letter-spacing: .06em;
  text-transform: uppercase;
  border-color: rgba(255,255,255,.15) !important;
  white-space: nowrap;
  position: sticky;
  top: 0;
  z-index: 2;
}
.table tbody tr:nth-child(even) > td { background: var(--row-alt); }
.table td { border-color: var(--border); color: var(--text); }
.table a { color: var(--accent); text-decoration: none; }
.table a:hover { text-decoration: underline; }
"""


_LIB_NAV_PAGES = [
    ('Circmap',     'Circ Map'),
    ('Holdmap',     'Hold Map'),
    ('Circrule',    'Circ Rules'),
    ('userprofile', 'User Profiles'),
]


def lib_nav(lib, current_dir=None):
    lib_lower = lib.lower()
    links = [f'<a href="../Libindex/{lib_lower}.html">← {lib}</a>']
    for directory, label in _LIB_NAV_PAGES:
        if directory != current_dir:
            links.append(f'<a href="../{directory}/{lib_lower}.html">{label}</a>')
    return f'<div class="page-nav">{"".join(links)}</div>'


def page(title, body, date, static_path=STATIC_PATH):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <link rel="stylesheet" href="{static_path}/bootstrap.min.css">
  <style>@font-face {{
  font-family: 'Geist';
  src: url('{static_path}/fonts/GeistVar.woff2') format('woff2');
  font-weight: 100 900;
}}
@font-face {{
  font-family: 'Monaspace Neon';
  src: url('{static_path}/fonts/MonaspaceNeonVar.woff2') format('woff2');
  font-weight: 100 900;
}}{_CSS}</style>
</head>
<body>
  <div class="site-header">
    <div class="inner">
      <a href="../index.html" class="site-back">← WYLD Policy Map</a>
      <h1 class="site-title">{title}</h1>
      <span class="site-date">{date}</span>
    </div>
  </div>
  <div class="main-content">
    {body}
  </div>
  <script src="{static_path}/bootstrap.bundle.min.js"></script>
</body>
</html>"""


def table(headers, rows):
    ths = ''.join(f'<th scope="col">{h}</th>' for h in headers)
    trs = ''
    for row in rows:
        tds = ''.join(f'<td>{cell}</td>' for cell in row)
        trs += f'<tr>{tds}</tr>\n'
    return f"""<div class="table-responsive">
  <table class="table table-bordered table-hover table-sm align-middle">
    <thead><tr>{ths}</tr></thead>
    <tbody>{trs}</tbody>
  </table>
</div>"""
