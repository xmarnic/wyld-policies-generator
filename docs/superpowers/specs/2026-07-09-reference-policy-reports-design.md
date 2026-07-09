# Item/Location/Category Reference Policy Reports

## Problem

Four reference record types from Unicorn/Symphony aren't surfaced anywhere
in the generated site: item type policies (`ITYP`), location policies
(`LOCN`), item category policies (`ICT1`-`ICT10`), and user category
policies (`CAT1`-`CAT10`). None of these are library-scoped — they're
system-wide reference data — so they belong as WYLD-only admin reports,
following the precedent already established by `wyldprofiles.py` for the
recirculating/library-use profile pages.

## Field mapping

`ITYP` and `LOCN` are already mapped in `policy_parser.py`'s `SCHEMAS`
(`ITYP`: code=1, name=2, description=8; `LOCN`: code=1, name=2,
description=6) — no parser changes needed for these two.

Item categories (`ICT1`-`ICT5`) and user categories (`CAT1`-`CAT10`, per
mock data currently populated through `CAT6`, with `CAT11`/`CAT12`
present but out of scope) share one simple layout, verified against
`mock-data/ucat.pol` and `mock-data/ictx.pol`:

```
CAT1|2|OUTREACH|Outreach User|
ICT6|1|AV|AV|
```

`fields[1]` = code, `fields[2]` = short-code/name, `fields[3]` =
description. Add to `SCHEMAS` in `policy_parser.py`:

```python
for n in range(1, 11):
    SCHEMAS[f'ICT{n}'] = {1: 'code', 2: 'name', 3: 'description'}
    SCHEMAS[f'CAT{n}'] = {1: 'code', 2: 'name', 3: 'description'}
```

(User categories are extended to `CAT1`-`CAT10`, beyond the currently
populated range, to keep the numbering symmetric with item categories and
cover data that doesn't exist in the mock snapshot but may in production.)

**File sources differ per record family:**

- `ITYP`, `LOCN`, `ICT1`-`ICT5` — parsed from the main `policies` file via
  the existing `parse_policies`, since their record types are already (or
  will be) present in `SCHEMAS`.
- `ICT6`-`ICT10` — parsed from `ictx.pol`, a sibling file to `policies`
  (same directory), not currently read by the generator.
- `CAT1`-`CAT10` — parsed from `ucat.pol`, another sibling file. All user
  category data comes from this one file; there is no split like `ICT`
  has (confirmed with user — unlike item categories, user categories are
  not divided across two files).

Add a generic aux-file parser to `policy_parser.py`, alongside the
existing `parse_libg`:

```python
def parse_aux_file(path, record_types):
    """Parse an arbitrary policies-formatted file, keeping only record_types."""
    records = {rtype: [] for rtype in record_types}
    with open(path, 'r') as f:
        for line in f:
            fields = line.rstrip('\n').split('|')
            rtype = fields[0]
            if rtype not in record_types:
                continue
            records[rtype].append(_fields_to_record(rtype, fields))
    return records
```

## Scope

WYLD-wide only, no per-library pages or filtering — same rationale as
`wyldprofiles.py`. Cards for these four reports appear only on the WYLD
hub page (`libcode == WYLD_LIBCODE` in `libindex.py`); no other
per-library page changes.

## Implementation

**`generate.py`:**

- After parsing the main `policies` file, also parse `ictx.pol` and
  `ucat.pol` (same directory as `policies`, same pattern already used for
  `libg.pol`):
  ```python
  ictx_path = os.path.join(os.path.dirname(policies_path), 'ictx.pol')
  ucat_path = os.path.join(os.path.dirname(policies_path), 'ucat.pol')
  ict_extra = parse_aux_file(ictx_path, [f'ICT{n}' for n in range(6, 11)])
  ucat = parse_aux_file(ucat_path, [f'CAT{n}' for n in range(1, 11)])
  ```
- Merge into `records` so downstream generators can treat all ten numbers
  uniformly regardless of source file:
  ```python
  for n in range(6, 11):
      records[f'ICT{n}'] = ict_extra[f'ICT{n}']
  for n in range(1, 11):
      records[f'CAT{n}'] = ucat[f'CAT{n}']
  ```

**`wyldprofiles.py`** (extended, not a new module — these are WYLD-wide
admin reports just like the existing UPRF-derived ones; docstring
broadened beyond "derived from UPRF"):

Two new helpers alongside the existing `_write_profiles_page`:

- `_write_flat_report(rows, heading, title, out_dir, static_path)` — for
  `ITYP` and `LOCN`. Two-column table (`SHORT-CODE`, `DESCRIPTION`), rows
  sorted by name.
- `_write_sectioned_report(records_by_number, label, heading, title,
  out_dir, static_path)` — for item/user categories. For each number 1-10
  with at least one record, render a subheading (e.g. "Item Category 3")
  followed by a two-column table (`SHORT-CODE`, `DESCRIPTION`) sorted by
  name. Numbers with no records are skipped entirely (no empty section,
  no placeholder row).

New pages, all written as `wyld.html` in their own output directory (matches
the existing `../{directory}/{lib_lower}.html` link convention used by
`libindex.py`'s `_policy_card`):

| Directory       | Title                     | Source                              |
|-----------------|---------------------------|--------------------------------------|
| `itemtype`      | Item Type Policies        | `records['ITYP']`                    |
| `location`      | Location Policies         | `records['LOCN']`                    |
| `itemcategory`  | Item Category Policies    | `records['ICT1']` .. `records['ICT10']` |
| `usercategory`  | User Category Policies    | `records['CAT1']` .. `records['CAT10']` |

`generate()` in `wyldprofiles.py` gains four calls building these pages
after the existing three UPRF-derived ones.

**`libindex.py`:**

Four new card tuples (`ITEMTYPE_CARD`, `LOCATION_CARD`,
`ITEMCATEGORY_CARD`, `USERCATEGORY_CARD`), appended to `cards` only when
`libcode == WYLD_LIBCODE`, same conditional block as `RECIRC_CARD`/
`LIBRARY_USE_CARD`.

## Out of scope

- No per-library pages, filtering, or cards for any of the four report
  types.
- No changes to existing pages (`ITYP`/`LOCN` continue to be used
  elsewhere, e.g. `holdcode.py`, unaffected by this work).
- `CAT11`, `CAT12`, and any other non-numeric-suffix `CAT`/`ICT` record
  types remain unparsed and out of scope.
