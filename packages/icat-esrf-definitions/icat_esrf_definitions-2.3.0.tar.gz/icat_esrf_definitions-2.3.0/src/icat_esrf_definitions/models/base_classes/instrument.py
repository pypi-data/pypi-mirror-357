from typing import Optional

from pydantic import Field

from ..base.nexus import NXattenuator
from ..base.nexus import NXbeam
from ..base.nexus import NXcollection
from ..base.nexus import NXcrystal
from ..base.nexus import NXdetector
from ..base.nexus import NXenvironment
from ..base.nexus import NXinsertion_device
from ..base.nexus import NXinstrument
from ..base.nexus import NXmonochromator
from ..base.nexus import NXpositioner
from ..base.nexus import NXsensor
from ..base.nexus import NXslit
from ..base.nexus import NXsource
from ..base.nexus import NXxraylens
from ..base.quantity import DEGREES
from ..base.quantity import JOULES
from ..base.quantity import METERS
from ..base.quantity import SECONDS


class IcatInstrumentSource(NXsource):
    mode: Optional[str] = Field(None, description="")
    current: Optional[str] = Field(None, description="")
    distance: Optional[str] = Field(
        None,
        description="Effective distance from sample Distance as seen by radiation from sample. "
        "This number should be negative to signify that it is upstream of the sample.",
    )
    name: Optional[str] = Field(None, description="Name of source")
    type: Optional[str] = Field(
        None,
        description="type of radiation source (pick one from the enumerated list and spell exactly). "
        "Spallation Neutron Source, Pulsed Reactor Neutron Source, Reactor Neutron Source, "
        "Synchrotron X-ray Source, Pulsed Muon Source, Rotating Anode X-ray, Fixed Tube X-ray, "
        "UV Laser, Free-Electron Laser, Optical Laser, Ion Source, UV Plasma Source",
    )
    probe: Optional[str] = Field(None, description="type of radiation probe")
    emittance_x: Optional[str] = Field(
        None, description="Source emittance (nm-rad) in X (horizontal) direction."
    )
    emittance_y: Optional[str] = Field(
        None, description="Source emittance (nm-rad) in Y (horizontal) direction."
    )


class IcatInstrumentVariables(NXcollection):
    name: Optional[str] = Field(None, description="")
    value: Optional[str] = Field(None, description="")


class IcatInstrumentLaser(NXsource):
    name: Optional[str] = Field(
        None,
        description="https://manual.nexusformat.org/classes/base_classes/NXsource.html#nxsource-name-field",
    )
    type: Optional[str] = Field(
        None,
        description="Type of source. "
        "https://manual.nexusformat.org/classes/base_classes/NXsource.html#nxsource-type-field",
    )
    probe: Optional[str] = Field(
        None,
        description="Type of radiation. "
        "https://manual.nexusformat.org/classes/base_classes/NXsource.html#nxsource-probe-field",
    )
    energy: Optional[JOULES] = Field(
        None,
        description="Energy emitted in a single pulse. "
        "https://manual.nexusformat.org/classes/base_classes/NXsource.html#nxsource-energy-field",
    )
    wavelength: Optional[METERS] = Field(
        None, description="Wavelength emitted in a single pulse."
    )
    repetition_rate: Optional[float] = Field(
        None, description="Pulse Repetition Frequency."
    )
    pulse_width: Optional[SECONDS] = Field(
        None,
        description="Time between the start and end of a single pulse. "
        "https://manual.nexusformat.org/classes/base_classes/NXsource.html#nxsource-pulse-width-field",
    )
    delay: Optional[SECONDS] = Field(
        None,
        description="The time of the start of the laser pulse with respect to the start of the measurement (T=0)",
    )


class IcatInstrumentMonochromatorCrystal(NXcrystal):
    usage: Optional[str] = Field(None, description="")
    d_spacing: Optional[str] = Field(None, description="")
    type: Optional[str] = Field(None, description="")
    reflection: Optional[str] = Field(None, description="")


