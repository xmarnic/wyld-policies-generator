# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Generator

```bash
# Development — generates to /tmp and serves locally
python3 generate.py mock-data/policies /tmp/wyld-test --local
python3 -m http.server 8080 --directory /tmp/wyld-test --bind 0.0.0.0
```

There are no tests and no linter configured. The `policies` file in the repo root is a mock snapshot used for local development.

`generate.py` also reads two sibling files in the same directory as `policies` (mocked in `mock-data/`): `ictx.pol` (item categories `ICT6`-`ICT10`, since `ICT1`-`ICT5` live in the main `policies` file) and `ucat.pol` (all of user categories `CAT1`-`CAT10`, no split across files). Both are parsed via `policy_parser.parse_aux_file(path, record_types)` and merged into `records` in `generate.py` before any generator runs.

## Architecture

`generate.py` is the entry point. It parses the policies file once via `policy_parser.py`, builds shared lookup dicts, then calls each generator module in sequence. All generators receive the same `records` and `lookups` dicts and write independently to the output directory.

**Data flow:**
1. `policy_parser.py` reads the `|`-delimited policies flat file and maps fields by index (per `SCHEMAS`) into named dicts. Fields not in the schema are ignored. List-valued fields (e.g. `library_codes`) are split on commas.
2. `generate.py` builds O(1) lookup dicts (`circ`, `uprf`, `ityp`, `locn`, `lprd`, `bstr`, `libr`, `libg`) for cross-referencing codes to names.
3. Each generator module (e.g. `circmap.py`, `holdmap.py`) filters and renders its own subset of records into HTML pages, one per library. `wyldprofiles.py` is the exception — it renders WYLD-only, single-page admin reports (see below), not one page per library.

**Special values:**
- `ALL_CODE = "25000"` — the sentinel value meaning "applies to all libraries/patrons/item types" in list-valued CMAP/HMAP fields.
- Library `libcode` `"115"` is the WYLD-wide library; `circmap.py` uses it to generate the "Complete Circ Map Policy" page showing all CMAP records unfiltered. `libindex.py`'s `WYLD_LIBCODE` constant is the same value, used to gate cards that should only appear on the WYLD hub page (e.g. the Recirculating/Library Use profile cards added by `wyldprofiles.py`).

**UPRF field indexing gotcha:**
`SCHEMAS` indexes directly into `line.split('|')`, where `fields[0]` is the record-type token (e.g. `"UPRF"`) itself. If you're checking field positions with `cut -d'|' -f N` against the raw policies file, `cut` counts that record-type token as field 1 — so a schema index is always `cut` field number minus 1. Verify any new field mapping against `mock-data/policies` for a record whose value you can predict (e.g. `LIBRARYUSE` is recirculating and library-use; `17PA` is a patron profile and isn't) before trusting the offset.

**WYLD-only admin reports (`wyldprofiles.py`):**
Some data isn't meaningfully per-library — e.g. UPRF's `recirculating` and `increment_charge_counter` flags are profile-wide, not library-scoped. `wyldprofiles.py` generates these as single global pages (`userprofile/wyld.html`, `recircprofiles/wyld.html`, `libraryuseprofiles/wyld.html`), reusing `HEADERS`/`_profile_row` from `userprofile.py` rather than duplicating the table rendering. Their cards are added in `libindex.py`'s `generate()` only when `libcode == WYLD_LIBCODE`. Note `userprofile.py` itself no longer generates the "all profiles" page for WYLD (that special case was moved into `wyldprofiles.py`) — its per-library loop skips any `lib` whose `uprf_library_prefixes.json` prefix is `"all"`.

`wyldprofiles.py` also generates four reference policy reports the same way: `itemtype/wyld.html` and `location/wyld.html` (flat two-column tables from `records['ITYP']`/`records['LOCN']`), and `itemcategory/wyld.html`/`usercategory/wyld.html` (one table per `ICT1`-`ICT10`/`CAT1`-`CAT10`, sections with no records silently skipped). All four `SCHEMAS` entries share the layout `{1: 'code', 2: 'name', 3: 'description'}`.

**Shared rendering:**
- `html_utils.py` — `page()` wraps a body string in the full HTML shell with header/nav/styles; `table()` renders a list of rows into a Bootstrap table; `lib_nav()` builds the per-page nav strip.
- All detail pages use `../static` as the asset path (relative to their subdirectory). The `--local` flag sets this; production uses an absolute server path.

## Configuration Files

- **`index_config.json`** — controls which libraries appear on the index page and how they are grouped. Libraries in the policies file but absent here still get pages generated; they just won't be linked from the index.
- **`uprf_library_prefixes.json`** — maps library `lib` abbreviation to the UPRF record name prefix (e.g. `"LARM": "02"`). This is not derivable from the policies file. Libraries absent here get no User Profiles page. `"WYLD": "all"` is the special case consumed by `wyldprofiles.py`.

## Adding a New Generator

Each generator module exports a single `generate(records, lookups, output_root, static_path=None)` function. Call it from `generate.py` after the existing generators. Output goes in a subdirectory of `output_root`. Use `page()` and `table()` from `html_utils.py` for consistent rendering.
