from typing import Optional

from pydantic import Field

from ..base.nexus import NXsubentry
from ..base.quantity import KILODALTONS
from ..base.quantity import NANOMETERS_CUBED


class IcatSaxs(NXsubentry):
    definition: Optional[str] = Field(
        None, description="Technique used to collect this dataset"
    )
    version: Optional[str] = Field(
        None,
        description="Version",
        json_schema_extra={"icat_name": "definition.version"},
    )
    directory: Optional[str] = Field(
        None,
        description="Data collection directory",
        json_schema_extra={"record": "final"},
    )
    experimentType: Optional[str] = Field(
        None, description="Type of experiment", json_schema_extra={"record": "final"}
    )
    prefix: Optional[str] = Field(
        None, description="", json_schema_extra={"record": "final"}
    )
    maskFile: Optional[str] = Field(
        None, description="", json_schema_extra={"record": "final"}
    )
    numberFrames: Optional[str] = Field(
        None, description="", json_schema_extra={"record": "final"}
    )
    timePerFrame: Optional[str] = Field(
        None, description="", json_schema_extra={"record": "final"}
    )
    concentration: Optional[str] = Field(
        None, description="", json_schema_extra={"record": "final"}
    )
    comments: Optional[str] = Field(
        None, description="", json_schema_extra={"record": "final"}
    )
    code: Optional[str] = Field(
        None, description="", json_schema_extra={"record": "final"}
    )
    detector_distance: Optional[str] = Field(
        None, description="", json_schema_extra={"record": "final"}
    )
    waveLength: Optional[str] = Field(
        None, description="", json_schema_extra={"record": "final"}
    )
    pixelSizeX: Optional[str] = Field(
        None, description="", json_schema_extra={"record": "final"}
    )
    pixelSizeY: Optional[str] = Field(
        None, description="", json_schema_extra={"record": "final"}
    )
    beam_center_x: Optional[str] = Field(
        None, description="", json_schema_extra={"record": "final"}
    )
    beam_center_y: Optional[str] = Field(
        None, description="", json_schema_extra={"record": "final"}
    )
    normalisation: Optional[str] = Field(
        None, description="", json_schema_extra={"record": "final"}
    )
    diode_currents: Optional[str] = Field(
        None, description="", json_schema_extra={"record": "final"}
    )
    acronym: Optional[str] = Field(
        None, description="", json_schema_extra={"record": "final"}
    )
    transmission: Optional[str] = Field(
        None, description="", json_schema_extra={"record": "final"}
    )
    storage_temperature: Optional[str] = Field(
        None, description="", json_schema_extra={"record": "final"}
    )
    exposure_temperature: Optional[str] = Field(
        None, description="", json_schema_extra={"record": "final"}
    )
    column_type: Optional[str] = Field(
        None,
        description="HPLC column type. [ex. Agilent BioSEC 130]",
        json_schema_extra={"record": "final"},
    )
    flow_rate: Optional[str] = Field(
        None, description="", json_schema_extra={"record": "final"}
    )
    hplc_port: Optional[str] = Field(
        None, description="", json_schema_extra={"record": "final"}
    )
    sample_type: Optional[str] = Field(
        None,
        description="It can be buffer or sample",
        json_schema_extra={"record": "final"},
    )
    run_number: Optional[str] = Field(
        None,
        description="It can be buffer or sample",
        json_schema_extra={"record": "final"},
    )
    experiment_type: Optional[str] = Field(
        None,
        description="It the kind of experiment: sample changer or HPLC",
        json_schema_extra={"record": "final"},
    )
    guinier_rg: Optional[str] = Field(
        None,
        description="Guinier radius of giration",
        json_schema_extra={"record": "final"},
    )
    guinier_sigma_rg: Optional[str] = Field(
        None,
        description="Guinier radius of giration sigma",
        json_schema_extra={"record": "final"},
    )
    guinier_points: Optional[str] = Field(
        None,
        description="Points of the Guinier region",
        json_schema_extra={"record": "final"},
    )
    guinier_points_start: Optional[str] = Field(
        None,
        description="Points of the Guinier region",
        json_schema_extra={"record": "final"},
    )
    guinier_points_end: Optional[str] = Field(
        None,
        description="Points of the Guinier region",
        json_schema_extra={"record": "final"},
    )
    guinier_i0: Optional[str] = Field(
        None,
        description="Guinier radius of giration",
        json_schema_extra={"record": "final"},
    )
    rg: Optional[str] = Field(
        None,
        description="Calculated radious of giration. It can be calculated with Gnom or BIFT",
        json_schema_extra={"record": "final"},
    )
    rg_std: Optional[str] = Field(
        None,
        description="Calculated std radious of giration",
        json_schema_extra={"record": "final"},
    )
    rg_avg: Optional[str] = Field(
        None,
        description="Calculated average of radious of giration",
        json_schema_extra={"record": "final"},
    )
    total: Optional[str] = Field(
        None, description="", json_schema_extra={"record": "final"}
    )
    d_max: Optional[str] = Field(
        None,
        description="maximum particle dimension. it is the largest distance between any two points within the particle and is a crucial parameter in SAXS analysis.",
        json_schema_extra={"record": "final"},
    )
    d_max_std: Optional[str] = Field(
        None,
        description="d_max standard deviation",
        json_schema_extra={"record": "final"},
    )
    porod_volume: Optional[str] = Field(
        None,
        description="The Porod volume is an estimate of the molecular volume of a particle derived from SAXS data. It is obtained using the Porod invariant, which is related to the scattering intensity at high angles.",
        json_schema_extra={"record": "final"},
    )
    porod_MM_volume_estimation: Optional[str] = Field(
        None,
        description="molecular weight (MW) of a macromolecule in solution using the Porod volume",
        json_schema_extra={"record": "final"},
    )
    frames_averaged: Optional[str] = Field(
        None, description="", json_schema_extra={"record": "final"}
    )
    vc: Optional[NANOMETERS_CUBED] = Field(
        None,
        description="The Volume of Correlation is a SAXS-derived parameter that provides an alternative estimate of the molecular volume of a biomolecule.",
        json_schema_extra={"record": "final"},
    )
    vc_error: Optional[NANOMETERS_CUBED] = Field(
        None,
        description="Volume of correlation error",
        json_schema_extra={"record": "final"},
    )
    mass: Optional[KILODALTONS] = Field(
        None, description="Molecular weight", json_schema_extra={"record": "final"}
    )
    mass_error: Optional[KILODALTONS] = Field(
        None,
        description="Molecular weight error",
        json_schema_extra={"record": "final"},
    )
    chi2r: Optional[str] = Field(
        None,
        description="goodness of fit between experimental scattering data and a theoretical model or fit.",
        json_schema_extra={"record": "final"},
    )
    chi2r_error: Optional[str] = Field(
        None,
        description="Error of the agreement",
        json_schema_extra={"record": "final"},
    )