class IcatInstrumentOpticsPositioners(NXpositioner):
    name: Optional[str] = Field(None, description="")
    value: Optional[str] = Field(None, description="")


class IcatInstrumentPositioners(NXpositioner):
    name: Optional[str] = Field(None, description="")
    value: Optional[str] = Field(None, description="")


class IcatInstrumentPrimarySlit(NXslit):
    name: Optional[str] = Field(None, description="")
    vertical_gap: Optional[str] = Field(None, description="")
    vertical_offset: Optional[str] = Field(None, description="")
    horizontal_gap: Optional[str] = Field(None, description="")
    horizontal_offset: Optional[str] = Field(None, description="")
    blade_up: Optional[str] = Field(None, description="")
    blade_down: Optional[str] = Field(None, description="")
    blade_front: Optional[str] = Field(None, description="")
    blade_back: Optional[str] = Field(None, description="")


class IcatInstrumentSecondarySlit(NXslit):
    name: Optional[str] = Field(None, description="")
    vertical_gap: Optional[str] = Field(None, description="")
    vertical_offset: Optional[str] = Field(None, description="")
    horizontal_gap: Optional[str] = Field(None, description="")
    horizontal_offset: Optional[str] = Field(None, description="")
    blade_up: Optional[str] = Field(None, description="")
    blade_down: Optional[str] = Field(None, description="")
    blade_front: Optional[str] = Field(None, description="")
    blade_back: Optional[str] = Field(None, description="")


class IcatInstrumentSlits(NXslit):
    name: Optional[str] = Field(None, description="")
    vertical_gap: Optional[str] = Field(None, description="")
    vertical_offset: Optional[str] = Field(None, description="")
    horizontal_gap: Optional[str] = Field(None, description="")
    horizontal_offset: Optional[str] = Field(None, description="")
    blade_up: Optional[str] = Field(None, description="")
    blade_down: Optional[str] = Field(None, description="")
    blade_front: Optional[str] = Field(None, description="")
    blade_back: Optional[str] = Field(None, description="")


class IcatInstrumentDetectorRois(NXcollection):
    name: Optional[str] = Field(None, description="")
    value: Optional[str] = Field(
        None,
        description="Parameters defining the ROI. Format: R1P1,R1P2 R2P1,R2P2 ... RnP1,RnP2",
    )


class IcatInstrumentEnvironmentSensors(NXsensor):
    name: Optional[str] = Field(None, description="")
    value: Optional[str] = Field(None, description="")


class IcatInstrumentInsertionDeviceGap(NXpositioner):
    name: Optional[str] = Field(None, description="")
    value: Optional[str] = Field(None, description="")


class IcatInstrumentInsertionDeviceTaper(NXpositioner):
    name: Optional[str] = Field(None, description="")
    value: Optional[str] = Field(None, description="")


class IcatInstrumentInsertionDevice(NXinsertion_device):
    gap: Optional[IcatInstrumentInsertionDeviceGap] = Field(
        None, description="", json_schema_extra={"icat_name": "_gap"}
    )
    taper: Optional[IcatInstrumentInsertionDeviceTaper] = Field(
        None, description="", json_schema_extra={"icat_name": "_taper"}
    )


class IcatInstrumentDetectorPositioners(NXpositioner):
    name: Optional[str] = Field(None, description="")
    value: Optional[str] = Field(None, description="")


class IcatInstrumentAttenuatorPositioners(NXpositioner):
    name: Optional[str] = Field(None, description="")
    value: Optional[str] = Field(None, description="")


