import re
from typing import Literal

import pytest
from pint.errors import DimensionalityError
from pydantic import Field
from pydantic import ValidationError

from ..models.base import units
from ..models.base.nexus import NXobject
from ..models.base.quantity import MILLIMETERS


def test_fixed_units_and_type():
    class TestModel(NXobject):
        NX_class: Literal["NXparameters"] = Field("NXparameters", alias="@NX_class")
        length: units.PydanticQuantity[r"mm", int]

    # Test unit conversion
    model = TestModel(length=[1, "m"])
    assert str(model.length) == "1000 mm"
    assert model.model_dump() == {
        "NX_class": "NXparameters",
        "length": 1000,
    }

    model.length = 2, "m"
    assert str(model.length) == "2000 mm"

    # Test failing unit conversion
    with pytest.raises(
        DimensionalityError,
        match=re.escape(
            r"Cannot convert from 'kilogram' ([mass]) to 'millimeter' ([length]"
        ),
    ):
        TestModel(length=[10, "kg"])

    # Test value type coercion
    model = TestModel(length=[1.5, "m"])
    assert str(model.length) == "1500 mm"
    assert model.model_dump() == {
        "NX_class": "NXparameters",
        "length": 1500,
    }

    model = TestModel(length=["1.5", "m"])
    assert str(model.length) == "1500 mm"
    assert model.model_dump() == {
        "NX_class": "NXparameters",
        "length": 1500,
    }

    model.length = 2.5, "m"
    assert str(model.length) == "2500 mm"

    # Test default units
    model = TestModel(length=[10, None])
    assert str(model.length) == "10 mm"
    assert model.model_dump() == {
        "NX_class": "NXparameters",
        "length": 10,
    }

    model = TestModel(length=[10])
    assert str(model.length) == "10 mm"
    assert model.model_dump() == {
        "NX_class": "NXparameters",
        "length": 10,
    }

    model.length = 20
    assert str(model.length) == "20 mm"

    model.length = 30
    assert str(model.length) == "30 mm"

    # Test failing type coercion
    with pytest.raises(
        ValidationError,
        match=r"Value error, Magnitude 1.5 cannot be converted to type int",
    ):
        TestModel(length=1.5)

    with pytest.raises(
        ValidationError,
        match=r"Value error, Magnitude 2.5 cannot be converted to type int",
    ):
        model.length = 2.5

    with pytest.raises(
        ValidationError,
        match=r"Value error, Magnitude 0.01 cannot be converted to type int",
    ):
        model = TestModel(length=[10, "µm"])

    with pytest.raises(
        ValidationError,
        match=r"Value error, Magnitude 0.01 cannot be converted to type int",
    ):
        model.length = 10, "µm"


def test_fixed_dimensions_and_type():
    class TestModel(NXobject):
        NX_class: Literal["NXparameters"] = Field("NXparameters", alias="@NX_class")
        length: units.PydanticQuantity[r"[length]", float]
        mass: units.PydanticQuantity[r"[mass]", int]

    model = TestModel(length=[5, "cm"], mass=[3000, "g"])

    assert str(model.length) == "5.0 cm"
    assert str(model.mass) == "3000 g"

    model.length = 6, "m"
    model.mass = 10.0, "mg"

    assert str(model.length) == "6.0 m"
    assert str(model.mass) == "10 mg"


def test_fixed_units_and_any_type():
    class TestModel(NXobject):
        NX_class: Literal["NXparameters"] = Field("NXparameters", alias="@NX_class")
        length: MILLIMETERS

    model = TestModel(length=[1, "m"])
    assert str(model.length) == "1000 mm"
    assert model.model_dump() == {
        "NX_class": "NXparameters",
        "length": 1000,
    }

    model = TestModel(length=[1.0, "m"])
    assert str(model.length) == "1000.0 mm"
    assert model.model_dump() == {
        "NX_class": "NXparameters",
        "length": 1000.0,
    }


def test_dimensionless_and_any_type():
    class TestModel(NXobject):
        NX_class: Literal["NXparameters"] = Field("NXparameters", alias="@NX_class")
        length: units.PydanticQuantity[None]

    model = TestModel(length=1)
    assert str(model.length) == "1"
    assert model.model_dump() == {
        "NX_class": "NXparameters",
        "length": 1,
    }

    model = TestModel(length=1.0)
    assert str(model.length) == "1.0"
    assert model.model_dump() == {
        "NX_class": "NXparameters",
        "length": 1.0,
    }

    with pytest.raises(
        DimensionalityError,
        match=re.escape(
            r"Cannot convert from 'kilogram' ([mass]) to 'dimensionless' (dimensionless)"
        ),
    ):
        TestModel(length=[10, "kg"])


def test_dimensionless_and_fixed_type():
    class TestModel(NXobject):
        NX_class: Literal["NXparameters"] = Field("NXparameters", alias="@NX_class")
        length: units.PydanticQuantity[None, int]

    model = TestModel(length=1)
    assert str(model.length) == "1"
    assert model.model_dump() == {
        "NX_class": "NXparameters",
        "length": 1,
    }

    model = TestModel(length=1.0)
    assert str(model.length) == "1"
    assert model.model_dump() == {
        "NX_class": "NXparameters",
        "length": 1,
    }

    with pytest.raises(
        ValidationError,
        match=r"Value error, Magnitude 1.5 cannot be converted to type int",
    ):
        TestModel(length=1.5)

    with pytest.raises(
        DimensionalityError,
        match=re.escape(
            r"Cannot convert from 'kilogram' ([mass]) to 'dimensionless' (dimensionless)"
        ),
    ):
        TestModel(length=[10, "kg"])


def test_ensure_units():
    q = units.ensure_units((10, "m"), "cm", float)
    assert isinstance(q.magnitude, float)
    assert str(q) == "1000.0 cm"

    for unit in ("photons/second", "photons/s", "photon/second", "photon/s"):
        value = units.ensure_units(100, unit, None)
        assert value.to("kHz").magnitude == 0.1


def test_check_dimension():
    q = units.ensure_dimension((10, "keV"), "[energy]", float)
    assert isinstance(q.magnitude, float)
    assert str(q) == "10.0 keV"

    q = units.ensure_dimension((10, "J"), "[energy]", int)
    assert isinstance(q.magnitude, int)
    assert str(q) == "10 J"
