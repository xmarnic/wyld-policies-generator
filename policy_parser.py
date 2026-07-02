POLICIES_FILE = "/software/WYLD/Unicorn/Config/policies"
LIBG_FILE = "/software/WYLD/Unicorn/Config/libg.pol"

ALL_CODE = "25000"

# Maps field index to named key for each record type we use.
# Only fields documented as used in the application are included.
SCHEMAS = {
    'LIBR': {
        1:  'libcode',
        2:  'lib',
        3:  'user_id',
        6:  'fixed_due_date_code',
        7:  'accrue_fines_closed',
        8:  'closed_date_starts',
        9:  'hold_location_code',
        12: 'closed_sun',
        13: 'closed_mon',
        14: 'closed_tue',
        15: 'closed_wed',
        16: 'closed_thu',
        17: 'closed_fri',
        18: 'closed_sat',
        20: 'closed_date_ends',
        21: 'name',
        23: 'acq_display_libs',
        24: 'acq_maint_libs',
        25: 'hold_perm_group',
        26: 'hold_group',
        28: 'serials_display_libs',
        29: 'serials_maint_libs',
        38: 'hold_avail_libs',
        40: 'skip_onshelf_holds_closed',
        42: 'callnum_maint_group',
        43: 'item_maint_group',
        44: 'marc_maint_group',
        45: 'hold_expire_days',
        46: 'avail_hold_expire_days',
        47: 'oclc_code',
    },
    'CMAP': {
        1: 'sequence',
        2: 'name',
        3: 'library_codes',
        4: 'patron_profile_codes',
        5: 'item_type_codes',
        6: 'circ_rule_code',
        7: 'description',
    },
    'HMAP': {
        1: 'sequence',
        2: 'name',
        3: 'description',
        4: 'library_codes',
        5: 'item_type_codes',
        6: 'user_profile_codes',
        7: 'permission',
        8: 'priority',
    },
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
    'ITYP': {
        1:  'code',
        2:  'name',
        5:  'hold_threshold',
        8:  'description',
        12: 'saleable',
    },
    'CIRC': {
        1:  'code',
        2:  'name',
        3:  'loan_period_code',
        4:  'bill_structure_code',
        5:  'renew_limit',
        6:  'chargeable',
        7:  'grace_period',
        8:  'recall_due',
        9:  'period_unit',
        10: 'overdue_flag',
        11: 'description',
        12: 'recall_loan_period_code',
        13: 'alt_loan_period_code',
        14: 'max_loan',
    },
    'LOCN': {
        1: 'code',
        2: 'name',
        3: 'available_flag',
        5: 'holdable_flag',
        6: 'description',
        9: 'available_flag2',
    },
    'LPRD': {
        1: 'code',
        2: 'name',
    },
    'BSTR': {
        1: 'code',
        2: 'name',
    },
    'DEFP': {
        1:  'sequence',
        2:  'name',
        3:  'description',
        4:  'item_type_code',
        5:  'library_code',
        6:  'processing_fee',
        7:  'default_price',
        8:  'remove_profee',
        9:  'use_default_always',
        10: 'auto_refund',
        12: 'deduct_overdue_fine',
    },
    'HLDC': {
        1:  'sequence',
        2:  'name',
        4:  'library_code',
        5:  'location_code',
        6:  'item_type_code',
        13: 'description',
    },
}

# Fields whose values are comma-separated lists of codes.
COMMA_FIELDS = {
    'CMAP': {'library_codes', 'patron_profile_codes', 'item_type_codes'},
    'HMAP': {'library_codes', 'item_type_codes', 'user_profile_codes'},
}



def _fields_to_record(record_type, fields):
    schema = SCHEMAS[record_type]
    comma_fields = COMMA_FIELDS.get(record_type, set())
    record = {}
    for idx, name in schema.items():
        value = fields[idx] if idx < len(fields) else ''
        if name in comma_fields:
            value = [v for v in value.split(',') if v]
        record[name] = value
    return record


def parse_policies(path):
    """Read the policies file once and return all known record types as named dicts.

    Returns a dict of record_type -> list of records, where each record is a
    dict of named fields as defined in SCHEMAS. The file is opened read-only.
    Record types not in SCHEMAS are ignored.
    """
    records = {rtype: [] for rtype in SCHEMAS}
    with open(path, 'r') as f:
        for line in f:
            fields = line.rstrip('\n').split('|')
            record_type = fields[0]
            if record_type not in SCHEMAS:
                continue
            records[record_type].append(_fields_to_record(record_type, fields))
    return records


def build_lookup(records, record_type, key_field):
    """Build a dict mapping key_field -> record for O(1) lookups.

    Example: circ_lookup = build_lookup(records, 'CIRC', 'code')
             circ_lookup['251']['name']
    """
    return {r[key_field]: r for r in records.get(record_type, [])}



def parse_libg(path=LIBG_FILE):
    """Parse libg.pol and return a dict mapping group ID -> short code."""
    libg = {}
    with open(path, 'r') as f:
        for line in f:
            fields = line.rstrip('\n').split('|')
            if fields[0] == 'LIBG' and len(fields) > 2:
                libg[fields[1]] = fields[2]
    return libg


if __name__ == "__main__":
    records = parse_policies(POLICIES_FILE)
    for rtype, rlist in records.items():
        print(f"{rtype}: {len(rlist)} records")