class IcatInstrumentBeam(NXbeam):
    incident_beam_divergence: Optional[DEGREES] = Field(
        None, description="Beam crossfire in degrees parallel to the laboratory X axis"
    )
    horizontal_incident_beam_divergence: Optional[DEGREES] = Field(
        None,
        description="Horizontal beam crossfire in degrees parallel to the laboratory X axis",
    )
    vertical_incident_beam_divergence: Optional[DEGREES] = Field(
        None,
        description="Vertical beam crossfire in degrees parallel to the laboratory X axis",
    )
    final_polarization: Optional[str] = Field(
        None,
        description="Polarization vector on leaving beamline component using Stokes notation (see incident_polarization_stokes).",
    )


class IcatInstrumentXraylens(NXxraylens):
    lens_geometry: Optional[str] = Field(
        None,
        description="Geometry of the lens. Any of these values:paraboloid,spherical,elliptical,hyperbolical",
    )
    focus_type: Optional[str] = Field(
        None,
        description="The type of focus of the lens. Any of these values:line,point",
    )
    lens_thickness: Optional[str] = Field(None, description="Thickness of the lens")
    lens_length: Optional[str] = Field(None, description="Length of the lens")
    curvature: Optional[str] = Field(
        None,
        description="Radius of the curvature as measured in the middle of the lens",
    )
    aperture: Optional[str] = Field(None, description="Diameter of the lens")
    number_of_lenses: Optional[int] = Field(
        None, description="Number of lenses that make up the compound lens"
    )
    lens_material: Optional[str] = Field(
        None, description="Material used to make the lens"
    )


class IcatInstrumentAttenuator(NXattenuator):
    type: Optional[str] = Field(None, description="")
    thickness: Optional[str] = Field(None, description="")
    status: Optional[str] = Field(None, description="")
    distance: Optional[str] = Field(None, description="")
    positioners: Optional[IcatInstrumentAttenuatorPositioners] = Field(
        None, description=""
    )


class IcatInstrumentAttenuatorWithDescription(IcatInstrumentAttenuator):
    # TODO: probably all IcatInstrumentAttenuator have a description
    description: Optional[str] = Field(None, description="")


class IcatInstrumentMonochromator(NXmonochromator):
    name: Optional[str] = Field(None, description="")
    energy: Optional[str] = Field(None, description="")
    wavelength: Optional[str] = Field(None, description="")
    crystal: Optional[IcatInstrumentMonochromatorCrystal] = Field(None, description="")


class IcatInstrumentOptics(NXcollection):
    positioners: Optional[IcatInstrumentOpticsPositioners] = Field(None, description="")


class IcatInstrumentEnvironment(NXenvironment):
    sensors: Optional[IcatInstrumentEnvironmentSensors] = Field(
        None, description="Parameters for controlling external conditions"
    )


