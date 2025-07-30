from typing import Optional

from pydantic import Field

from ..base.nexus import NXsubentry
from ..base.quantity import DEGREES_ANGLE
from ..base.quantity import GRAY
from ..base.quantity import GRAY_PER_SECOND_PER_MILLIAMPERE
from ..base.quantity import MICROMETERS
from ..base.quantity import MILLIMETERS
from ..base.quantity import MILLIMETERS_PER_SECOND


class IcatMrt(NXsubentry):
    mscType: Optional[str] = Field(None, description="Multislit Type")
    doseRate: Optional[GRAY_PER_SECOND_PER_MILLIAMPERE] = Field(
        None, description="Dose Rate"
    )
    ctcMot: Optional[str] = Field(None, description="C-to-C Motor")
    ctcSpacing: Optional[MICROMETERS] = Field(None, description="C-to-C Spacing")
    ctcN: Optional[int] = Field(None, description="Number of Irradiations")
    crossMot: Optional[str] = Field(None, description="Crossfiring Motor")
    crossAngle: Optional[DEGREES_ANGLE] = Field(None, description="Crossfiring Angle")
    crossN: Optional[int] = Field(None, description="Number of Crossfiring")
    intlcdMot: Optional[str] = Field(None, description="Interlaced Motor")
    intlcdOff: Optional[MICROMETERS] = Field(None, description="Interlaced Offset")
    expoStart: Optional[MILLIMETERS] = Field(None, description="Z Start Position")
    expoStop: Optional[MILLIMETERS] = Field(None, description="Z Stop Position")
    expoSpeed: Optional[MILLIMETERS_PER_SECOND] = Field(
        None, description="Z Last Speed"
    )
    IC01: Optional[str] = Field(None, description="Counts on ION chamber 0-1")
    IC02: Optional[str] = Field(None, description="Counts on ION chamber 0-2")
    IC0MU1: Optional[str] = Field(None, description="Counts on ION MUSST chamber 0-1")
    IC0MU2: Optional[str] = Field(None, description="Counts on ION MUSST chamber 0-2")
    IONCH1: Optional[str] = Field(None, description="Counts on ION chamber 1")
    IONCH2: Optional[str] = Field(None, description="Counts on ION chamber 2")
    dose: Optional[GRAY] = Field(None, description="Dose Planned")
    beamHeight: Optional[MICROMETERS] = Field(None, description="Beam Vertical Width")
    beamSize: Optional[MICROMETERS] = Field(None, description="Microbeam Width")
