from typing import Optional

from pydantic import Field

from ..base.nexus import NXsubentry
from ..base.quantity import MICROMETERS


class IcatSxdm(NXsubentry):
    beamSizeVertical: Optional[MICROMETERS] = Field(
        None,
        description="Vertical beam size on the sample in microns",
        json_schema_extra={"record": "final"},
    )
    beamSizeHorizontal: Optional[MICROMETERS] = Field(
        None,
        description="Horizontal beam size on the sample in microns",
        json_schema_extra={"record": "final"},
    )