class IcatInstrumentDetector(NXdetector):
    name: Optional[str] = Field(None, description="Name of the detector")
    type: Optional[str] = Field(
        None,
        description="Description of type such as He3 gas cylinder, He3 PSD, scintillator, "
        "fission chamber, proportion counter, ion chamber, ccd, pixel, image plate, CMOS, …",
    )
    manufacturer: Optional[str] = Field(
        None, description="Name of the manufacturer of the detector. Example: Dectris"
    )
    model: Optional[str] = Field(
        None, description="Model of the detector. Example: Pilatus3_6M"
    )
    preset_time: Optional[float] = Field(None, description="Desired measuring time")
    live_time: Optional[float] = Field(
        None,
        description="Time the detector has been actually measuring (elapsed_time - dead_time)",
        json_schema_extra={"icat_name": "elapsed_live_time"},
    )
    elapsed_time: Optional[float] = Field(
        None,
        description="Time elapsed between start and stop of the measurement",
        json_schema_extra={"icat_name": "elapsed_real_time"},
    )
    calibration: Optional[str] = Field(
        None,
        description="For MCA detectors, coefficients a, b, c to compute a scale based on channel number as a + b * x + c * x * x ",
    )
    description: Optional[str] = Field(
        None, description="name/manufacturer/model/etc. information"
    )
    local_name: Optional[str] = Field(None, description="Local name for the detector")
    x_pixel_size: Optional[str] = Field(
        None,
        description="Size of each detector pixel. If it is scalar all pixels are the same size.",
    )
    y_pixel_size: Optional[str] = Field(
        None,
        description="Size of each detector pixel. If it is scalar all pixels are the same size.",
    )
    calibration_date: Optional[str] = Field(None, description="")
    layout: Optional[str] = Field(
        None,
        description="How the detector is represented. Any of these values: point | linear | area",
    )
    beam_center_x: Optional[str] = Field(
        None,
        description="This is the x position where the direct beam would hit the detector. "
        "This is a length and can be outside of the actual detector. The length can be in physical "
        "units or pixels as documented by the units attribute.",
    )
    beam_center_y: Optional[str] = Field(
        None,
        description="This is the y position where the direct beam would hit the detector. "
        "This is a length and can be outside of the actual detector. The length can be in physical "
        "units or pixels as documented by the units attribute.",
    )
    flatfield_applied: Optional[str] = Field(
        None,
        description="True when the flat field correction has been applied in the electronics, false otherwise.",
        json_schema_extra={"icat_name": "flat_field_applied"},
    )
    pixel_mask: Optional[str] = Field(
        None, description="The 32-bit pixel mask for the detector"
    )
    pixel_mask_applied: Optional[str] = Field(
        None,
        description="True when the pixel mask correction has been applied in the electronics, false otherwise.",
    )
    countrate_correction_applied: Optional[str] = Field(
        None,
        description="Counting detectors usually are not able to measure all incoming particles, especially at "
        "higher count-rates. Count-rate correction is applied to account for these errors.",
    )
    saturation_value: Optional[str] = Field(
        None,
        description="The value at which the detector goes into saturation. Especially common to CCD detectors, "
        "the data is known to be invalid above this value.",
    )
    threshold_energy: Optional[str] = Field(
        None,
        description="Single photon counter detectors can be adjusted for a certain energy range in which they "
        "work optimally. This is the energy setting for this.",
    )
    sensor_thickness: Optional[str] = Field(None, description="")
    sensor_material: Optional[str] = Field(
        None,
        description="At times, radiation is not directly sensed by the detector. Rather, the detector might sense "
        "the output from some converter like a scintillator. This is the name of this converter material.",
    )
    bit_depth_readout: Optional[str] = Field(
        None,
        description="How many bits the electronics reads per pixel. With CCD’s and single photon counting detectors, "
        "this must not align with traditional integer sizes. This can be 4, 8, 12, 14, 16, ",
    )
    distance: Optional[str] = Field(
        None,
        description="This is the distance to the previous component in the instrument; most often the sample. "
        "The usage depends on the nature of the detector: Most often it is the distance of the detector assembly. "
        "But there are irregular detectors. In this case the distance must be specified for each detector pixel.",
    )
    frame_time: Optional[str] = Field(
        None,
        description="This is time for each frame. This is exposure_time + readout time.",
    )
    positioners: Optional[IcatInstrumentDetectorPositioners] = Field(
        None, description=""
    )
    rois: Optional[IcatInstrumentDetectorRois] = Field(
        None, description="Names and parameters describing the ROIs applied"
    )
    acquisition_mode: Optional[str] = Field(
        None,
        description="The acquisition mode of the detector. Any of these values: "
        "gated,triggered,summed,event,histogrammed,decimated",
    )


