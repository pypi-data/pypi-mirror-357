"""Support Pint quantities (value and unit) in Pydantic models."""

import numbers
from typing import Any
from typing import Generic
from typing import Optional
from typing import Sequence
from typing import Type
from typing import TypeVar
from typing import Union

try:
    from typing import Annotated
except ImportError:
    # python <3.9
    from typing_extensions import Annotated

import pint
import pydantic
from pint import Quantity
from pint import Unit
from pint.util import UnitsContainer
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

# Initialize Pint unit registry
REGISTRY = pint.UnitRegistry()

# Use unit symbols (like "mm", "µm") instead of full names
try:
    REGISTRY.formatter.default_format = "~P"
except AttributeError:
    # python <3.9
    REGISTRY.default_format = "~P"

# Define custom units
REGISTRY.define("photon = count")
REGISTRY.define("photons = photon")
REGISTRY.define("pixel = []")  # dimensionless
REGISTRY.define("pixels = pixel")

# Type variables for generics
ValueT = TypeVar("ValueT", bound=Optional[type])
UnitStrT = TypeVar("UnitStrT", bound=Optional[str])

# Acceptable input types for a quantity e.g., [100, "m"]
ValueWithUnitsType = Union[
    Quantity, Sequence[Union[numbers.Number, str]], numbers.Number, str
]


def ensure_units(
    value: ValueWithUnitsType, units: Union[Unit, str], value_type: Optional[type]
) -> Quantity:
    """
    Normalize various input types into a Pint Quantity with specified units
    and optionally enforce magnitude type.
    """
    if isinstance(units, str):
        units = REGISTRY.parse_units(units)
    elif not isinstance(units, Unit):
        raise TypeError(f"{units} is not a pint Unit instance")
    if value_type is not None and not isinstance(value_type, type):
        raise TypeError(f"The value type {value_type} is not a type")

    # Parse value into a Quantity with unit coercion when needed
    if isinstance(value, Quantity):
        # Coerce units when needed
        q = value.to(units)
    elif isinstance(value, Sequence) and not isinstance(value, str):
        # Handle list/tuple input like [value, "unit"]
        if len(value) == 2:
            v, u = value
        elif len(value) == 1:
            v, u = value[0], None
        else:
            raise ValueError(f"{value} cannot have more than one value")

        if isinstance(v, str):
            v = float(v)
        if value_type is None:
            value_type = type(v)

        # Coerce units when needed
        q = REGISTRY.Quantity(v, u or units).to(units)
    else:
        # Scalar input: number or string
        if isinstance(value, str):
            value = float(value)
        if value_type is None:
            value_type = type(value)
        q = REGISTRY.Quantity(value, units)

    # Validate or coerce magnitude to expected type
    return _magnitude_type_coerce(q, value_type)


def ensure_dimension(
    value: ValueWithUnitsType,
    dimension: Union[UnitsContainer, str],
    value_type: Optional[type],
) -> Quantity:
    """
    Convert `value` to a Quantity without forcing unit conversion, then check if
    its dimensionality matches `dimension`.
    Raises ValueError if dimension does not match.
    """
    if isinstance(dimension, str):
        dimension = REGISTRY.get_dimensionality(dimension)
    elif not isinstance(dimension, UnitsContainer):
        raise TypeError(f"{dimension} is not a pint UnitsContainer instance")
    if value_type is not None and not isinstance(value_type, type):
        raise TypeError(f"The value type {value_type} is not a type")

    # Parse value into a Quantity
    if isinstance(value, Quantity):
        q = value
    elif isinstance(value, Sequence) and not isinstance(value, str):
        if len(value) == 2:
            v, u = value
        elif len(value) == 1:
            v, u = value[0], None
        else:
            raise ValueError(f"{value} cannot have more than one value")
        if isinstance(v, str):
            v = float(v)
        q = REGISTRY.Quantity(v, u)
    else:
        if isinstance(value, str):
            value = float(value)
        q = REGISTRY.Quantity(value)

    # Check dimensionality
    if not q.check(dimension):
        raise ValueError(f"{value} does not match dimensionality '{dimension}'")

    # Validate or coerce magnitude to expected type
    return _magnitude_type_coerce(q, value_type)


def _magnitude_type_coerce(q: Quantity, value_type: Optional[type]) -> Quantity:
    if value_type is None or isinstance(q.magnitude, value_type):
        return q

    magnitude = value_type(q.magnitude)
    if magnitude != q.magnitude:
        raise ValueError(
            f"Magnitude {q.magnitude} cannot be converted to type {value_type.__name__}"
        )

    return REGISTRY.Quantity(magnitude, q.units)


