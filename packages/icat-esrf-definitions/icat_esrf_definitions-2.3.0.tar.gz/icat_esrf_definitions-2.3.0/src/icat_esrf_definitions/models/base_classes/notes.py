from typing import Optional

from pydantic import Field

from ..base.nexus import NXnote


class IcatNotes(NXnote):
    note_00: Optional[str] = Field(None, description="")
    note_01: Optional[str] = Field(None, description="")
    note_02: Optional[str] = Field(None, description="")
    note_03: Optional[str] = Field(None, description="")
    note_04: Optional[str] = Field(None, description="")
    note_05: Optional[str] = Field(None, description="")
    note_06: Optional[str] = Field(None, description="")
    note_07: Optional[str] = Field(None, description="")
    note_08: Optional[str] = Field(None, description="")
    note_09: Optional[str] = Field(None, description="")