class IcatInstrument(NXinstrument):
    name: Optional[str] = Field(
        None,
        description="ID of the beamline",
        json_schema_extra={"icat_name": "beamlineID"},
    )
    variables: Optional[IcatInstrumentVariables] = Field(None, description="")
    positioners: Optional[IcatInstrumentPositioners] = Field(None, description="")
    beam: Optional[IcatInstrumentBeam] = Field(None, description="")
    monochromator: Optional[IcatInstrumentMonochromator] = Field(None, description="")
    source: Optional[IcatInstrumentSource] = Field(None, description="")
    laser01: Optional[IcatInstrumentLaser] = Field(None, description="")
    laser02: Optional[IcatInstrumentLaser] = Field(None, description="")
    primary_slit: Optional[IcatInstrumentPrimarySlit] = Field(
        None,
        description="",
        json_schema_extra={"icat_name": "slit_primary"},
    )
    secondary_slit: Optional[IcatInstrumentSecondarySlit] = Field(
        None,
        description="",
        json_schema_extra={"icat_name": "slit_secondary"},
    )
    slits: Optional[IcatInstrumentSlits] = Field(None, description="")
    xraylens01: Optional[IcatInstrumentXraylens] = Field(None, description="")
    xraylens02: Optional[IcatInstrumentXraylens] = Field(None, description="")
    xraylens03: Optional[IcatInstrumentXraylens] = Field(None, description="")
    xraylens04: Optional[IcatInstrumentXraylens] = Field(None, description="")
    xraylens05: Optional[IcatInstrumentXraylens] = Field(None, description="")
    xraylens06: Optional[IcatInstrumentXraylens] = Field(None, description="")
    xraylens07: Optional[IcatInstrumentXraylens] = Field(None, description="")
    xraylens08: Optional[IcatInstrumentXraylens] = Field(None, description="")
    xraylens09: Optional[IcatInstrumentXraylens] = Field(None, description="")
    xraylens10: Optional[IcatInstrumentXraylens] = Field(None, description="")
    attenuator01: Optional[IcatInstrumentAttenuatorWithDescription] = Field(
        None, description=""
    )
    attenuator02: Optional[IcatInstrumentAttenuator] = Field(None, description="")
    attenuator03: Optional[IcatInstrumentAttenuator] = Field(None, description="")
    attenuator04: Optional[IcatInstrumentAttenuator] = Field(None, description="")
    attenuator05: Optional[IcatInstrumentAttenuator] = Field(None, description="")
    attenuator06: Optional[IcatInstrumentAttenuator] = Field(None, description="")
    attenuator07: Optional[IcatInstrumentAttenuator] = Field(None, description="")
    attenuator08: Optional[IcatInstrumentAttenuator] = Field(None, description="")
    attenuator09: Optional[IcatInstrumentAttenuator] = Field(None, description="")
    attenuator10: Optional[IcatInstrumentAttenuator] = Field(None, description="")
    attenuator11: Optional[IcatInstrumentAttenuator] = Field(None, description="")
    attenuator12: Optional[IcatInstrumentAttenuator] = Field(None, description="")
    attenuator13: Optional[IcatInstrumentAttenuator] = Field(None, description="")
    attenuator14: Optional[IcatInstrumentAttenuator] = Field(None, description="")
    attenuator15: Optional[IcatInstrumentAttenuator] = Field(None, description="")
    insertion_device: Optional[IcatInstrumentInsertionDevice] = Field(
        None, description=""
    )
    optics: Optional[IcatInstrumentOptics] = Field(None, description="")
    environment: Optional[IcatInstrumentEnvironment] = Field(None, description="")
    detector01: Optional[IcatInstrumentDetector] = Field(None, description="")
    detector02: Optional[IcatInstrumentDetector] = Field(None, description="")
    detector03: Optional[IcatInstrumentDetector] = Field(None, description="")
    detector04: Optional[IcatInstrumentDetector] = Field(None, description="")
    detector05: Optional[IcatInstrumentDetector] = Field(None, description="")
    detector06: Optional[IcatInstrumentDetector] = Field(None, description="")
    detector07: Optional[IcatInstrumentDetector] = Field(None, description="")
    detector08: Optional[IcatInstrumentDetector] = Field(None, description="")
    detector09: Optional[IcatInstrumentDetector] = Field(None, description="")
    detector10: Optional[IcatInstrumentDetector] = Field(None, description="")
