from typing import Optional

from pydantic import Field

from ..base.nexus import NXcollection
from ..base.nexus import NXsubentry
from ..base.quantity import ANGSTROMS
from ..base.quantity import DEGREES
from ..base.quantity import MILLIMETERS
from ..base.quantity import PHOTON_FLUX
from ..base.quantity import SECONDS


class IcatMxAutoprocintegrationScaling(NXcollection):
    overall_resolution_limit_low: Optional[str] = Field(None, description="")
    overall_resolution_limit_high: Optional[str] = Field(None, description="")
    overall_r_merge: Optional[str] = Field(None, description="")
    overall_r_meas_within_IPlus_IMinus: Optional[str] = Field(None, description="")
    overall_r_meas_all_IPlus_IMinus: Optional[str] = Field(None, description="")
    overall_r_pim_within_IPlus_IMinus: Optional[str] = Field(None, description="")
    overall_r_pim_all_IPlus_IMinus: Optional[str] = Field(None, description="")
    overall_fractional_partial_bias: Optional[str] = Field(None, description="")
    overall_n_total_observations: Optional[str] = Field(None, description="")
    overall_n_total_unique_observations: Optional[str] = Field(None, description="")
    overall_mean_I_over_sigI: Optional[str] = Field(None, description="")
    overall_completeness: Optional[str] = Field(None, description="")
    overall_multiplicity: Optional[str] = Field(None, description="")
    overall_anomalous_completeness: Optional[str] = Field(None, description="")
    overall_anomalous_multiplicity: Optional[str] = Field(None, description="")
    overall_anomalous: Optional[str] = Field(None, description="")
    overall_cc_half: Optional[str] = Field(None, description="")
    overall_ccAno: Optional[str] = Field(None, description="")
    overall_sigAno: Optional[str] = Field(None, description="")
    overall_isa: Optional[str] = Field(None, description="")
    overall_completeness_spherical: Optional[str] = Field(None, description="")
    overall_completeness_ellipsoidal: Optional[str] = Field(None, description="")
    overall_anomalous_completeness_spherical: Optional[str] = Field(
        None, description=""
    )
    overall_anomalous_completeness_ellipsoidal: Optional[str] = Field(
        None, description=""
    )
    inner_resolution_limit_low: Optional[str] = Field(None, description="")
    inner_resolution_limit_high: Optional[str] = Field(None, description="")
    inner_r_merge: Optional[str] = Field(None, description="")
    inner_r_meas_within_IPlus_IMinus: Optional[str] = Field(None, description="")
    inner_r_meas_all_IPlus_IMinus: Optional[str] = Field(None, description="")
    inner_r_pim_within_IPlus_IMinus: Optional[str] = Field(None, description="")
    inner_r_pim_all_IPlus_IMinus: Optional[str] = Field(None, description="")
    inner_fractional_partial_bias: Optional[str] = Field(None, description="")
    inner_n_total_observations: Optional[str] = Field(None, description="")
    inner_n_total_unique_observations: Optional[str] = Field(None, description="")
    inner_mean_I_over_sigI: Optional[str] = Field(None, description="")
    inner_completeness: Optional[str] = Field(None, description="")
    inner_multiplicity: Optional[str] = Field(None, description="")
    inner_anomalous_completeness: Optional[str] = Field(None, description="")
    inner_anomalous_multiplicity: Optional[str] = Field(None, description="")
    inner_anomalous: Optional[str] = Field(None, description="")
    inner_cc_half: Optional[str] = Field(None, description="")
    inner_ccAno: Optional[str] = Field(None, description="")
    inner_sigAno: Optional[str] = Field(None, description="")
    inner_isa: Optional[str] = Field(None, description="")
    inner_completeness_spherical: Optional[str] = Field(None, description="")
    inner_completeness_ellipsoidal: Optional[str] = Field(None, description="")
    inner_anomalous_completeness_spherical: Optional[str] = Field(None, description="")
    inner_anomalous_completeness_ellipsoidal: Optional[str] = Field(
        None, description=""
    )
    outer_resolution_limit_low: Optional[str] = Field(None, description="")
    outer_resolution_limit_high: Optional[str] = Field(None, description="")
    outer_r_merge: Optional[str] = Field(None, description="")
    outer_r_meas_within_IPlus_IMinus: Optional[str] = Field(None, description="")
    outer_r_meas_all_IPlus_IMinus: Optional[str] = Field(None, description="")
    outer_r_pim_within_IPlus_IMinus: Optional[str] = Field(None, description="")
    outer_r_pim_all_IPlus_IMinus: Optional[str] = Field(None, description="")
    outer_fractional_partial_bias: Optional[str] = Field(None, description="")
    outer_n_total_observations: Optional[str] = Field(None, description="")
    outer_n_total_unique_observations: Optional[str] = Field(None, description="")
    outer_mean_I_over_sigI: Optional[str] = Field(None, description="")
    outer_completeness: Optional[str] = Field(None, description="")
    outer_multiplicity: Optional[str] = Field(None, description="")
    outer_anomalous_completeness: Optional[str] = Field(None, description="")
    outer_anomalous_multiplicity: Optional[str] = Field(None, description="")
    outer_anomalous: Optional[str] = Field(None, description="")
    outer_cc_half: Optional[str] = Field(None, description="")
    outer_ccAno: Optional[str] = Field(None, description="")
    outer_sigAno: Optional[str] = Field(None, description="")
    outer_isa: Optional[str] = Field(None, description="")
    outer_completeness_spherical: Optional[str] = Field(None, description="")
    outer_completeness_ellipsoidal: Optional[str] = Field(None, description="")
    outer_anomalous_completeness_spherical: Optional[str] = Field(None, description="")
    outer_anomalous_completeness_ellipsoidal: Optional[str] = Field(
        None, description=""
    )


