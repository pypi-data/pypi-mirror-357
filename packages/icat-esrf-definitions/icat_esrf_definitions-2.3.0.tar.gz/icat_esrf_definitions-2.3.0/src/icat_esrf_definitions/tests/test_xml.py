from .. import DEFINITIONS_FILE
from ..models import IcatDataset
from . import xml_utils


def test_xml_dict():
    xml_dict_from_file = xml_utils.read_xml(DEFINITIONS_FILE)
    xml_dict_from_model = IcatDataset.to_xml_dict()
    assert xml_dict_from_model == xml_dict_from_file


def test_xml_file(tmp_path):
    with open(DEFINITIONS_FILE, "r", encoding="utf-8") as f:
        xml_str_from_file = f.read()

    filename = str(tmp_path / "test.xml")
    IcatDataset.to_xml_file(filename)

    with open(DEFINITIONS_FILE, "r", encoding="utf-8") as f:
        xml_str_from_model = f.read()

    assert xml_str_from_file == xml_str_from_model
