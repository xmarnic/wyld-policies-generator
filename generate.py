#!/usr/bin/env python3
"""Main entry point. Parses the policies file once and runs all generators."""

import os
import sys

from policy_parser import parse_policies, build_lookup, POLICIES_FILE
import circmap
import circrule
import defprice
import holdcode
import holdmap
import index_page
import libcircrule
import libindex
import libinfo
import userprofile

OUTPUT_ROOT = "/software/apache/WYLD/htdocs/new-map"


def build_lookups(records):
    return {
        'circ':  build_lookup(records, 'CIRC', 'code'),
        'uprf':  build_lookup(records, 'UPRF', 'code'),
        'ityp':  build_lookup(records, 'ITYP', 'code'),
        'locn':  build_lookup(records, 'LOCN', 'code'),
        'lprd':  build_lookup(records, 'LPRD', 'code'),
        'bstr':  build_lookup(records, 'BSTR', 'code'),
        'libr':  build_lookup(records, 'LIBR', 'libcode'),
    }


def main(policies_path=POLICIES_FILE, output_root=OUTPUT_ROOT, local=False):
    print(f"Parsing {policies_path}...")
    records = parse_policies(policies_path)
    lookups = build_lookups(records)

    os.makedirs(output_root, exist_ok=True)

    static_path = None
    if local:
        import shutil
        static_src = os.path.join(os.path.dirname(__file__), 'static')
        static_dst = os.path.join(output_root, 'static')
        shutil.copytree(static_src, static_dst, dirs_exist_ok=True)
        static_path = '../static'

    circmap.generate(records, lookups, output_root, static_path)
    circrule.generate(records, lookups, output_root, static_path)
    holdmap.generate(records, lookups, output_root, static_path)
    holdcode.generate(records, lookups, output_root, static_path)
    defprice.generate(records, lookups, output_root, static_path)
    libinfo.generate(records, lookups, output_root, static_path)
    libcircrule.generate(records, lookups, output_root, static_path)
    userprofile.generate(records, lookups, output_root, static_path)
    libindex.generate(records, lookups, output_root, static_path)
    index_page.generate(records, lookups, output_root, './static' if local else None)

    print("Done.")


if __name__ == "__main__":
    args = sys.argv[1:]
    local = '--local' in args
    args = [a for a in args if a != '--local']
    policies = args[0] if len(args) > 0 else POLICIES_FILE
    output = args[1] if len(args) > 1 else OUTPUT_ROOT
    main(policies, output, local)