class IcatMxMrLigandfitting(NXcollection):
    ligand_FOFC_CC: Optional[str] = Field(
        None, description="Ligand FOFC_CC", json_schema_extra={"record": "final"}
    )
    R_free: Optional[str] = Field(
        None, description="Free-r", json_schema_extra={"record": "final"}
    )
    R_cryst: Optional[str] = Field(
        None, description="R crystal", json_schema_extra={"record": "final"}
    )
    B_factor: Optional[str] = Field(
        None, description="B factor", json_schema_extra={"record": "final"}
    )
    occupancy: Optional[str] = Field(
        None, description="Occupancy", json_schema_extra={"record": "final"}
    )
    PDB_file: Optional[str] = Field(
        None, description="pdb file path", json_schema_extra={"record": "final"}
    )
    MTZ_file: Optional[str] = Field(
        None, description="mtz file", json_schema_extra={"record": "final"}
    )
    PNG_2FOFC: Optional[str] = Field(
        None,
        description="snapshot of the ligand in 2FO-FC electron density",
        json_schema_extra={"record": "final"},
    )
    PNG_FOFC: Optional[str] = Field(
        None,
        description="snapshot of the ligand in FO-FC electron density",
        json_schema_extra={"record": "final"},
    )
    GIF_file: Optional[str] = Field(
        None,
        description="animated GIF of the ligand in FO-FC electron density",
        json_schema_extra={"record": "final"},
    )
    ligand_XYZ: Optional[str] = Field(
        None,
        description="x,y,z coordinates of the ligand",
        json_schema_extra={"record": "final"},
    )
    ligand_name: Optional[str] = Field(
        None, description="name of the ligand", json_schema_extra={"record": "final"}
    )
    MAP_FOFC: Optional[str] = Field(
        None, description="MAP_FOFC file path", json_schema_extra={"record": "final"}
    )
    MAP_2FOFC: Optional[str] = Field(
        None, description="MAP_2FOFC file path", json_schema_extra={"record": "final"}
    )


