from typing import Optional

from pydantic import Field

from ..base.nexus import NXcollection
from ..base.nexus import NXsubentry
from ..base.quantity import MICROMETERS
from ..base.quantity import MILLIMETERS
from ..base.quantity import SECONDS


class IcatPtychoHorizontalAxis(NXcollection):
    name: Optional[str] = Field(
        None, description="Scan motor in the horizontal direction"
    )
    range: Optional[MICROMETERS] = Field(
        None, description="Range of the moves in microns"
    )


class IcatPtychoVerticalAxis(NXcollection):
    name: Optional[str] = Field(
        None, description="Scan motor in the vertical direction"
    )
    range: Optional[MICROMETERS] = Field(
        None, description="Range of the moves in microns"
    )


class IcatPtycho(NXsubentry):
    propagation: Optional[str] = Field(
        None,
        description="Propagation may be near or far",
        json_schema_extra={"record": "final"},
    )
    beamSize: Optional[MICROMETERS] = Field(
        None,
        description="Beam size on the sample in microns",
        json_schema_extra={"record": "final"},
    )
    stepSize: Optional[MICROMETERS] = Field(
        None, description="Step size during scan", json_schema_extra={"record": "final"}
    )
    focusToDetectorDistance: Optional[MILLIMETERS] = Field(
        None,
        description="Focus to detector distance",
        json_schema_extra={"record": "final"},
    )
    countTime: Optional[SECONDS] = Field(
        None, description="Step size during scan", json_schema_extra={"record": "final"}
    )
    parameters: Optional[str] = Field(
        None, description="Ptycho parameters", json_schema_extra={"record": "final"}
    )
    tomoParameters: Optional[str] = Field(
        None,
        description="Ptycho tomography parameters",
        json_schema_extra={"record": "final"},
    )
    refN: Optional[float] = Field(
        None, description="Ptycho parameters", json_schema_extra={"record": "final"}
    )
    darkN: Optional[float] = Field(
        None, description="Ptycho parameters", json_schema_extra={"record": "final"}
    )
    pixelSize: Optional[MICROMETERS] = Field(
        None, description="Ptycho parameters", json_schema_extra={"record": "final"}
    )
    Axis1: Optional[IcatPtychoHorizontalAxis] = Field(
        None,
        description="",
        json_schema_extra={"icat_name": "_Axis1"},
    )
    Axis2: Optional[IcatPtychoVerticalAxis] = Field(
        None,
        description="",
        json_schema_extra={"icat_name": "_Axis2"},
    )