class PydanticQuantity(Generic[UnitStrT, ValueT]):
    """
    Pydantic field for a physical quantity with a unit and optional enforced value type.

    Usage example:

    .. code-block: python

        class MyModel(BaseModel):
            length: PydanticQuantity["mm", float]       # Require float, convert to mm
            energy: PydanticQuantity["[energy]", None]  # Validate energy unit
            count: PydanticQuantity["count", int]       # Require int, dimensionless
            any_unitless: PydanticQuantity[None, None]  # Dimensionless

        m = MyModel(length=[1, "m"], energy=[10, "keV"], count=42, any_unitless="3.5")
        print(m.length)       # 1000.0 millimeter
        print(m.energy)       # 10 keV
        print(m.count)        # 42 count
        print(m.any_unitless) # 3.5
    """

    def __class_getitem__(cls, item):
        # Support generic syntax: PydanticQuantity["mm", float] or PydanticQuantity["length", float]
        if isinstance(item, tuple):
            unit_in, value_type = item
        else:
            unit_in, value_type = item, None

        # Parse the unit or dimension
        if not unit_in:
            unit_in = REGISTRY.dimensionless

        if isinstance(unit_in, Unit):
            return cls.__unit_annotated(unit_in, value_type)

        if isinstance(unit_in, UnitsContainer):
            return cls.__unit_annotated(unit_in, value_type)

        try:
            # Try interpreting as a specific unit (e.g., "mm", "s")
            unit = REGISTRY.parse_units(unit_in)
        except (pint.UndefinedUnitError, pint.DefinitionSyntaxError):
            # If it's not a unit, treat it as a dimensionality (e.g., "length")
            dimension = REGISTRY.get_dimensionality(unit_in)
            return cls.__dimension_annotated(dimension, value_type)

        return cls.__unit_annotated(unit, value_type)

    @classmethod
    def __unit_annotated(cls, unit: Unit, value_type: Optional[type]):
        # Validator for converting values
        def validator(value: ValueWithUnitsType) -> Quantity:
            return ensure_units(value, unit, value_type)

        # Serializer: return only magnitude (used in model_dump)
        def serializer(value: ValueWithUnitsType) -> numbers.Number:
            return ensure_units(value, unit, value_type).magnitude

        # Core schema to use Pydantic's internals
        json_schema = core_schema.no_info_plain_validator_function(validator)
        python_schema = core_schema.union_schema(
            [
                core_schema.is_instance_schema(Quantity),
                json_schema,
            ]
        )
        serialization = core_schema.plain_serializer_function_ser_schema(serializer)

        # Define how this field should look in JSON schema
        json_schema_dict: JsonSchemaValue = {
            "type": "array",
            "minItems": 2,
            "maxItems": 2,
            "items": [
                {
                    "type": "number",
                    "description": "Magnitude of the quantity",
                },
                {
                    "type": "string",
                    "description": "Unit symbol (e.g., 'mm', 'µm', 'kg')",
                },
            ],
            "description": (
                f"Physical quantity represented as a [magnitude, unit_string] pair. "
                f"The value will be converted to '{unit}' during validation."
            ),
        }

        # Class holding metadata for introspection
        class PintUnitConverter:
            __unit__: Unit = unit
            __value_type__: Type = float if value_type is None else value_type

            @classmethod
            def __get_pydantic_core_schema__(
                cls, source: Any, handler: pydantic.GetCoreSchemaHandler
            ) -> core_schema.CoreSchema:
                return core_schema.json_or_python_schema(
                    json_schema=json_schema,
                    python_schema=python_schema,
                    serialization=serialization,
                )

            @classmethod
            def __get_pydantic_json_schema__(
                cls,
                schema: core_schema.CoreSchema,
                handler: pydantic.GetJsonSchemaHandler,
            ) -> JsonSchemaValue:
                return json_schema_dict

        # Annotated field for Pydantic to hook into
        return Annotated[Quantity, PintUnitConverter]

    @classmethod
    def __dimension_annotated(
        cls, dimension: UnitsContainer, value_type: Optional[type]
    ):
        # Validator for converting values
        def validator(value: ValueWithUnitsType) -> Quantity:
            return ensure_dimension(value, dimension, value_type)

        # Serializer: return only magnitude (used in model_dump)
        def serializer(value: ValueWithUnitsType) -> numbers.Number:
            return ensure_dimension(value, dimension, value_type).magnitude

        # Core schema to use Pydantic's internals
        json_schema = core_schema.no_info_plain_validator_function(validator)
        python_schema = core_schema.union_schema(
            [
                core_schema.is_instance_schema(Quantity),
                json_schema,
            ]
        )
        serialization = core_schema.plain_serializer_function_ser_schema(serializer)

        # Define how this field should look in JSON schema
        json_schema_dict: JsonSchemaValue = {
            "type": "array",
            "minItems": 2,
            "maxItems": 2,
            "items": [
                {
                    "type": "number",
                    "description": "Magnitude of the quantity",
                },
                {
                    "type": "string",
                    "description": "Unit dimension (e.g., '[length]', '[mass]', '[energy]')",
                },
            ],
            "description": (
                f"Physical quantity represented as a [magnitude, dimension_string] pair. "
                f"The value will be converted to '{dimension}' during validation."
            ),
        }

        # Class holding metadata for introspection
        class PintDimensionConverter:
            __dimension__ = dimension
            __value_type__: Type = float if value_type is None else value_type

            @classmethod
            def __get_pydantic_core_schema__(
                cls, source: Any, handler: pydantic.GetCoreSchemaHandler
            ) -> core_schema.CoreSchema:
                return core_schema.json_or_python_schema(
                    json_schema=json_schema,
                    python_schema=python_schema,
                    serialization=serialization,
                )

            @classmethod
            def __get_pydantic_json_schema__(
                cls,
                schema: core_schema.CoreSchema,
                handler: pydantic.GetJsonSchemaHandler,
            ) -> JsonSchemaValue:
                return json_schema_dict

        # Annotated field for Pydantic to hook into
        return Annotated[Quantity, PintDimensionConverter]
