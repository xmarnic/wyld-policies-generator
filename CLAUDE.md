# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Generator

```bash
# Development — generates to /tmp and serves locally
python3 generate.py mock-data/policies /tmp/wyld-test --local
python3 -m http.server 8080 --directory /tmp/wyld-test --bind 0.0.0.0
```

There are no tests and no linter configured. The `policies` file in the repo root is a mock snapshot used for local development.

## Architecture

`generate.py` is the entry point. It parses the policies file once via `policy_parser.py`, builds shared lookup dicts, then calls each generator module in sequence. All generators receive the same `records` and `lookups` dicts and write independently to the output directory.

**Data flow:**
1. `policy_parser.py` reads the `|`-delimited policies flat file and maps fields by index (per `SCHEMAS`) into named dicts. Fields not in the schema are ignored. List-valued fields (e.g. `library_codes`) are split on commas.
2. `generate.py` builds O(1) lookup dicts (`circ`, `uprf`, `ityp`, `locn`, `lprd`, `bstr`, `libr`, `libg`) for cross-referencing codes to names.
3. Each generator module (e.g. `circmap.py`, `holdmap.py`) filters and renders its own subset of records into HTML pages, one per library.

**Special values:**
- `ALL_CODE = "25000"` — the sentinel value meaning "applies to all libraries/patrons/item types" in list-valued CMAP/HMAP fields.
- Library `libcode` `"115"` is the WYLD-wide library; `circmap.py` uses it to generate the "Complete Circ Map Policy" page showing all CMAP records unfiltered.

**Shared rendering:**
- `html_utils.py` — `page()` wraps a body string in the full HTML shell with header/nav/styles; `table()` renders a list of rows into a Bootstrap table; `lib_nav()` builds the per-page nav strip.
- All detail pages use `../static` as the asset path (relative to their subdirectory). The `--local` flag sets this; production uses an absolute server path.

## Configuration Files

- **`index_config.json`** — controls which libraries appear on the index page and how they are grouped. Libraries in the policies file but absent here still get pages generated; they just won't be linked from the index.
- **`uprf_library_prefixes.json`** — maps library `lib` abbreviation to the UPRF record name prefix (e.g. `"LARM": "02"`). This is not derivable from the policies file. Libraries absent here get no User Profiles page.

## Adding a New Generator

Each generator module exports a single `generate(records, lookups, output_root, static_path=None)` function. Call it from `generate.py` after the existing generators. Output goes in a subdirectory of `output_root`. Use `page()` and `table()` from `html_utils.py` for consistent rendering.
