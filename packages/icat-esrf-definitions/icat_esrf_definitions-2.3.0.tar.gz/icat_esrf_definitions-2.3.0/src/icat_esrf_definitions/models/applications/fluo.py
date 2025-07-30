from typing import Optional

from pydantic import Field

from ..base.nexus import NXcollection
from ..base.nexus import NXsubentry
from ..base.quantity import MICROMETERS
from ..base.quantity import MILLIAMPERES
from ..base.quantity import PHOTON_FLUX
from ..base.quantity import SECONDS


class IcatFluoMeasurement(NXcollection):
    current_start: Optional[MILLIAMPERES] = Field(
        None, description="Machine current", json_schema_extra={"record": "initial"}
    )
    current_end: Optional[MILLIAMPERES] = Field(
        None, description="Machine current", json_schema_extra={"record": "final"}
    )
    i0_start: Optional[PHOTON_FLUX] = Field(
        None, description="Incident flux", json_schema_extra={"record": "initial"}
    )
    it_start: Optional[PHOTON_FLUX] = Field(
        None, description="Transmitted flux", json_schema_extra={"record": "initial"}
    )
    i0_end: Optional[PHOTON_FLUX] = Field(
        None, description="Incident flux", json_schema_extra={"record": "final"}
    )
    it_end: Optional[PHOTON_FLUX] = Field(
        None, description="Transmitted flux", json_schema_extra={"record": "final"}
    )


class IcatFluo(NXsubentry):
    pixelSize: Optional[MICROMETERS] = Field(
        None, description="", json_schema_extra={"record": "final"}
    )
    dwellTime: Optional[SECONDS] = Field(
        None, description="", json_schema_extra={"record": "final"}
    )
    scanDim_1: Optional[float] = Field(
        None,
        description="",
        json_schema_extra={"icat_name": "scanDim1", "record": "final"},
    )
    scanDim_2: Optional[float] = Field(
        None,
        description="",
        json_schema_extra={"icat_name": "scanDim2", "record": "final"},
    )
    scanRange_1: Optional[MICROMETERS] = Field(
        None,
        description="",
        json_schema_extra={"icat_name": "scanRange1", "record": "final"},
    )
    scanRange_2: Optional[MICROMETERS] = Field(
        None,
        description="",
        json_schema_extra={"icat_name": "scanRange2", "record": "final"},
    )
    scanAxis_1: Optional[str] = Field(
        None,
        description="",
        json_schema_extra={"icat_name": "scanAxis1", "record": "final"},
    )
    scanAxis_2: Optional[str] = Field(
        None,
        description="",
        json_schema_extra={"icat_name": "scanAxis2", "record": "final"},
    )
    i0: Optional[float] = Field(None, description="Incident intensity")
    it: Optional[float] = Field(None, description="Transmitted intensity")
    measurement: Optional[IcatFluoMeasurement] = Field(None, description="")
