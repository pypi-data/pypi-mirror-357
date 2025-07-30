from typing import Optional

from pydantic import Field

from ..base.nexus import NXprocess


class IcatWorkflow(NXprocess):
    name: Optional[str] = Field(None, description="")
    id: Optional[str] = Field(None, description="")
    type: Optional[str] = Field(None, description="")
    status: Optional[str] = Field(None, description="")
