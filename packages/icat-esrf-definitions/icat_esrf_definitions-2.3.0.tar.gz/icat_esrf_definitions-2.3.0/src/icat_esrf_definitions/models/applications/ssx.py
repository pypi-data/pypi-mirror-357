from typing import Optional

from pydantic import Field

from ..base.nexus import NXcollection
from ..base.nexus import NXsubentry


class IcatSsxChip(NXcollection):
    horizontal_spacing: Optional[str] = Field(None, description="")
    vertical_spacing: Optional[str] = Field(None, description="")
    row_number: Optional[str] = Field(None, description="")
    column_number: Optional[str] = Field(None, description="")
    model: Optional[str] = Field(None, description="")


class IcatSsxJet(NXcollection):
    speed: Optional[str] = Field(None, description="Jet's speed")
    size: Optional[str] = Field(None, description="Jet's size")


class IcatSsx(NXsubentry):
    jet: Optional[IcatSsxJet] = Field(None, description="")
    chip: Optional[IcatSsxChip] = Field(None, description="")
