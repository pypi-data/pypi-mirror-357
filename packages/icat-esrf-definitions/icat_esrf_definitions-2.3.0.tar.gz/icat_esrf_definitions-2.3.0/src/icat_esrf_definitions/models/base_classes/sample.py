from typing import Optional

from pydantic import Field

from ..base.nexus import NXcollection
from ..base.nexus import NXenvironment
from ..base.nexus import NXnote
from ..base.nexus import NXpositioner
from ..base.nexus import NXsample
from ..base.nexus import NXsensor
from ..base.nexus import NXsubentry
from ..base.quantity import CELSIUS
from ..base.quantity import CENTIMETERS
from ..base.quantity import KILOGRAMS
from ..base.quantity import YEARS


class IcatSampleChanger(NXcollection):
    position: Optional[str] = Field(None, description="Sample changer position")
    name: Optional[str] = Field(
        None,
        description="Name (or ideally identifier) for a batch (series of data collections)",
    )


class IcatSampleEnvironmentSensors(NXsensor):
    name: Optional[str] = Field(None, description="")
    value: Optional[str] = Field(None, description="")


class IcatSampleLocalisation(NXcollection):
    name: Optional[str] = Field(None, description="Name of the localisation")
    country: Optional[str] = Field(None, description="Country")
    continental_region: Optional[str] = Field(None, description="Continental region")


class IcatSampleNotes(NXnote):
    notes: Optional[str] = Field(None, json_schema_extra={"record": "final"})


class IcatSamplePaleoClassification(NXcollection):
    species: Optional[str] = Field(None, description="Species")
    material_type: Optional[str] = Field(None, description="Material Type")
    clade1: Optional[str] = Field(None, description="Clade 1")
    clade2: Optional[str] = Field(None, description="Clade 2")
    clade3: Optional[str] = Field(None, description="Clade 3")
    clade4: Optional[str] = Field(None, description="Clade 4")
    clade5: Optional[str] = Field(None, description="Clade 5")
    clade6: Optional[str] = Field(None, description="Clade 6")


class IcatSamplePaleoGeologicalTime(NXcollection):
    formation: Optional[str] = Field(None, description="Formation")
    era: Optional[str] = Field(None, description="Era")
    period: Optional[str] = Field(None, description="Period")
    epoch: Optional[str] = Field(None, description="Epoch")


class IcatSamplePatient(NXcollection):
    institute: Optional[str] = Field(
        None, description="Institute of origin of the patient"
    )
    number: Optional[int] = Field(None, description="Number of the patient")
    age: Optional[YEARS] = Field(None, description="Age of the patient")
    sex: Optional[str] = Field(None, description="Sex of the patient")
    weight: Optional[KILOGRAMS] = Field(None, description="Weight of the patient")
    size: Optional[CENTIMETERS] = Field(None, description="Size of the patient")
    info: Optional[str] = Field(None, description="Information about the patient")
    organ_name: Optional[str] = Field(None, description="Name of the organ")
    organ_description: Optional[str] = Field(None, description="Name of the organ")


class IcatSamplePositioners(NXpositioner):
    name: Optional[str] = Field(None, description="")
    value: Optional[str] = Field(None, description="")


class IcatSampleProtein(NXcollection):
    acronym: Optional[str] = Field(None, description="Acronym of the protein")
    name: Optional[str] = Field(None, description="Acronym of the protein")


class IcatSampleTrackingContainer(NXcollection):
    type: Optional[str] = Field(
        None, description="Type of container. Example: unipuck, spinepuck, etc..."
    )
    capacity: Optional[str] = Field(
        None,
        description="Total capacity of the container",
        json_schema_extra={"icat_name": "capaticy"},
    )
    position: Optional[str] = Field(
        None, description="Position of the sample within the container"
    )
    id: Optional[str] = Field(None, description="Identifier of the container")
    name: Optional[str] = Field(
        None,
        description="Name of the container where the sample is. Example: puck_name",
    )


