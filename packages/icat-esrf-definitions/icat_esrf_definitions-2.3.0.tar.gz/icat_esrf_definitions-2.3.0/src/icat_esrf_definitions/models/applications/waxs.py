from typing import Optional

from pydantic import Field

from ..base.nexus import NXsubentry


class IcatWaxs(NXsubentry):
    definition: Optional[str] = Field(
        None, description="Technique used to collect this dataset"
    )
