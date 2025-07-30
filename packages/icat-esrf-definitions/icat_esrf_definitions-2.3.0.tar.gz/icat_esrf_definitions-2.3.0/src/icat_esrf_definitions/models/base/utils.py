import datetime
from typing import Any
from typing import Literal
from typing import NamedTuple
from typing import Optional
from typing import Tuple
from typing import Type
from typing import Union

try:
    from typing import Annotated
    from typing import get_args
    from typing import get_origin
except ImportError:
    # For Python <3.9
    from typing_extensions import Annotated, get_args, get_origin

from . import units as units_module


class UnitInfo(NamedTuple):
    dimension: units_module.UnitsContainer
    units: Optional[units_module.Unit]

    def __str__(self) -> str:
        if self.units is None:
            return str(self.dimension)
        return f"{self.units:~}"

    def as_str_xml(self) -> str:
        if self.units is None:
            return str(self.dimension)
        return f"{self.units:~P}"


class IcatFieldInfo(NamedTuple):
    icat_name: str
    nexus_nodes: Tuple[str, ...]
    description: str
    required: bool
    unit_info: Optional[UnitInfo]
    nexus_type: str
    value_type: type
    record: Literal[None, "initial", "final"]

    @property
    def nexus_name(self) -> str:
        return ".".join(self.nexus_nodes)


def nxapitype_from_type(value_type: Type) -> str:
    if issubclass(value_type, str):
        return "NX_CHAR"
    if issubclass(value_type, bool):
        return "NX_BOOLEAN"
    if issubclass(value_type, int):
        return "NX_INT"
    if issubclass(value_type, float):
        return "NX_FLOAT"
    if issubclass(value_type, datetime.datetime):
        return "NX_DATE_TIME"
    raise TypeError(value_type)


def nxapitype_from_annotation(annotation) -> str:
    if get_field_type(annotation, str):
        return "NX_CHAR"
    if get_field_type(annotation, bool):
        return "NX_BOOLEAN"
    if get_field_type(annotation, int):
        return "NX_INT"
    if get_field_type(annotation, float):
        return "NX_FLOAT"
    if get_field_type(annotation, datetime.datetime):
        return "NX_DATE_TIME"
    raise TypeError(annotation)


def value_type_from_annotation(annotation) -> Type:
    if get_field_type(annotation, str):
        return str
    if get_field_type(annotation, bool):
        return bool
    if get_field_type(annotation, int):
        return int
    if get_field_type(annotation, float):
        return float
    if get_field_type(annotation, datetime.datetime):
        return datetime.datetime
    raise TypeError(annotation)


def get_units_and_type(
    annotation: Any,
) -> Optional[Tuple[UnitInfo, Optional[Type]]]:
    """
    Recursively find a PydanticQuantity-style Annotated field and extract:
      - a flag if it's found
      - the pint unit
      - and the expected value type (e.g. float or int)

    Example:
        class Meta:
            __unit__ = ureg.meter
            __value_type__ = float

        annotation = Optional[Annotated[pint.Quantity, Meta]]
        _get_units_and_type(annotation) → (True, <Unit('meter')>, float)
    """
    origin = get_origin(annotation)

    # Case: Optional[...] → Union[X, None]
    if origin is Union:
        for arg in get_args(annotation):
            if arg is not type(None):  # Skip the NoneType
                unit_info, value_type = get_units_and_type(arg)
                if unit_info is not None:
                    return unit_info, value_type

    # Case: Annotated[pint.Quantity, Meta]
    if origin is Annotated or getattr(annotation, "__origin__", None) is Annotated:
        args = get_args(annotation)
        # args[0] is the base type (should be pint.Quantity)
        # args[1:] are metadata (e.g., the PintConverter or Meta class with unit info)
        for meta in args[1:]:
            if hasattr(meta, "__unit__"):
                units = meta.__unit__
                unit_info = UnitInfo(dimension=units.dimensionality, units=units)
                value_type = getattr(meta, "__value_type__", None)
                return unit_info, value_type
            if hasattr(meta, "__dimension__"):
                dimension = meta.__dimension__
                unit_info = UnitInfo(dimension=dimension, units=None)
                value_type = getattr(meta, "__value_type__", None)
                return unit_info, value_type

    # Recurse into other inner types if present
    for arg in get_args(annotation):
        unit_info, value_type = get_units_and_type(arg)
        if unit_info is not None:
            return unit_info, value_type

    # Not found
    return None, None


def get_field_type(annotation: Any, target_type: Type) -> Optional[Type]:
    """Recursively search the `annotation` for `target_type` or a subclass.

    Example:
        For annotation = Optional[Annotated[int, SomeMeta]]
        get_field_type(annotation, int) → int
    """
    # Direct match
    if is_subclass(annotation, target_type):
        return annotation

    # Get outer type, e.g., Union, Annotated
    origin = get_origin(annotation)
    if not origin:
        return

    # Recurse into other inner types if present
    for arg in get_args(annotation):
        field_type = get_field_type(arg, target_type)
        if field_type:
            return field_type


def is_subclass(obj: Any, class_: Type) -> bool:
    """Check if obj is a subclass of class_ safely."""
    return isinstance(obj, type) and issubclass(obj, class_)
