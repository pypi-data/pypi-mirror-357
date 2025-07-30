from copy import deepcopy

import pytest
from pydantic import ValidationError

from ..models import IcatDataset


def test_entry():
    model_dict, icat_dict, hdf5_dict = _entry_data()
    _assert_round_trip(model_dict, icat_dict, hdf5_dict)


def test_value_with_units():
    model_dict, icat_dict, hdf5_dict = _entry_data()
    model_dict["PTYCHO"] = {"beamSize": (0.001, "mm")}
    icat_dict["PTYCHO_beamSize"] = 1.0
    hdf5_dict["PTYCHO"] = {
        "@NX_class": "NXsubentry",
        "beamSize": 1.0,
        "beamSize@units": "µm",
    }
    _assert_round_trip(model_dict, icat_dict, hdf5_dict)


def test_wrong_value():
    model_dict, *_ = _entry_data()
    model_dict["PTYCHO"] = {"non_existing": 42}
    with pytest.raises(ValidationError):
        _ = IcatDataset(**model_dict)


def test_icat_fields():
    fields = IcatDataset.icat_fields()
    field_names = IcatDataset.icat_field_names()
    assert list(fields) == list(field_names)


def test_json_schema():
    model_json_schema = IcatDataset.model_json_schema()
    json_schema = model_json_schema["$defs"]["IcatPtycho"]["properties"]["beamSize"]
    expected = {
        "anyOf": [
            {
                "description": "Physical quantity represented as a [magnitude, "
                "unit_string] pair. The value will be converted to "
                "'µm' during validation.",
                "items": [
                    {"description": "Magnitude of the quantity", "type": "number"},
                    {
                        "description": "Unit symbol (e.g., 'mm', 'µm', 'kg')",
                        "type": "string",
                    },
                ],
                "maxItems": 2,
                "minItems": 2,
                "type": "array",
            },
            {"type": "null"},
        ],
        "default": None,
        "description": "Beam size on the sample in microns",
        "record": "final",
        "title": "Beamsize",
    }

    assert json_schema == expected


def _entry_data():
    model_dict = {
        "title": "dummy title",
        "scanNumber": "dummy scanNumber",
        "proposal": "dummy proposal",
        "folder_path": "dummy folder_path",
        "start_time": "2032-04-23T10:20:30.400000+02:30",
        "end_time": "2032-04-23T10:20:30.400000+02:30",
        "sample": {"name": "dummy sample"},
    }
    icat_dict = {
        "datasetName": "dummy title",
        "scanNumber": "dummy scanNumber",
        "proposal": "dummy proposal",
        "location": "dummy folder_path",
        "startDate": "2032-04-23T10:20:30.400000+02:30",
        "endDate": "2032-04-23T10:20:30.400000+02:30",
        "Sample_name": "dummy sample",
    }
    hdf5_dict = {
        "@NX_class": "NXentry",
        "title": "dummy title",
        "scanNumber": "dummy scanNumber",
        "proposal": "dummy proposal",
        "folder_path": "dummy folder_path",
        "start_time": "2032-04-23T10:20:30.400000+02:30",
        "end_time": "2032-04-23T10:20:30.400000+02:30",
        "sample": {"@NX_class": "NXsample", "name": "dummy sample"},
    }
    return model_dict, icat_dict, hdf5_dict


def _assert_round_trip(model_dict: dict, icat_dict: dict, hdf5_dict: dict):
    original_model_dict = deepcopy(model_dict)
    original_icat_dict = deepcopy(icat_dict)
    original_hdf5_dict = deepcopy(hdf5_dict)

    model = IcatDataset(**model_dict)

    assert model.to_icat_dict() == icat_dict
    assert model.to_hdf5_dict() == hdf5_dict

    model1 = IcatDataset.from_icat_dict(icat_dict)
    model2 = IcatDataset.from_hdf5_dict(hdf5_dict)
    assert model1 == model
    assert model2 == model

    assert original_model_dict == model_dict
    assert original_icat_dict == icat_dict
    assert original_hdf5_dict == hdf5_dict
