from typing import Optional

from pydantic import Field

from ..base.nexus import NXfresnel_zone_plate


class IcatFresnelZonePlate(NXfresnel_zone_plate):
    outer_diameter: Optional[str] = Field(None, description="")
    outermost_zone_width: Optional[str] = Field(None, description="")
    central_stop_diameter: Optional[str] = Field(None, description="")
    fabrication: Optional[str] = Field(
        None,
        description="how the zone plate was manufactured. Any of these values: etched | plated | zone doubled | other",
    )
    zone_height: Optional[str] = Field(None, description="")
    zone_material: Optional[str] = Field(None, description="")
    zone_support_material: Optional[str] = Field(
        None,
        description="Material present between the zones. This is usually only present for the “zone doubled” fabrication process",
    )
    central_stop_material: Optional[str] = Field(None, description="")
    central_stop_thickness: Optional[str] = Field(None, description="")
    support_membrane_material: Optional[str] = Field(None, description="")
    distance: Optional[str] = Field(None, description="")
    component_index: Optional[str] = Field(None, description="")
