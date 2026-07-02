# Recirculating User Profiles Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a WYLD-only page listing all recirculating (`recirculating == 'Y'`) user profiles, sorted by name, linked from a new card on the WYLD hub page.

**Architecture:** Parse a previously-unused UPRF field into `policy_parser.py`'s schema, add a small new generator module (`recircprofiles.py`) that reuses `userprofile.py`'s table rendering helpers, wire it into `generate.py`, and add a conditional card to `libindex.py` visible only on the WYLD hub page.

**Tech Stack:** Python 3 stdlib only, no test framework or linter in this repo (per `CLAUDE.md`) — verification is done by running `generate.py` against `mock-data/policies` and inspecting the generated HTML output.

## Global Constraints

- No tests, no linter configured in this repo — do not add a test framework; verify by running the generator and inspecting output (per `CLAUDE.md`).
- UPRF schema index for `recirculating` is **5** (`fields[5]`), not 6 — confirmed against `mock-data/policies`: `LIBRARYUSE`/`INTRANSIT` are `Y`, `ADMIN`/`17PA`/`ILL` are `N`. Do not reuse index 6 (`card_life_type`, already mapped).
- `ALL_CODE = "25000"` and WYLD libcode `"115"` are existing sentinel values used elsewhere; the WYLD-only condition for the new card should check `libcode == WYLD_LIBCODE` (already defined as `'115'` in `libindex.py`), matching the existing `Holdcode` card conditional.
- New page must be reachable at `recircprofiles/wyld.html` under the output root, so it fits `libindex.py`'s existing `_policy_card(directory, title, desc, lib_lower)` link-building convention (`../{directory}/{lib_lower}.html`).
- Table columns and formatting must exactly match `userprofile.py`'s existing `HEADERS` / `_profile_row`, reused via import — not reimplemented.

---

### Task 1: Add `recirculating` field to the UPRF schema

**Files:**
- Modify: `policy_parser.py:60-75` (the `SCHEMAS['UPRF']` dict)

**Interfaces:**
- Consumes: nothing new
- Produces: every parsed UPRF record dict now has a `'recirculating'` key holding `'Y'` or `'N'` (raw string from the policies file, no coercion — consistent with how every other flag field in this schema, e.g. `allow_edit_expire`, is left as a raw string).

- [ ] **Step 1: Add the field mapping**

In `policy_parser.py`, inside `SCHEMAS['UPRF']`, add index 5 in numeric order with the other keys:

```python
    'UPRF': {
        1:  'code',
        2:  'name',
        5:  'recirculating',
        6:  'card_life_type',
        7:  'card_life_value',
        8:  'overdue_threshold',
        9:  'bill_threshold',
        10: 'charges_limit',
        27: 'hold_limit',
        28: 'uses_lib_precedence',
        29: 'location_code',
        30: 'user_access_code',
        33: 'description',
        41: 'increment_charge_counter',
        50: 'allow_edit_expire',
    },
```

(Only the `5: 'recirculating',` line is new; every other line is unchanged — this shows the full dict so the insertion point is unambiguous.)

- [ ] **Step 2: Verify the field parses correctly**

Run:
```bash
python3 -c "
from policy_parser import parse_policies
records = parse_policies('mock-data/policies')
uprf = {u['name']: u['recirculating'] for u in records['UPRF']}
print(uprf['LIBRARYUSE'], uprf['INTRANSIT'], uprf['ADMIN'], uprf['17PA'], uprf['ILL'])
"
```
Expected output: `Y Y N N N`

- [ ] **Step 3: Commit**

```bash
git add policy_parser.py
git commit -m "Parse recirculating field on UPRF records"
```

---

### Task 2: Create the `recircprofiles.py` generator module

**Files:**
- Create: `recircprofiles.py`

