from typing import Optional

from pydantic import Field

from ..base.nexus import NXsubentry
from ..base.quantity import KILOELECTRONVOLTS
from ..base.quantity import MILLIMETERS
from ..base.quantity import SECONDS


class IcatHtxrpd(NXsubentry):
    energy: Optional[KILOELECTRONVOLTS] = Field(None, description="Beam energy")
    exposureTime: Optional[SECONDS] = Field(
        None, description="Requested exposure time per diffraction pattern"
    )
    distance: Optional[MILLIMETERS] = Field(
        None, description="The perpendicular sample-detector distance"
    )
    sampleVibration: Optional[float] = Field(
        None, description="The vibration speed of the powder sample (0-100 %)"
    )
