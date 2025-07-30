from typing import Optional

from pydantic import Field

from ..base.nexus import NXsubentry
from ..base.quantity import SECONDS


class IcatHolo(NXsubentry):
    n: Optional[float] = Field(
        None,
        description="Number of planes for holography",
        json_schema_extra={"icat_name": "N"},
    )
    sampleDetectorDistances: Optional[str] = Field(
        None,
        description="Sample/detector distances for all planes used",
        json_schema_extra={"icat_name": "holoSampleDetectorDistances"},
    )
    sourceSampleDistances: Optional[str] = Field(
        None,
        description="Source/sample distances for all planes used",
        json_schema_extra={"icat_name": "holoSourceSampleDistances"},
    )
    im01NumEnd: Optional[float] = Field(
        None,
        description="Index of last sample image in plane 1",
        json_schema_extra={"icat_name": "im01_num_end"},
    )
    im01NumStart: Optional[float] = Field(
        None,
        description="Index of first sample image in plane 1",
        json_schema_extra={"icat_name": "im01_num_start"},
    )
    im02NumEnd: Optional[float] = Field(
        None,
        description="Index of last sample image in plane 2",
        json_schema_extra={"icat_name": "im02_num_end"},
    )
    im02NumStart: Optional[float] = Field(
        None,
        description="Index of first sample image in plane 2",
        json_schema_extra={"icat_name": "im02_num_start"},
    )
    im03NumEnd: Optional[float] = Field(
        None,
        description="Index of last sample image in plane 3",
        json_schema_extra={"icat_name": "im03_num_end"},
    )
    im03NumStart: Optional[float] = Field(
        None,
        description="Index of first sample image in plane 3",
        json_schema_extra={"icat_name": "im03_num_start"},
    )
    im04NumEnd: Optional[float] = Field(
        None,
        description="Index of last sample image in plane 4",
        json_schema_extra={"icat_name": "im04_num_end"},
    )
    im04NumStart: Optional[float] = Field(
        None,
        description="Index of first sample image in plane 4",
        json_schema_extra={"icat_name": "im04_num_start"},
    )
    ref01NumEnd: Optional[float] = Field(
        None,
        description="Index of last reference image in plane 1",
        json_schema_extra={"icat_name": "ref01_num_end"},
    )
    ref02NumEnd: Optional[float] = Field(
        None,
        description="Index of last reference image in plane 2",
        json_schema_extra={"icat_name": "ref02_num_end"},
    )
    ref02NumStart: Optional[float] = Field(
        None,
        description="Index of first reference image in plane 2",
        json_schema_extra={"icat_name": "ref02_num_start"},
    )
    ref03NumEnd: Optional[float] = Field(
        None,
        description="Index of last reference image in plane 3",
        json_schema_extra={"icat_name": "ref03_num_end"},
    )
    ref03NumStart: Optional[float] = Field(
        None,
        description="Index of first reference image in plane 3",
        json_schema_extra={"icat_name": "ref03_num_start"},
    )
    ref04NumEnd: Optional[float] = Field(
        None,
        description="Index of last reference image in plane 4",
        json_schema_extra={"icat_name": "ref04_num_end"},
    )
    ref04NumStart: Optional[float] = Field(
        None,
        description="Index of first reference image in plane 4",
        json_schema_extra={"icat_name": "ref04_num_start"},
    )
    darkNumStart: Optional[float] = Field(
        None,
        description="Index of first dark image",
        json_schema_extra={"icat_name": "dark_num_start"},
    )
    darkNumEnd: Optional[float] = Field(
        None,
        description="Index of last dark image",
        json_schema_extra={"icat_name": "dark_num_end"},
    )
    pixelSize: Optional[SECONDS] = Field(
        None, description="Pixel size of first distance in micron"
    )