class IcatSampleTrackingParcel(NXsubentry):
    id: Optional[str] = Field(None, description="Identifier of the parcel")
    name: Optional[str] = Field(
        None, description="Name of the parcel where the sample has been shipped"
    )
    storage_condition: Optional[CELSIUS] = Field(
        None, description="Storage conditions of the parcel. Example: -80 degrees"
    )


class IcatSampleTrackingShipment(NXsubentry):
    id: Optional[str] = Field(None, description="Identifier of the shipment")
    name: Optional[str] = Field(None, description="Name of the shipment")


class IcatSampleEnvironment(NXenvironment):
    name: Optional[str] = Field(
        None, description="Apparatus identification code/model number; e.g. OC100 011"
    )
    type: Optional[str] = Field(
        None,
        description="Type of apparatus. This could be the SE codes in scheduling database; e.g. OC/100",
    )
    description: Optional[str] = Field(
        None,
        description="Description of the apparatus; e.g. 100mm bore orange cryostat with Roots pump",
    )
    sensors: Optional[IcatSampleEnvironmentSensors] = Field(
        None, description="Parameters for controlling external conditions"
    )


class IcatSamplePaleo(NXcollection):
    scientific_domain: Optional[str] = Field(None, description="Scientific domain")
    repository_institution: Optional[str] = Field(
        None, description="Repository institution"
    )
    collection_number: Optional[str] = Field(
        None, description="Collection number in the repository institution"
    )
    geological_time: Optional[IcatSamplePaleoGeologicalTime] = Field(
        None, description=""
    )
    classification: Optional[IcatSamplePaleoClassification] = Field(
        None, description=""
    )


class IcatSampleTracking(NXsubentry):
    shipment: Optional[IcatSampleTrackingShipment] = Field(None, description="")
    parcel: Optional[IcatSampleTrackingParcel] = Field(None, description="")
    container: Optional[IcatSampleTrackingContainer] = Field(None, description="")


class IcatSample(NXsample):
    name: str = Field(
        ..., description="Name of the sample", json_schema_extra={"record": "final"}
    )
    description: Optional[str] = Field(
        None,
        description="Description of the sample",
        json_schema_extra={"record": "final"},
    )
    distance: Optional[str] = Field(
        None,
        description="Translation of the sample along the Z-direction of the laboratory coordinate system",
        json_schema_extra={"record": "final"},
    )
    support: Optional[str] = Field(
        None,
        description="Name of the support used to collect the sample. It can be a chip, plate, jet, etc...",
        json_schema_extra={"record": "final"},
    )
    notes: Optional[IcatSampleNotes] = Field(
        None,
        description="",
        json_schema_extra={"icat_name": ""},
    )
    positioners: Optional[IcatSamplePositioners] = Field(None, description="")
    protein: Optional[IcatSampleProtein] = Field(None, description="")
    changer: Optional[IcatSampleChanger] = Field(None, description="")
    patient: Optional[IcatSamplePatient] = Field(None, description="")
    environment: Optional[IcatSampleEnvironment] = Field(None, description="")
    tracking: Optional[IcatSampleTracking] = Field(None, description="")
    localisation: Optional[IcatSampleLocalisation] = Field(None, description="")
    paleo: Optional[IcatSamplePaleo] = Field(None, description="")
    situation: Optional[str] = Field(
        None,
        description="The atmosphere will be one of the components, which is where "
        "its details will be stored; the relevant components will be indicated by "
        "the entry in the sample_component member.",
        json_schema_extra={"record": "final"},
    )
    ub_matrix: Optional[str] = Field(
        None,
        description="UB matrix of single crystal sample using Busing-Levy convention: "
        "W. R. Busing and H. A. Levy (1967). Acta Cryst. 22, 457-464. This is the multiplication "
        "of the orientation_matrix, given above, with the BB matrix which can be derived from the lattice constants.",
        json_schema_extra={"record": "final"},
    )
    temperature_env: Optional[str] = Field(
        None,
        description="Additional sample temperature environment information",
        json_schema_extra={"record": "final"},
    )
    chemical_formula: Optional[str] = Field(
        None,
        description="Chemical formula of the sample",
        json_schema_extra={"record": "final"},
    )