class IcatMxMrPhasing(NXcollection):
    source: Optional[str] = Field(
        None,
        description="Describes the pdb suource: Alphafold, user, unit cell",
        json_schema_extra={"record": "final"},
    )
    search_model: Optional[str] = Field(
        None,
        description="Identifier to the search model. It can be a link",
        json_schema_extra={"record": "final"},
    )
    space_group: Optional[str] = Field(
        None, description="Phasing space group", json_schema_extra={"record": "final"}
    )
    number_of_search_models_found: Optional[str] = Field(
        None, description="Models found", json_schema_extra={"record": "final"}
    )
    best_RFZ: Optional[str] = Field(
        None, description="Best RFZ", json_schema_extra={"record": "final"}
    )
    best_TFZ: Optional[str] = Field(
        None, description="Best TTZ", json_schema_extra={"record": "final"}
    )
    LLG: Optional[str] = Field(
        None, description="Best LLG", json_schema_extra={"record": "final"}
    )
    monomer_form_count: Optional[str] = Field(
        None, description="Number of monomers", json_schema_extra={"record": "final"}
    )
    RFZ_list: Optional[str] = Field(
        None, description="List of RFZ", json_schema_extra={"record": "final"}
    )
    TFZ_list: Optional[str] = Field(
        None, description="List of TFZ", json_schema_extra={"record": "final"}
    )
    PDB_file: Optional[str] = Field(
        None, description="pdb file path", json_schema_extra={"record": "final"}
    )
    MTZ_file: Optional[str] = Field(
        None, description="MTZ file path", json_schema_extra={"record": "final"}
    )
    MAP_2FOFC: Optional[str] = Field(
        None, description="2FOFC map file path", json_schema_extra={"record": "final"}
    )
    MAP_FOFC: Optional[str] = Field(
        None, description="FOFC map file path", json_schema_extra={"record": "final"}
    )


class IcatMxMrRefinement(NXcollection):
    R_free: Optional[str] = Field(
        None, description="Free-r", json_schema_extra={"record": "final"}
    )
    R_cryst: Optional[str] = Field(
        None, description="R crystal", json_schema_extra={"record": "final"}
    )
    PDB_file: Optional[str] = Field(
        None, description="List of TFZ", json_schema_extra={"record": "final"}
    )
    MTZ_file: Optional[str] = Field(
        None, description="List of TFZ", json_schema_extra={"record": "final"}
    )
    MAP_FOFC: Optional[str] = Field(
        None, description="MAP_FOFC file path", json_schema_extra={"record": "final"}
    )
    MAP_2FOFC: Optional[str] = Field(
        None, description="MAP_2FOFC file path", json_schema_extra={"record": "final"}
    )


class IcatMxSad(NXcollection):
    min_resolution: Optional[ANGSTROMS] = Field(
        None,
        description="SAD minimal resolution",
        json_schema_extra={"record": "final"},
    )
    max_resolution: Optional[ANGSTROMS] = Field(
        None,
        description="SAD maximal resolution",
        json_schema_extra={"record": "final"},
    )
    enantiomorph: Optional[str] = Field(
        None, description="SAD enantiomorph", json_schema_extra={"record": "final"}
    )
    space_group: Optional[str] = Field(
        None, description="SAD space group", json_schema_extra={"record": "final"}
    )
    step: Optional[str] = Field(
        None, description="SAD step", json_schema_extra={"record": "final"}
    )
    solvent: Optional[str] = Field(
        None, description="SAD solvent", json_schema_extra={"record": "final"}
    )
    pseudo_free_cc: Optional[str] = Field(
        None, description="SAD pseudo_free_cc", json_schema_extra={"record": "final"}
    )
    cc_partial_model: Optional[str] = Field(
        None, description="SAD cc_partial_model", json_schema_extra={"record": "final"}
    )
    chain_count: Optional[str] = Field(
        None, description="SAD chain_count", json_schema_extra={"record": "final"}
    )
    residues_count: Optional[str] = Field(
        None, description="SAD residues_count", json_schema_extra={"record": "final"}
    )
    average_fragment_length: Optional[str] = Field(
        None,
        description="SAD average_fragment_length",
        json_schema_extra={"record": "final"},
    )
    PDB_file: Optional[str] = Field(
        None, description="SAD PDB file path", json_schema_extra={"record": "final"}
    )
    MTZ_file: Optional[str] = Field(
        None, description="SAD MTZ file path", json_schema_extra={"record": "final"}
    )


class IcatMxMr(NXcollection):
    step: Optional[str] = Field(
        None, description="MR Step", json_schema_extra={"record": "final"}
    )
    space_group: Optional[str] = Field(
        None, description="MR space group", json_schema_extra={"record": "final"}
    )
    min_resolution: Optional[str] = Field(
        None, description="MR min resolution", json_schema_extra={"record": "final"}
    )
    max_resolution: Optional[str] = Field(
        None, description="MR max resolution", json_schema_extra={"record": "final"}
    )
    Phasing: Optional[IcatMxMrPhasing] = Field(None, description="")
    Refinement: Optional[IcatMxMrRefinement] = Field(None, description="")
    LigandFitting: Optional[IcatMxMrLigandfitting] = Field(None, description="")


