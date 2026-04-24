"""Shared HTML helpers used by all generators."""

STATIC_PATH = "/new-map/static"

_CSS = """
:root {
  --brand:    #1b3a5c;
  --accent:   #1a5fa8;
  --border:   #d0d7de;
  --row-alt:  #f6f8fa;
  --hdr-h:    52px;
}
*, *::before, *::after { box-sizing: border-box; }
body {
  background: #edf1f7;
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
  font-size: .875rem;
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
  box-shadow: 0 2px 6px rgba(0,0,0,.28);
}
.site-header .inner {
  display: flex;
  align-items: center;
  gap: .6rem;
  width: 100%;
  padding: 0 1.25rem;
}
.site-back {
  color: rgba(255,255,255,.65);
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
  border-left: 1px solid rgba(255,255,255,.3);
}
.site-date {
  margin-left: auto;
  color: rgba(255,255,255,.5);
  font-size: .75rem;
  white-space: nowrap;
}
.main-content { padding: 1.25rem; }
h2 { font-size: 1.1rem; font-weight: 600; color: var(--brand); margin-bottom: .75rem; }
.policy-links { margin-top: .5rem; }
.policy-links li { margin-bottom: .5rem; }
.policy-links a {
  color: #1a5fa8;
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
  color: #1a5fa8;
  text-decoration: none;
  border: 1px solid #d0d7de;
  padding: .2rem .6rem;
  border-radius: .25rem;
  background: #fff;
}
.page-nav a:hover { background: #e9eff7; }
.alert-info {
  background: #e4ecf9;
  border-color: #b0c8ef;
  color: var(--brand);
  font-size: .8rem;
}
.table-responsive {
  border-radius: .4rem;
  border: 1px solid var(--border);
  box-shadow: 0 1px 4px rgba(0,0,0,.07);
  max-height: calc(100vh - var(--hdr-h) - 8rem);
  overflow-y: auto;
}
.table { margin-bottom: 0; font-size: .82rem; }
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
.table td { border-color: var(--border); }
.table a { color: var(--accent); text-decoration: none; }
.table a:hover { text-decoration: underline; }
"""


def page(title, body, date, static_path=STATIC_PATH):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <link rel="stylesheet" href="{static_path}/bootstrap.min.css">
  <style>{_CSS}</style>
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
