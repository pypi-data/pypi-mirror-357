from typing import Optional

from pydantic import Field

from ..base.nexus import NXcite
from ..base.nexus import NXnote


class IcatExternalReferencesDatacollector(NXcite):
    endnote: Optional[str] = Field(None, description="")


class IcatExternalReferencesPublication(NXcite):
    doi: Optional[str] = Field(None, description="")
    endnote: Optional[str] = Field(None, description="")


class IcatExternalReferences(NXnote):
    neuroglancer: Optional[str] = Field(None, description="")
    publication: Optional[IcatExternalReferencesPublication] = Field(
        None, description=""
    )
    datacollector: Optional[IcatExternalReferencesDatacollector] = Field(
        None, description=""
    )
