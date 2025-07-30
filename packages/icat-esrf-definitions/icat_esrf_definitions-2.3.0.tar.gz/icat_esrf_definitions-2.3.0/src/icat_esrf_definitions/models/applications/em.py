from typing import Optional

from pydantic import Field

from ..base.nexus import NXcollection
from ..base.nexus import NXsubentry


class IcatEmCtf(NXcollection):
    resolution_limit: Optional[str] = Field(None, description="Limit of the resolution")
    correlation: Optional[str] = Field(None, description="")
    defocus_u: Optional[str] = Field(None, description="")
    defocus_v: Optional[str] = Field(None, description="")
    angle: Optional[str] = Field(None, description="")
    estimated_b_factor: Optional[str] = Field(None, description="")


class IcatEmMotionCorrection(NXcollection):
    total_motion: Optional[str] = Field(None, description="Total motion of the sample")
    average_motion: Optional[str] = Field(None, description="Average motion")
    frame_range: Optional[str] = Field(None, description="Motion frame range")
    frame_dose: Optional[str] = Field(None, description="Dose/frame")
    total_dose: Optional[str] = Field(None, description="Total dose")


class IcatEm(NXsubentry):
    protein_acronym: Optional[str] = Field(None, description="Protein acronym")
    voltage: Optional[str] = Field(None, description="Voltage")
    magnification: Optional[str] = Field(None, description="Magnification")
    images_count: Optional[int] = Field(None, description="Number of images in movie")
    position_x: Optional[str] = Field(None, description="Position X")
    position_y: Optional[str] = Field(None, description="Position Y")
    dose_initial: Optional[str] = Field(None, description="Dose initial")
    dose_per_frame: Optional[str] = Field(None, description="Dose per frame")
    spherical_aberration: Optional[str] = Field(
        None, description="Spherical aberration"
    )
    amplitude_contrast: Optional[str] = Field(None, description="Amplitude contrast")
    sampling_rate: Optional[str] = Field(None, description="samplingRate")
    tilt_angle: Optional[str] = Field(None, description="tilt_angle")
    grid_name: Optional[str] = Field(None, description="grid_name")
    motioncorrection: Optional[IcatEmMotionCorrection] = Field(
        None,
        description="",
        json_schema_extra={"icat_name": "MotionCorrection"},
    )

    ctf: Optional[IcatEmCtf] = Field(
        None,
        description="",
        json_schema_extra={"icat_name": "CTF"},
    )