**Interfaces:**
- Consumes: `userprofile.HEADERS` (list of 11 column-header strings) and `userprofile._profile_row(uprf, locn_lookup)` (returns a list of 11 cell strings for one UPRF record) — both already exist in `userprofile.py`, imported not duplicated. Also consumes `html_utils.page(title, body, date, static_path)` and `html_utils.table(headers, rows)`.
- Produces: `generate(records, lookups, output_root, static_path=None)` — same signature as every other generator module (see `circmap.generate`, `userprofile.generate`). Writes one file: `{output_root}/recircprofiles/wyld.html`.

- [ ] **Step 1: Write the module**

```python
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
```

- [ ] **Step 2: Verify it generates correctly**

Run:
```bash
python3 -c "
from policy_parser import parse_policies, parse_libg, build_lookup
import recircprofiles

records = parse_policies('mock-data/policies')
lookups = {'locn': build_lookup(records, 'LOCN', 'code')}
recircprofiles.generate(records, lookups, '/tmp/recircprofiles-check', static_path='../static')
"
grep -c '<tr>' /tmp/recircprofiles-check/recircprofiles/wyld.html
grep -o '<td>[A-Z0-9_-]*</td>' /tmp/recircprofiles-check/recircprofiles/wyld.html | head -5
```
Expected: a row count matching the 51 names listed in the spec/global-constraints check (`awk -F'|' '$1=="UPRF" && $6=="Y"'` against `mock-data/policies` returns 51 profiles), and the first `<td>` values sorted alphabetically (e.g. `01BKMOB`, `01TELEDISP`, `04DISPLAY1`, ...).

- [ ] **Step 3: Commit**

```bash
git add recircprofiles.py
git commit -m "Add recircprofiles generator for recirculating user profiles"
```

---

### Task 3: Wire `recircprofiles` into `generate.py`

**Files:**
- Modify: `generate.py:9-18` (import block), `generate.py:55-64` (generator call sequence)

**Interfaces:**
- Consumes: `recircprofiles.generate(records, lookups, output_root, static_path)` from Task 2.
- Produces: running `python3 generate.py <policies> <output> [--local]` now also writes `{output}/recircprofiles/wyld.html`.

- [ ] **Step 1: Add the import**

In `generate.py`, in the import block (currently ends `import userprofile`), add `recircprofiles` in alphabetical order with the others:

```python
from policy_parser import parse_policies, parse_libg, build_lookup, POLICIES_FILE
import circmap
import circrule
import defprice
import holdcode
import holdmap
import index_page
import libcircrule
import libindex
import libinfo
import recircprofiles
import userprofile
```

- [ ] **Step 2: Add the generator call**

In `generate.py`'s `main()`, add the call right after `userprofile.generate(...)` and before `libindex.generate(...)` (so `libindex` can assume the page already exists, matching the existing ordering where `userprofile` runs before the hub pages that link to it):

```python
    userprofile.generate(records, lookups, output_root, static_path)
    recircprofiles.generate(records, lookups, output_root, static_path)
    libindex.generate(records, lookups, output_root, static_path)
```

- [ ] **Step 3: Verify the full generator run produces the page**

Run:
```bash
rm -rf /tmp/wyld-plan-check
python3 generate.py mock-data/policies /tmp/wyld-plan-check --local
test -f /tmp/wyld-plan-check/recircprofiles/wyld.html && echo "FOUND"
```
Expected output ends with `Finished successfully` followed by `FOUND`.

- [ ] **Step 4: Commit**

```bash
git add generate.py
git commit -m "Call recircprofiles generator from main pipeline"
```

---

### Task 4: Add the card to the WYLD hub page

**Files:**
- Modify: `libindex.py:18-26` (card tuple constants), `libindex.py:152-159` (card assembly in `generate()`)

**Interfaces:**
- Consumes: `_policy_card(directory, title, desc, lib_lower)` (existing helper in `libindex.py`), the module-level `WYLD_LIBCODE = '115'` constant (already defined at `libindex.py:16`).
- Produces: on the WYLD hub page only (`Libindex/wyld.html`), the policy-card grid includes a card linking to `../recircprofiles/wyld.html`.

