from typing import Any
from typing import Dict

import xmltodict


def read_xml(xml_path: str) -> Dict[str, Any]:
    with open(xml_path, "r", encoding="utf-8") as fh:
        xml_string = fh.read()
    return xmltodict.parse(xml_string)["group"]
