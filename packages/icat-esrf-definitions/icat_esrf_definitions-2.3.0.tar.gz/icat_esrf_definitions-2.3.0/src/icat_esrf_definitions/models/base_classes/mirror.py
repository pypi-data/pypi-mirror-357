from typing import Optional

from pydantic import Field

from ..base.nexus import NXgeometry
from ..base.nexus import NXmirror


class IcatMirrorGeometry(NXgeometry):
    vertical: Optional[str] = Field(
        None,
        description="Optional description/label. Probably only present if we are an additional reference point for components rather than the location of a real component.",
    )
    horizontal: Optional[str] = Field(None, description="")
    transformation: Optional[str] = Field(None, description="")
    distance: Optional[str] = Field(None, description="")
    component_index: Optional[str] = Field(
        None,
        description="Position of the component along the beam path. The sample is at 0, components upstream have negative component_index, components downstream have positive component_index.",
    )


class IcatMirror(NXmirror):
    type: Optional[str] = Field(
        None,
        description="Any of these values: single: mirror with a single material as a reflecting surface, multi: mirror with stacked, multiple layers as a reflecting surface",
    )
    description: Optional[str] = Field(None, description="description of this mirror")
    interior_atmosphere: Optional[str] = Field(
        None, description="Any of these values: vacuum | helium | argon"
    )
    substrate_material: Optional[str] = Field(None, description="")
    coating_material: Optional[str] = Field(None, description="")
    geometry: Optional[IcatMirrorGeometry] = Field(None, description="")