- [ ] **Step 1: Add the card constant**

In `libindex.py`, right after the existing `PROFILE_CARD` constant, add:

```python
PROFILE_CARD = ('userprofile', 'User Profiles', 'Patron profile settings and borrowing limits')
RECIRC_CARD = ('recircprofiles', 'Recirculating Profiles', 'User profiles flagged as recirculating')
```

- [ ] **Step 2: Append the card only for the WYLD library**

In `libindex.py`'s `generate()`, the current card-assembly block is:

```python
        cards = [
            _policy_card(d, t, desc, lib_lower)
            for d, t, desc in POLICY_CARDS
            if d != 'Holdcode' or libcode == WYLD_LIBCODE or libcode in libs_with_holdcodes
        ]
        if lib in prefixes:
            d, t, desc = PROFILE_CARD
            cards.append(_policy_card(d, t, desc, lib_lower))
```

Change it to add the new card conditionally on `libcode == WYLD_LIBCODE`:

```python
        cards = [
            _policy_card(d, t, desc, lib_lower)
            for d, t, desc in POLICY_CARDS
            if d != 'Holdcode' or libcode == WYLD_LIBCODE or libcode in libs_with_holdcodes
        ]
        if lib in prefixes:
            d, t, desc = PROFILE_CARD
            cards.append(_policy_card(d, t, desc, lib_lower))
        if libcode == WYLD_LIBCODE:
            d, t, desc = RECIRC_CARD
            cards.append(_policy_card(d, t, desc, lib_lower))
```

- [ ] **Step 3: Verify the card appears only on the WYLD hub page**

Run:
```bash
rm -rf /tmp/wyld-plan-check
python3 generate.py mock-data/policies /tmp/wyld-plan-check --local
grep -c 'recircprofiles/wyld.html' /tmp/wyld-plan-check/Libindex/wyld.html
grep -rl 'recircprofiles/wyld.html' /tmp/wyld-plan-check/Libindex/ | wc -l
```
Expected: first command prints `1` (the card is present on the WYLD hub page), second command prints `1` (it's the *only* hub page containing that link).

- [ ] **Step 4: Commit**

```bash
git add libindex.py
git commit -m "Add Recirculating Profiles card to WYLD hub page"
```

---

### Task 5: End-to-end verification

**Files:** none (verification only)

- [ ] **Step 1: Full regeneration and manual spot-check**

```bash
rm -rf /tmp/wyld-test
python3 generate.py mock-data/policies /tmp/wyld-test --local
python3 -m http.server 8080 --directory /tmp/wyld-test --bind 0.0.0.0 &
```

Open `http://localhost:8080/Libindex/wyld.html` in a browser, confirm the "Recirculating Profiles" card is present and click through to `http://localhost:8080/recircprofiles/wyld.html`. Confirm the table lists 51 profiles sorted alphabetically by name (first row `01BKMOB`, matching the `awk` check from Task 2), with the same 11 columns as the existing User Profiles page.

Then stop the server:
```bash
kill %1
```

- [ ] **Step 2: Confirm no regressions in existing pages**

Check out the pre-change revision into a throwaway worktree, generate from it, and diff the file listing against the post-change output (excluding the new `recircprofiles` directory, which is expected to only exist post-change):

```bash
git worktree add /tmp/wyld-before-wt HEAD~4
python3 /tmp/wyld-before-wt/generate.py mock-data/policies /tmp/wyld-before --local
diff <(find /tmp/wyld-before -type f | sed 's|/tmp/wyld-before||' | sort) \
     <(find /tmp/wyld-test -type f | sed 's|/tmp/wyld-test||' | grep -v '^/recircprofiles/' | sort)
git worktree remove /tmp/wyld-before-wt
```

Expected: no diff output (empty) — every file present before this change is still present and unchanged in location after it, aside from the new `recircprofiles` directory.
