"""Base model to represent ICAT schema's."""

import pathlib
from copy import deepcopy
from typing import Any
from typing import Dict
from typing import Generator
from typing import List
from typing import Tuple
from typing import Union

import pint
from pydantic import BaseModel
from pydantic import model_validator

try:
    import xmltodict
except ImportError:
    xmltodict = None

from . import icat
from . import utils

_ALLOWED_EXTRA_KEYS = {"icat_name", "record"}
_ALLOWED_RECORD_VALUES = {"initial", "final"}


class IcatBaseModel(BaseModel, extra="forbid", validate_assignment=True):
    """Base model for ICAT dataset metadata.

    Model instances (i.e. includes values) can be converted to and from
    the following python dictionaries:

    - ICAT: flat dictionary with ICAT database key-value pairs.
    - HDF5: nested dictionary with Nexus groups, fields and attributes
            following the Silx dictdump schema.

    Numeric fields with units or unit dimensions are supported.

    Model classes (i.e. no values) can be converted to the following
    schema's

    - XML: original (non-defined) ICAT dataset metadata XDS schema.
    - Any schema supported by Pydantic like JSON schema.
    """

    @classmethod
    def __pydantic_init_subclass__(cls, *args, **kwargs) -> Any:
        """Validate the JSON extra keys of all fields."""
        result = super().__pydantic_init_subclass__(*args, **kwargs)
        for field_name, field_info in cls.model_fields.items():
            extras: Dict[str, Any] = field_info.json_schema_extra or {}

            unknown_keys = set(extras) - _ALLOWED_EXTRA_KEYS
            if unknown_keys:
                raise ValueError(
                    f"Field '{field_name}' in '{cls.__name__}' contains invalid json_schema_extra keys: {unknown_keys}. "
                    f"Allowed keys are: {_ALLOWED_EXTRA_KEYS}"
                )

            if "record" in extras:
                record_value = extras["record"]
                if record_value not in _ALLOWED_RECORD_VALUES:
                    raise ValueError(
                        f"Field '{field_name}' in '{cls.__name__}' has invalid 'record' value: {record_value}. "
                        f"Allowed values are: {_ALLOWED_RECORD_VALUES}"
                    )

        return result

    @model_validator(mode="before")
    @classmethod
    def parse_hdf5_style_units(cls, data: Any) -> Any:
        """
        Looks for HDF5-style quantity definitions (e.g., 'beamSize' and 'beamSize@units')
        in the input data and converts them into a format PydanticQuantity understands
        (e.g., {'beamSize': [magnitude, unit_str]}) before field validation.
        """
        if not isinstance(data, dict):
            return data

        modified_data = data.copy()
        keys_to_remove = set()

        for field_name, field_info in cls.model_fields.items():
            quantity_type = utils.get_field_type(field_info.annotation, pint.Quantity)
            if not quantity_type:
                continue

            # Field, attribute or group alias
            alias = field_info.alias or field_name
            units_key = f"{alias}@units"
            if alias in modified_data and units_key in modified_data:
                magnitude = modified_data[alias]
                unit_or_dimension = modified_data[units_key]
                modified_data[alias] = [magnitude, unit_or_dimension]
                keys_to_remove.add(units_key)

        for key in keys_to_remove:
            del modified_data[key]

        return modified_data

    @classmethod
    def icat_field_names(cls, parent_prefix: str = "") -> List[str]:
        return list(cls._iter_icat_names(parent_prefix))

    @classmethod
    def icat_fields(
        cls, parent_prefix: str = "", parent_nexus_nodes=()
    ) -> Dict[str, utils.IcatFieldInfo]:
        return {
            info.icat_name: info
            for info in cls._iter_icat_field_info(parent_prefix, parent_nexus_nodes)
        }

    def to_icat_dict(self, parent_prefix: str = "") -> Dict[str, Any]:
        return self._to_icat_dict(parent_prefix)

    @classmethod
    def from_icat_dict(
        cls, icat_data: Dict[str, Any], parent_prefix: str = ""
    ) -> "IcatBaseModel":
        model_data = cls._from_icat_dict(icat_data, parent_prefix)
        return cls(**model_data)

    @classmethod
    def to_xml_dict(
        cls, group_name: str = "${entry}", parent_prefix: str = ""
    ) -> Dict[str, Any]:
        return cls._to_xml_dict(group_name, parent_prefix)

    @classmethod
    def to_xml_file(
        cls,
        xml_file: Union[str, bytes, pathlib.Path],
        group_name: str = "${entry}",
        parent_prefix: str = "",
    ) -> None:
        with open(xml_file, mode="w", encoding="utf-8") as fh:
            fh.write(
                cls.to_xml_string(group_name=group_name, parent_prefix=parent_prefix)
            )

    @classmethod
    def to_xml_string(
        cls, group_name: str = "${entry}", parent_prefix: str = ""
    ) -> str:
        xml_dict = cls.to_xml_dict(group_name=group_name, parent_prefix=parent_prefix)
        return cls._xml_dict_to_string(xml_dict)

    def to_hdf5_dict(self) -> Dict[str, Any]:
        return self._to_hdf5_dict()

    @classmethod
    def from_hdf5_dict(cls, hdf5_data: Dict[str, Any]) -> "IcatBaseModel":
        return cls(**hdf5_data)

    def _to_icat_dict(self, parent_prefix: str) -> Dict[str, Any]:
        icat_data = dict()
        dump_field_names = set()
        alias_to_icat_short_name = dict()
        for field_name, field_info in type(self).model_fields.items():
            # Field or group alias
            alias = field_info.alias or field_name
            if alias.startswith("@"):
                continue

            # ICAT field name with respect to parent group
            if field_info.json_schema_extra:
                short_icat_name = field_info.json_schema_extra.get("icat_name", alias)
            else:
                short_icat_name = alias
            alias_to_icat_short_name[alias] = short_icat_name

            value = getattr(self, field_name)
            if isinstance(value, IcatBaseModel):
                # Dump group
                field_prefix = icat.icat_field_prefix(parent_prefix, short_icat_name)
                icat_data.update(value._to_icat_dict(field_prefix))
                continue

            # Dump field later
            dump_field_names.add(field_name)

        # Dump fields
        fields = self.model_dump(
            exclude_unset=True, by_alias=True, mode="json", include=dump_field_names
        )
        icat_data.update(
            {
                icat.icat_field_name(parent_prefix, short_icat_name): value
                for short_icat_name, value in fields.items()
            }
        )

        # Ensure keys are ICAT names
        icat_data = {
            alias_to_icat_short_name.get(alias, alias): value
            for alias, value in icat_data.items()
        }

        return icat_data

    @classmethod
    def _from_icat_dict(
        cls, icat_data: Dict[str, Any], parent_prefix: str, _top: bool = True
    ) -> dict:
        result = dict()
        if _top:
            icat_data = deepcopy(icat_data)
        for field_name, field_info in cls.model_fields.items():
            # Field or group alias
            alias = field_info.alias or field_name
            if alias.startswith("@"):
                continue

            # ICAT field name with respect to parent group
            if field_info.json_schema_extra:
                short_icat_name = field_info.json_schema_extra.get("icat_name", alias)
            else:
                short_icat_name = alias

            # Load group
            group_model = utils.get_field_type(field_info.annotation, IcatBaseModel)
            if group_model:
                field_prefix = icat.icat_field_prefix(parent_prefix, short_icat_name)
                subdata = group_model._from_icat_dict(
                    icat_data, field_prefix, _top=False
                )
                if subdata:
                    result[alias] = subdata
                continue

            # Pop field value
            icat_name = icat.icat_field_name(parent_prefix, short_icat_name)
            if icat_name in icat_data:
                result[alias] = icat_data.pop(icat_name)

        # Field values which are not popped are invalid.
        if _top and icat_data:
            raise ValueError(f"Unknown ICAT fields {list(icat_data)}")

        return result

    @classmethod
    def _iter_icat_names(cls, parent_prefix: str) -> Generator[str, None, None]:
        for field_name, field_info in cls.model_fields.items():
            # Field or group alias
            alias = field_info.alias or field_name
            if alias.startswith("@"):
                continue

            # ICAT field name with respect to parent group
            if field_info.json_schema_extra:
                short_icat_name = field_info.json_schema_extra.get("icat_name", alias)
            else:
                short_icat_name = alias

            # Traverse group
            group_model = utils.get_field_type(field_info.annotation, IcatBaseModel)
            if group_model:
                field_prefix = icat.icat_field_prefix(parent_prefix, short_icat_name)
                yield from group_model._iter_icat_names(field_prefix)
                continue

            # Full ICAT field name
            icat_name = icat.icat_field_name(parent_prefix, short_icat_name)
            yield icat_name

    @classmethod
    def _iter_icat_field_info(
        cls, parent_prefix: str, parent_nexus_nodes: Tuple[str, ...]
    ) -> Generator[utils.IcatFieldInfo, None, None]:
        for field_name, field_info in cls.model_fields.items():
            # Field or group alias
            alias = field_info.alias or field_name
            if alias.startswith("@"):
                continue

            # ICAT field name with respect to parent group
            if field_info.json_schema_extra:
                short_icat_name = field_info.json_schema_extra.get("icat_name", alias)
            else:
                short_icat_name = alias

            nexus_nodes = parent_nexus_nodes + (field_name,)

            # Traverse group
            group_model = utils.get_field_type(field_info.annotation, IcatBaseModel)
            if group_model:
                field_prefix = icat.icat_field_prefix(parent_prefix, short_icat_name)
                yield from group_model._iter_icat_field_info(field_prefix, nexus_nodes)
                continue

            # Field info
            icat_name = icat.icat_field_name(parent_prefix, short_icat_name)

            unit_info, value_type = utils.get_units_and_type(field_info.annotation)
            if unit_info is None:
                nexus_type = utils.nxapitype_from_annotation(field_info.annotation)
                value_type = utils.value_type_from_annotation(field_info.annotation)
            else:
                nexus_type = utils.nxapitype_from_type(value_type)

            if field_info.json_schema_extra:
                record = field_info.json_schema_extra.get("record", None)
            else:
                record = None

            yield utils.IcatFieldInfo(
                icat_name=icat_name,
                nexus_nodes=nexus_nodes,
                description=field_info.description or "",
                required=field_info.is_required(),
                unit_info=unit_info,
                nexus_type=nexus_type,
                value_type=value_type,
                record=record,
            )

    @classmethod
    def _to_xml_dict(cls, group_name: str, parent_prefix: str) -> Dict[str, Any]:
        xml_group_data = {"@groupName": group_name}
        groups = list()
        for field_name, field_info in cls.model_fields.items():
            # Field, attribute or group alias
            alias = field_info.alias or field_name

            # Store attribute
            if alias.startswith("@"):
                xml_group_data[alias] = field_info.default
                continue

            # ICAT field name with respect to parent group
            if field_info.json_schema_extra:
                short_icat_name = field_info.json_schema_extra.get("icat_name", alias)
            else:
                short_icat_name = alias

            # Store group
            group_model = utils.get_field_type(field_info.annotation, IcatBaseModel)
            if group_model:
                field_prefix = icat.icat_field_prefix(parent_prefix, short_icat_name)
                group_attrs = group_model._to_xml_dict(alias, field_prefix)

                if field_info.description is not None:
                    group_attrs["@ESRF_description"] = field_info.description

                groups.append(group_attrs)
                continue

            # Store field
            field_attrs = dict()
            if field_info.is_required():
                field_attrs["@ESRF_mandatory"] = "Mandatory"

            if field_info.description is not None:
                field_attrs["@ESRF_description"] = field_info.description

            unit_info, value_type = utils.get_units_and_type(field_info.annotation)
            if unit_info is None:
                field_attrs["@NAPItype"] = utils.nxapitype_from_annotation(
                    field_info.annotation
                )
            else:
                field_attrs["@units"] = unit_info.as_str_xml()
                field_attrs["@NAPItype"] = utils.nxapitype_from_type(value_type)

            if field_info.json_schema_extra:
                for k, v in field_info.json_schema_extra.items():
                    if k == "icat_name" or v is None:
                        continue
                    field_attrs[f"@{k}"] = v

            icat_name = icat.icat_field_name(parent_prefix, short_icat_name)
            field_attrs["#text"] = f"${{{icat_name}}}"
            xml_group_data[field_name] = field_attrs

        # Copy groups
        if groups:
            if len(groups) == 1:
                xml_group_data["group"] = groups[0]
            else:
                xml_group_data["group"] = groups

        return xml_group_data

    @classmethod
    def _xml_string_to_dict(cls, xml_string: str) -> dict:
        if xmltodict is None:
            raise RuntimeError("Requires 'xmltodict'")
        data = xmltodict.parse(xml_string)[cls.__name__]
        if data is None:
            return dict()
        return data

    @classmethod
    def _xml_dict_to_string(cls, xml_dict: dict) -> str:
        if xmltodict is None:
            raise RuntimeError("Requires 'xmltodict'")
        return xmltodict.unparse({"group": xml_dict}, pretty=True, indent=4)

    def _to_hdf5_dict(self) -> Dict[str, Any]:
        hdf5_data = dict()
        dump_field_names = set()
        for field_name, field_info in type(self).model_fields.items():
            # Field, attribute or group alias
            alias = field_info.alias or field_name

            value = getattr(self, field_name)
            if isinstance(value, pint.Quantity):
                # Dump pint Quantity
                units_key = f"{alias}@units"
                hdf5_data[alias] = value.magnitude
                hdf5_data[units_key] = str(value.units)
            elif isinstance(value, IcatBaseModel):
                # Dump group
                hdf5_data[alias] = value.to_hdf5_dict()
            else:
                # Dump field later
                dump_field_names.add(field_name)

        # Dump fields
        fields = self.model_dump(
            exclude_none=True, by_alias=True, mode="json", include=dump_field_names
        )
        hdf5_data.update(fields)

        return hdf5_data
