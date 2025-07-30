from typing import Optional

from pydantic import Field

from ..base.nexus import NXprocess


class IcatProcess(NXprocess):
    program: Optional[str] = Field(None, description="")
    sequence_index: Optional[str] = Field(None, description="")
    version: Optional[str] = Field(None, description="")
    note: Optional[str] = Field(None, description="")
    triggering: Optional[str] = Field(
        None,
        description="Defines how the process has been launched. Values are MANUAL, AUTOMATIC",
    )
