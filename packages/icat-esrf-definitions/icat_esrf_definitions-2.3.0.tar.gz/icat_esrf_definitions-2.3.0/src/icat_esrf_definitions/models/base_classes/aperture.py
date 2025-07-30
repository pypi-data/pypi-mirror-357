from typing import Optional

from pydantic import Field

from ..base.nexus import NXaperture
from ..base.nexus import NXgeometry


class IcatApertureGeometry(NXgeometry):
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


class IcatAperture(NXaperture):
    description: Optional[str] = Field(
        None,
        description="Declares which child group contains a path leading to a NXdata group. It is recommended (as of NIAC2014) to use this attribute to help define the path to the default dataset to be plotted. See https://www.nexusformat.org/2014_How_to_find_default_data.html for a summary of the discussion.",
    )
    material: Optional[str] = Field(
        None, description="Absorbing material of the aperture"
    )
    geometry: Optional[IcatApertureGeometry] = Field(None, description="")
