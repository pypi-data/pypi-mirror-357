"""Convert hierarchical tree node names to ICAT field names.

ICAT field names use CamelCase for parent/group levels and snake_case for leaf fields.
The helpers functions in this module build full ICAT field names from the NeXus tree
structure following that convention.
"""

import re


def icat_field_prefix(parent_prefix: str, group_name: str):
    """Add another group in the tree to the ICAT field name prefix."""
    if not group_name:
        return parent_prefix
    parts = group_name.split("_")
    if all(parts):
        parts = [s[0].upper() + s[1:] for s in parts]
        group_prefix = "".join(parts)
    else:
        group_prefix = re.sub("_+", "_", group_name)
    return f"{parent_prefix}{group_prefix}"


def icat_field_name(parent_prefix: str, short_icat_name: str):
    """Add the short ICAT name (i.e. relative to the parent in the tree)
    to the parent prefix."""
    if parent_prefix:
        icat_name = f"{parent_prefix}_{short_icat_name}"
    else:
        icat_name = short_icat_name
    return _CONSISTENT_TO_INCONSISTENT.get(icat_name, icat_name)


# Some ICAT field names were not consistent in the original XML file.
# Map consistent to (original) inconsistent names.
_CONSISTENT_TO_INCONSISTENT = {
    "SAXS_definition": "saxs_definition",
    "SAXS_definition.version": "saxs_definition.version",
    "FLUOMeasurement_i0_end": "TOMO_i0_end",
    "FLUOMeasurement_i0_start": "TOMO_i0_start",
    "FLUOMeasurement_it_end": "TOMO_it_end",
    "FLUOMeasurement_it_start": "TOMO_it_start",
    "FLUOMeasurement_current_end": "InstrumentSource_current_end",
    "FLUOMeasurement_current_start": "Source_current_start",
    "Instrument_beamlineID": "beamlineID",
    "WAXS_definition": "xrf_definition",
}
