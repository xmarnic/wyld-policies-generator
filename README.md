# WYLD Policy Map

Static HTML generator for the WYLD consortium's SirsiDynix Symphony ILS policy pages. Parses the Symphony `policies` flat file and produces one navigable HTML site covering circulation maps, hold maps, circ rules, holding codes, default prices, user profiles, and library info — one set of pages per library.

## Usage

```bash
python3 generate.py [policies_file] [output_dir] [--local]
```

| Argument | Default | Description |
|---|---|---|
| `policies_file` | `/software/WYLD/Symphony/Config/policies` | Path to the Symphony policies flat file |
| `output_dir` | `/software/apache/WYLD/htdocs/new-map` | Root directory for generated HTML |
| `--local` | off | Copy Bootstrap assets into `output_dir/static/` and use relative paths (for local development) |

**Development example:**
```bash
python3 generate.py ../policies /tmp/wyld-test --local
python3 -m http.server 8080 --directory /tmp/wyld-test --bind 0.0.0.0
```

## Generated Output

```
output_dir/
  index.html              # Landing page — all libraries by category
  static/                 # Bootstrap assets (--local only)
  Libindex/{lib}.html     # Library hub page (info + links to all policy pages)
  Circmap/{lib}.html      # Circulation map for the library
  Circrules/{code}.html   # One page per circ rule (named by numeric policy code)
  Circrule/{lib}.html     # Circ rules used by the library
  Holdmap/{lib}.html      # Hold map for the library
  Holdcode/{lib}.html     # Holding codes for the library
  Defprice/{lib}.html     # Default replacement prices for the library
  userprofile/{lib}.html  # User/patron profiles for the library
  Libinfo/{lib}.html      # Library configuration details
```

All filenames use the lowercase library abbreviation (e.g., `larm.html`, `wyld.html`).

## Configuration Files

### `index_config.json`
Controls the index page layout. Defines the standalone "All WYLD Policies" link and the four columns (Public Libraries, K-12 Schools, Academic, Special Libraries), with county/district groupings within each column. **This is the only place that controls which libraries appear on the index page.** Libraries present in the policies file but absent from this config will still have pages generated — they just won't be linked from the index.

### `uprf_library_prefixes.json`
Maps each library abbreviation to the name prefix used by its UPRF (user profile) records in the policies file (e.g., `"LARM": "02"`). This mapping is not derivable from the policies file itself — it reflects a naming convention embedded in UPRF record names. Libraries not listed here will not get a User Profiles page.

## Architecture

`generate.py` is the entry point. It parses the policies file once via `policy_parser.py`, builds lookup dicts for all referenced record types, then calls each generator module in sequence. All generators share the same `records` and `lookups` dicts and write independently to the output directory.

`html_utils.py` provides the shared `page()` wrapper and `table()` renderer used by all detail page generators.

The policies file is a `|`-delimited flat file. `policy_parser.py` defines field index mappings (`SCHEMAS`) for each record type used. Fields not listed in the schema are silently ignored.

## Adding a New Library to the Index

1. Confirm the library's `lib` abbreviation from the policies file (e.g., `grep '^LIBR|' policies | cut -d'|' -f3`)
2. Add the library to the appropriate group in `index_config.json`
3. If the library has user profiles, add its UPRF prefix to `uprf_library_prefixes.json`
4. Regenerate
