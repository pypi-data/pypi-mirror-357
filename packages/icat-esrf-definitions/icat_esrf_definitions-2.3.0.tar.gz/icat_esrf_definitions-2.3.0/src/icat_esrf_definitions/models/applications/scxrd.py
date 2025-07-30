from typing import Optional

from pydantic import Field

from ..base.nexus import NXsubentry
from ..base.quantity import ANGSTROMS
from ..base.quantity import DEGREES
from ..base.quantity import METERS
from ..base.quantity import SECONDS


class IcatScxrd(NXsubentry):
    sample_detector_distance: Optional[METERS] = Field(
        None,
        description="Distance from sample to detector",
        json_schema_extra={"record": "final"},
    )
    beam_center_x: Optional[float] = Field(
        None,
        description="X Coordinate of the beamcenter",
        json_schema_extra={"record": "final"},
    )
    beam_center_y: Optional[float] = Field(
        None,
        description="Y Coordinate of the beamcenter",
        json_schema_extra={"record": "final"},
    )
    wavelength: Optional[ANGSTROMS] = Field(
        None, description="X-ray wavelength", json_schema_extra={"record": "final"}
    )
    detector_tilts: Optional[DEGREES] = Field(
        None,
        description="Detector tilts around X, Y and Z axes",
        json_schema_extra={"record": "final"},
    )
    rotation_axis: Optional[str] = Field(
        None,
        description="Name of the rotation axis (e.g., omega)",
        json_schema_extra={"record": "final"},
    )
    rotation_range: Optional[DEGREES] = Field(
        None,
        description="Rotation range for the crystal scan (start,end)",
        json_schema_extra={"record": "final"},
    )
    rotation_step: Optional[DEGREES] = Field(
        None,
        description="Rotation step between two frames",
        json_schema_extra={"record": "final"},
    )
    exposure_time: Optional[SECONDS] = Field(
        None,
        description="Exposure time per image",
        json_schema_extra={"record": "final"},
    )
