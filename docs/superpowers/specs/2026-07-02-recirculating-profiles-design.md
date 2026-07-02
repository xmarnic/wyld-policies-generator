# Recirculating User Profiles Page

## Problem

There's no page listing which user profiles (UPRF records) are flagged as
recirculating. This flag lives in the policies file but isn't currently
parsed or surfaced anywhere in the generated site.

## Field mapping

UPRF field 6 as counted by `cut -d'|' -f6` (1-indexed, counting the `UPRF`
record-type token as field 1) corresponds to Python list index 5 in
`policy_parser.py`, since `SCHEMAS` indexes directly into
`line.split('|')` where `fields[0]` is the record type itself. Verified
against mock data: `fields[5]` is `Y` for `LIBRARYUSE` and `INTRANSIT`
(profiles that plausibly recirculate) and `N` for `ADMIN`, `17PA`, `ILL`
(patron/admin/ILL profiles). Field index 6 is already mapped to
`card_life_type` and holds unrelated data.

Add to `SCHEMAS['UPRF']` in `policy_parser.py`:
```python
5: 'recirculating',
```

## Scope

User profiles are not owned by an individual library — the recirculating
flag is a system-wide attribute — so this is a single global report, not
a per-library page. It follows the precedent set by `circmap.py`'s
"Complete Circ Map Policy" page for the WYLD-wide library (libcode
`115`): one page, linked only from the WYLD hub page.

## Implementation

**New module `recircprofiles.py`**, following the standard generator
convention (`generate(records, lookups, output_root, static_path=None)`):

- Filter `records['UPRF']` to records where `recirculating == 'Y'`.
- Sort the filtered list by `name`.
- Reuse `HEADERS` and `_profile_row` from `userprofile.py` (import, don't
  duplicate) so the table columns exactly match the existing User
  Profiles page.
- Render via `page()` and `table()` from `html_utils.py`, consistent with
  every other generator.
- Write a single file to `recircprofiles/wyld.html`. Using the `wyld.html`
  filename (rather than e.g. `index.html`) keeps it compatible with
  `libindex.py`'s `_policy_card(directory, title, desc, lib_lower)`
  helper, which builds links as `../{directory}/{lib_lower}.html`.
- Page title: "Recirculating User Profiles".

**Wiring:**

- `generate.py`: import `recircprofiles` and call
  `recircprofiles.generate(records, lookups, output_root, static_path)`
  alongside the other generator calls.
- `libindex.py`: add a new card tuple and append it to `cards` only when
  `libcode == WYLD_LIBCODE`, mirroring the existing conditional pattern
  used for the `Holdcode` card. Directory: `recircprofiles`. Title:
  "Recirculating Profiles". Description: "User profiles flagged as
  recirculating".

## Out of scope

- No per-library filtering or card on non-WYLD hub pages.
- No changes to the existing User Profiles page or its columns.