class IcatMxAutoprocintegration(NXcollection):
    start_image_number: Optional[int] = Field(
        None, description="First image number of the integration"
    )
    end_image_number: Optional[int] = Field(
        None, description="Last image number of the integration"
    )
    detector_distance: Optional[str] = Field(
        None, description="Refined detector distance"
    )
    beam_x: Optional[str] = Field(None, description="Refined beam x")
    beam_y: Optional[str] = Field(None, description="Refined beam y")
    rotation_axis_x: Optional[str] = Field(
        None, description="X position of the rotation axis"
    )
    rotation_axis_y: Optional[str] = Field(
        None, description="Y position of the rotation axis"
    )
    rotation_axis_z: Optional[str] = Field(
        None, description="Z position of the rotation axis"
    )
    beam_vector_x: Optional[str] = Field(None, description="Vector X")
    beam_vector_y: Optional[str] = Field(None, description="Vector Y")
    beam_vector_z: Optional[str] = Field(None, description="Vector Z")
    space_group: Optional[str] = Field(None, description="Space group")
    cell_a: Optional[str] = Field(None, description="cell a")
    cell_b: Optional[str] = Field(None, description="cell b")
    cell_c: Optional[str] = Field(None, description="cell c")
    cell_alpha: Optional[str] = Field(None, description="cell alpha")
    cell_beta: Optional[str] = Field(None, description="cell beta")
    cell_gamma: Optional[str] = Field(None, description="cell gamma")
    anomalous: Optional[str] = Field(None, description="anomalous")
    diffraction_limit_direction_1: Optional[str] = Field(
        None,
        description="Diffraction limits (Ang.) of the ellipsoid fitted to the diffraction "
        "cut-off surface as direction cosines relative to the orthonormal basis (standard PDB convention), "
        "and also in terms of reciprocal unit-cell vectors",
    )
    diffraction_limit_direction_2: Optional[str] = Field(
        None,
        description="Diffraction limits (Ang.) of the ellipsoid fitted to the diffraction "
        "cut-off surface as direction cosines relative to the orthonormal basis (standard PDB convention), "
        "and also in terms of reciprocal unit-cell vectors",
    )
    diffraction_limit_direction_3: Optional[str] = Field(
        None,
        description="Diffraction limits (Ang.) of the ellipsoid fitted to the diffraction cut-off surface "
        "as direction cosines relative to the orthonormal basis (standard PDB convention), "
        "and also in terms of reciprocal unit-cell vectors",
    )
    principal_axis_1: Optional[str] = Field(
        None,
        description="Corresponding principal axes of the ellipsoid fitted to the diffraction cut-off surface "
        "as direction cosines relative to the orthonormal basis (standard PDB convention), "
        "and also in terms of reciprocal unit-cell vectors",
    )
    principal_axis_2: Optional[str] = Field(
        None,
        description="Corresponding principal axes of the ellipsoid fitted to the diffraction cut-off surface "
        "as direction cosines relative to the orthonormal basis (standard PDB convention), "
        "and also in terms of reciprocal unit-cell vectors",
    )
    principal_axis_3: Optional[str] = Field(
        None,
        description="Corresponding principal axes of the ellipsoid fitted to the diffraction cut-off surface "
        "as direction cosines relative to the orthonormal basis (standard PDB convention), "
        "and also in terms of reciprocal unit-cell vectors",
    )
    Scaling: Optional[IcatMxAutoprocintegrationScaling] = Field(None, description="")


