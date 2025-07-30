from datetime import datetime
from typing import Optional

from pydantic import Field

from .applications.bcdi import IcatBcdi
from .applications.em import IcatEm
from .applications.fluo import IcatFluo
from .applications.holo import IcatHolo
from .applications.htxrpd import IcatHtxrpd
from .applications.mrt import IcatMrt
from .applications.mx import IcatMx
from .applications.ptycho import IcatPtycho

# NeXus applications definitions
from .applications.saxs import IcatSaxs
from .applications.scxrd import IcatScxrd
from .applications.ssx import IcatSsx
from .applications.sxdm import IcatSxdm
from .applications.tomo import IcatTomo
from .applications.waxs import IcatWaxs
from .base.nexus import NXentry
from .base_classes.aperture import IcatAperture
from .base_classes.external_references import IcatExternalReferences
from .base_classes.fresnel_zone_plate import IcatFresnelZonePlate
from .base_classes.instrument import IcatInstrument
from .base_classes.mirror import IcatMirror
from .base_classes.notes import IcatNotes
from .base_classes.process import IcatProcess

# NeXus base classes
from .base_classes.sample import IcatSample
from .base_classes.workflow import IcatWorkflow


class IcatDataset(NXentry):
    """Root model for ICAT dataset metadata."""

    title: str = Field(
        ...,
        description="Name of the dataset",
        json_schema_extra={"icat_name": "datasetName"},
    )
    scanNumber: str = Field(..., description="Scan number")
    proposal: str = Field(..., description="Proposal code")
    dataset_type: Optional[str] = Field(
        None,
        description="Scan type can be 'step_by_step' or 'continuous'",
        json_schema_extra={"icat_name": "scanType", "record": "final"},
    )
    folder_path: str = Field(
        ...,
        description="Scan starting date",
        json_schema_extra={"icat_name": "location"},
    )
    start_time: datetime = Field(
        ...,
        description="Scan starting date",
        json_schema_extra={"icat_name": "startDate"},
    )
    end_time: datetime = Field(
        ...,
        description="Scan ending date",
        json_schema_extra={"icat_name": "endDate", "record": "final"},
    )
    definition: Optional[str] = Field(
        None, description="Techniques used to collect this dataset"
    )
    technique_pid: Optional[str] = Field(
        None,
        description="List of space-separated techniques identifiers used to collect this dataset, eg. PaNET ids",
    )
    doi_abstract: Optional[str] = Field(
        None,
        description="Abstract of the DOI",
        json_schema_extra={"icat_name": "DOI_abstract"},
    )
    doi_title: Optional[str] = Field(
        None,
        description="Title fo the DOI",
        json_schema_extra={"icat_name": "DOI_title"},
    )
    doi_users: Optional[str] = Field(
        None,
        description="Users of the DOI. Comma separated string",
        json_schema_extra={"icat_name": "DOI_users"},
    )
    project_name: Optional[str] = Field(
        None,
        description="Name of project",
        json_schema_extra={"icat_name": "Project_name"},
    )
    machine: Optional[str] = Field(
        None, description="Name of the machine that collects the data"
    )
    software: Optional[str] = Field(
        None, description="Name of the software that collects the data"
    )
    group_by: Optional[str] = Field(
        None,
        description="Comma separated list of parameters name that will be used to "
        "represent the data acquisition as a tree. Mostly for visualization purposes",
    )
    SAXS: Optional[IcatSaxs] = Field(None, description="Small-Angle X-ray Scattering")
    MX: Optional[IcatMx] = Field(None, description="Macromolecular Crystallography")
    EM: Optional[IcatEm] = Field(None, description="Electron Microscopy")
    PTYCHO: Optional[IcatPtycho] = Field(None, description="Ptychographic Imaging")
    FLUO: Optional[IcatFluo] = Field(None, description="X-ray Fluorescence Imaging")
    TOMO: Optional[IcatTomo] = Field(None, description="Tomography")
    MRT: Optional[IcatMrt] = Field(None, description="Microbeam Radiation Therapy")
    HOLO: Optional[IcatHolo] = Field(None, description="X-ray Holography")
    SSX: Optional[IcatSsx] = Field(
        None, description="Serial Synchrotron Crystallography"
    )
    WAXS: Optional[IcatWaxs] = Field(None, description="Wide-Angle X-ray Scattering")
    HTXRPD: Optional[IcatHtxrpd] = Field(
        None, description="High-Throughput X-ray Powder Diffraction"
    )
    SXDM: Optional[IcatSxdm] = Field(
        None, description="Scanning X-ray Diffraction Microscopy"
    )
    BCDI: Optional[IcatBcdi] = Field(
        None, description="Bragg Coherent Diffraction Imaging"
    )
    SCXRD: Optional[IcatScxrd] = Field(
        None, description="Single Crystal X-ray Diffraction"
    )
    sample: IcatSample = Field(
        ...,
        description="Description and metadata about the physical sample used in the experiment.",
    )
    fresnel_zone_plate: Optional[IcatFresnelZonePlate] = Field(
        None,
        description="Fresnel Zone Plate information",
        json_schema_extra={"icat_name": "Fresnel__zone__plate"},
    )
    aperture: Optional[IcatAperture] = Field(
        None, description="Aperture settings or characteristics"
    )
    mirror: Optional[IcatMirror] = Field(
        None, description="Mirror configuration or parameters"
    )
    instrument: Optional[IcatInstrument] = Field(
        None, description="Instrument configuration and setting"
    )
    notes: Optional[IcatNotes] = Field(
        None, description="Free-form user notes or annotations"
    )
    process: Optional[IcatProcess] = Field(
        None, description="Post-processing metadata or logs"
    )
    workflow: Optional[IcatWorkflow] = Field(
        None, description="Workflow steps or automation pipeline"
    )
    external_references: Optional[IcatExternalReferences] = Field(
        None, description="Linked datasets, publications, or IDs"
    )