class IcatMx(NXsubentry):
    aperture: Optional[str] = Field(
        None,
        description="Aperture size in microns",
        json_schema_extra={"record": "final"},
    )
    kappa_settings_id: Optional[str] = Field(
        None,
        description="Identifier used to distinguished between multiple kappa setting within the same data collection",
        json_schema_extra={"record": "final"},
    )
    beamShape: Optional[str] = Field(
        None,
        description="Beam shape at sample position",
        json_schema_extra={"record": "final"},
    )
    beamSizeAtSampleX: Optional[MILLIMETERS] = Field(
        None,
        description="Horizontal beam size in mm at sample position",
        json_schema_extra={"record": "final"},
    )
    beamSizeAtSampleY: Optional[MILLIMETERS] = Field(
        None,
        description="Vertical beam size in mm at sample position",
        json_schema_extra={"record": "final"},
    )
    dataCollectionId: Optional[str] = Field(
        None,
        description="ISPyB data collection id",
        json_schema_extra={"record": "final"},
    )
    detectorDistance: Optional[MILLIMETERS] = Field(
        None,
        description="Distance from detector to sample position",
        json_schema_extra={"record": "final"},
    )
    directory: Optional[str] = Field(
        None,
        description="Data collection directory",
        json_schema_extra={"record": "final"},
    )
    exposureTime: Optional[SECONDS] = Field(
        None,
        description="Exposure time per frame",
        json_schema_extra={"record": "final"},
    )
    flux: Optional[PHOTON_FLUX] = Field(
        None,
        description="Photon flux at the sample position",
        json_schema_extra={"record": "final"},
    )
    fluxEnd: Optional[str] = Field(
        None,
        description="Flux in photon/s before data collection",
        json_schema_extra={"record": "final"},
    )
    motorsName: Optional[str] = Field(
        None,
        description="Motor names",
        json_schema_extra={"icat_name": "motors_name", "record": "final"},
    )
    motorsValue: Optional[MILLIMETERS] = Field(
        None,
        description="Motor positions in mm",
        json_schema_extra={"icat_name": "motors_value", "record": "final"},
    )
    numberOfImages: Optional[int] = Field(
        None, description="Number of images", json_schema_extra={"record": "final"}
    )
    oscillationOverlap: Optional[DEGREES] = Field(
        None,
        description="Overlap between frames",
        json_schema_extra={"record": "final"},
    )
    oscillationRange: Optional[DEGREES] = Field(
        None,
        description="Degrees rotated per frame",
        json_schema_extra={"record": "final"},
    )
    oscillationStart: Optional[DEGREES] = Field(
        None,
        description="Starting angle of data collection",
        json_schema_extra={"record": "final"},
    )
    resolution: Optional[ANGSTROMS] = Field(
        None,
        description="Resolution at the edge of the detector",
        json_schema_extra={"record": "final"},
    )
    resolution_at_corner: Optional[ANGSTROMS] = Field(
        None,
        description="Resolution at the corner of the detector",
        json_schema_extra={"record": "final"},
    )
    scanType: Optional[str] = Field(
        None,
        description="mxCuBE experiment type",
        json_schema_extra={"record": "final"},
    )
    startImageNumber: Optional[int] = Field(
        None,
        description="Data collection image start number",
        json_schema_extra={"record": "final"},
    )
    template: Optional[str] = Field(
        None,
        description="Image file name template",
        json_schema_extra={"record": "final"},
    )
    transmission: Optional[str] = Field(
        None, description="Transmission in %", json_schema_extra={"record": "final"}
    )
    wavelength: Optional[ANGSTROMS] = Field(
        None, description="Wavelength in A", json_schema_extra={"record": "final"}
    )
    xBeam: Optional[MILLIMETERS] = Field(
        None,
        description="Horizontal beam centre in mm",
        json_schema_extra={"record": "final"},
    )
    yBeam: Optional[MILLIMETERS] = Field(
        None,
        description="Vertical beam centre in mm",
        json_schema_extra={"record": "final"},
    )
    rotation_axis: Optional[str] = Field(
        None,
        description="Name of the rotation axis",
        json_schema_extra={"record": "final"},
    )
    axis_range: Optional[str] = Field(
        None, description="Axis range", json_schema_extra={"record": "final"}
    )
    axis_start: Optional[str] = Field(
        None, description="Rotation start angle", json_schema_extra={"record": "final"}
    )
    axis_end: Optional[str] = Field(
        None, description="Rotation end angle", json_schema_extra={"record": "final"}
    )
    SAD: Optional[IcatMxSad] = Field(None, description="")
    MR: Optional[IcatMxMr] = Field(None, description="")
    AutoprocIntegration: Optional[IcatMxAutoprocintegration] = Field(
        None, description=""
    )
    position_id: Optional[str] = Field(
        None,
        description="Identifier of the position within the crystal",
        json_schema_extra={"record": "final"},
    )
    characterisation_id: Optional[str] = Field(
        None,
        description="Identifier of the characterisation",
        json_schema_extra={"record": "final"},
    )
    crystalPositionName: Optional[str] = Field(
        None,
        description="Centered position, line and grid ID",
        json_schema_extra={"record": "final"},
    )
