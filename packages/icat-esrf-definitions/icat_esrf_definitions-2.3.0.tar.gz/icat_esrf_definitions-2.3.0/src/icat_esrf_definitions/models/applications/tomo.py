from typing import Optional

from pydantic import Field

from ..base.nexus import NXcollection
from ..base.nexus import NXsubentry
from ..base.quantity import DEGREES
from ..base.quantity import DEGREES_ANGLE
from ..base.quantity import GRAY_PER_SECOND
from ..base.quantity import KILOELECTRONVOLTS
from ..base.quantity import KILOGRAY
from ..base.quantity import MICROMETERS
from ..base.quantity import MILLIAMPERES
from ..base.quantity import MILLIMETERS
from ..base.quantity import MILLISECONDS
from ..base.quantity import SECONDS


class IcatTomoAcquisitionZseries(NXcollection):
    z_mot: Optional[str] = Field(None, description="Motor mnemonic for Z-axis")
    z_start: Optional[MILLIMETERS] = Field(
        None, description="Initial position of the motor on the Z-axis (first stage)"
    )
    z_delta: Optional[MILLIMETERS] = Field(
        None, description="Incremental value for the Z-axis stage"
    )
    z_n_steps: Optional[float] = Field(
        None, description="Number of steps for the Z-axis stage"
    )
    duration: Optional[SECONDS] = Field(
        None, description="Time it took for the acquisition z-series sequence to run"
    )


class IcatTomoReconstructionPhase(NXcollection):
    ctf_advanced_params: Optional[str] = Field(
        None, description="Advanced parameters for CTF phase retrieval"
    )
    ctf_geometry: Optional[str] = Field(
        None, description="CTF phase retrieval geometry"
    )
    delta_beta: Optional[float] = Field(
        None, description="Delta-beta ratio for phase retrieval"
    )
    detector_sample_distance: Optional[MILLIMETERS] = Field(
        None, description="Detector-sample distance for phase retrieval"
    )
    method: Optional[str] = Field(None, description="Phase retrieval method used")
    padding_type: Optional[str] = Field(
        None, description="Padding type for phase retrieval"
    )
    unsharp_coeff: Optional[float] = Field(
        None, description="Unsharp coefficient for phase retrieval"
    )
    unsharp_method: Optional[str] = Field(
        None, description="Unsharp method used for phase retrieval"
    )
    unsharp_sigma: Optional[float] = Field(
        None, description="Unsharp sigma for phase retrieval"
    )


class IcatTomoAcquisition(NXcollection):
    technique: Optional[str] = Field(
        None, description="Technique used for hierarchical phase-contrast tomography"
    )
    proj_n: Optional[float] = Field(None, description="Number of projections images")
    flat_n: Optional[float] = Field(None, description="Number of flat field images")
    dark_n: Optional[float] = Field(None, description="Number of dark field images")
    flat_on: Optional[float] = Field(
        None, description="Interval for capturing flat field images"
    )
    y_step: Optional[MILLIMETERS] = Field(
        None, description="Translation step size in the Y-axis for flat images"
    )
    z_step: Optional[MILLIMETERS] = Field(
        None, description="Translation step size in the Z-axis for flat images"
    )
    start_angle: Optional[DEGREES_ANGLE] = Field(
        None, description="Start angle of the tomographic acquisition"
    )
    exposure_time: Optional[SECONDS] = Field(
        None,
        description="Exposure time per projection",
        json_schema_extra={"record": "final"},
    )
    sample_detector_distance: Optional[MILLIMETERS] = Field(
        None, description="Distance between sample and detector"
    )
    source_sample_distance: Optional[MILLIMETERS] = Field(
        None, description="Distance between source and sample"
    )
    energy: Optional[KILOELECTRONVOLTS] = Field(None, description="Beam energy")
    half_acquisition: Optional[bool] = Field(
        None, description="Half-acquisition mode enabled"
    )
    type: Optional[str] = Field(
        None, description="Acquisition type (e.g., half, full, or quarter acquisition)"
    )
    camera_pixel_size: Optional[MICROMETERS] = Field(
        None, description="Pixel size of the camera hardware"
    )
    sample_pixel_size: Optional[MICROMETERS] = Field(
        None, description="Pixel size in the sample space after all magnifications"
    )
    optic_magnified_pixel_size: Optional[MICROMETERS] = Field(
        None,
        description="Pixel size in the sample space after magnification of the optics",
    )
    magnification: Optional[float] = Field(
        None, description="Magnification factor of the optics"
    )
    beam_magnification: Optional[float] = Field(
        None, description="Magnification factor from the beam divergence"
    )
    read_srcur: Optional[bool] = Field(
        None, description="Enable real-time beam intensity measurement"
    )
    srcur_start: Optional[MILLIAMPERES] = Field(
        None, description="Beam intensity before scan"
    )
    srcur_stop: Optional[MILLIAMPERES] = Field(
        None, description="Beam intensity after scan"
    )
    scan_range: Optional[DEGREES_ANGLE] = Field(
        None, description="Rotation range for tomography"
    )
    scan_type: Optional[str] = Field(
        None,
        description="Type of scan used for the projection scan (e.g. INTERLACED, STEP, CONTINUOUS)",
    )
    acc_exposure_time: Optional[SECONDS] = Field(
        None, description="Accumulated exposure time per frame"
    )
    acc_frames_count: Optional[float] = Field(
        None, description="Number of frames in accumulation mode"
    )
    accel_disp: Optional[MILLIMETERS] = Field(
        None, description="Acceleration displacement for the rotation stage"
    )
    beam_check: Optional[bool] = Field(
        None, description="Suspend scan if no beam is detected"
    )
    camera_x_mot: Optional[str] = Field(
        None, description="Motor for moving the camera along the beam axis"
    )
    camera_acq_mode: Optional[str] = Field(
        None, description="Acquisition mode of the camera"
    )
    camera_flip_horz: Optional[bool] = Field(
        None, description="Horizontal flip of the camera (left-right)"
    )
    camera_flip_vert: Optional[bool] = Field(
        None, description="Vertical flip of the camera (up-down)"
    )
    latency_time: Optional[SECONDS] = Field(
        None, description="Extra readout time for the camera"
    )
    no_images_at_end: Optional[bool] = Field(
        None, description="Capture of images at the end of scan disabled"
    )
    no_flat_at_end: Optional[bool] = Field(
        None, description="Capture of flat images at the end of scan disabled"
    )
    optic_name: Optional[str] = Field(None, description="Name of optic used")
    optic_type: Optional[str] = Field(None, description="Type of optic used")
    scintillator: Optional[str] = Field(
        None, description="Name of the scintillator used"
    )
    duration: Optional[SECONDS] = Field(
        None, description="Time it took for the acquisition sequence to run"
    )
    comment: Optional[str] = Field(None, description="Additional comments")
    zseries: Optional[IcatTomoAcquisitionZseries] = Field(None, description="")


class IcatTomoReconstruction(NXcollection):
    angle_offset: Optional[DEGREES] = Field(
        None, description="Angle offset for the reconstruction in degrees"
    )
    angles_file: Optional[str] = Field(
        None, description="File path for angles used in reconstruction"
    )
    axis_correction_file: Optional[str] = Field(
        None, description="File path for axis correction data"
    )
    centered_axis: Optional[bool] = Field(
        None, description="Whether the reconstruction is centered on the axis"
    )
    clip_outer_circle: Optional[bool] = Field(
        None, description="Whether to clip the outer circle of the reconstruction"
    )
    cor_options: Optional[str] = Field(
        None, description="Options for center of rotation correction"
    )
    enable_halftomo: Optional[bool] = Field(
        None, description="Enable half-tomography mode"
    )
    end_x: Optional[int] = Field(
        None, description="End X coordinate (in pixels) for reconstruction"
    )
    end_y: Optional[int] = Field(
        None, description="End Y coordinate (in pixels) for reconstruction"
    )
    end_z: Optional[int] = Field(
        None, description="End Z coordinate (in pixels) for reconstruction"
    )
    fbp_filter_cutoff: Optional[float] = Field(
        None, description="Cutoff frequency for the FBP filter"
    )
    fbp_filter_type: Optional[str] = Field(None, description="Type of FBP filter used")
    method: Optional[str] = Field(
        None, description="Reconstruction method used (e.g., FBP, SIRT)"
    )
    optim_algorithm: Optional[str] = Field(
        None, description="Optimization algorithm used for reconstruction"
    )
    padding_type: Optional[str] = Field(
        None, description="Padding type for reconstruction"
    )
    preconditioning_filter: Optional[str] = Field(
        None, description="Preconditioning filter applied to the reconstruction"
    )
    rotation_axis_position: Optional[float] = Field(
        None, description="Position of the rotation axis in pixels"
    )
    start_x: Optional[int] = Field(
        None, description="Start X coordinate (in pixels) for reconstruction"
    )
    start_y: Optional[int] = Field(
        None, description="Start Y coordinate (in pixels) for reconstruction"
    )
    start_z: Optional[int] = Field(
        None, description="Start Z coordinate (in pixels) for reconstruction"
    )
    translation_movements_file: Optional[str] = Field(
        None, description="File path for translation movements data"
    )
    weight_tv: Optional[float] = Field(
        None, description="Total variation weight for reconstruction"
    )
    voxel_size_x: Optional[MICROMETERS] = Field(
        None, description="Voxel size in X direction"
    )
    voxel_size_y: Optional[MICROMETERS] = Field(
        None, description="Voxel size in Y direction"
    )
    voxel_size_z: Optional[MICROMETERS] = Field(
        None, description="Voxel size in Z direction"
    )
    nb_voxel_x: Optional[float] = Field(
        None, description="Reconstructed volume length in pixels (x-direction)"
    )
    nb_voxel_y: Optional[float] = Field(
        None, description="Reconstructed volume length in pixels (y-direction)"
    )
    nb_voxel_z: Optional[float] = Field(
        None, description="Reconstructed volume length in pixels (z-direction)"
    )
    phase: Optional[IcatTomoReconstructionPhase] = Field(None, description="")


class IcatTomo(NXsubentry):
    acquisition: Optional[IcatTomoAcquisition] = Field(None, description="")
    reconstruction: Optional[IcatTomoReconstruction] = Field(None, description="")
    experiment_type: Optional[str] = Field(
        None,
        description="Type of experiment conducted",
        json_schema_extra={"record": "final"},
    )
    ftomo_par: Optional[str] = Field(
        None, description="Parameters for Fourier-tomography"
    )
    xshutter_time: Optional[MILLISECONDS] = Field(
        None, description="Shutter closing time for the detector"
    )
    images_per_step: Optional[float] = Field(
        None, description="Number of images captured per step"
    )
    interlaced: Optional[float] = Field(None, description="Enable interlaced scanning")
    nested: Optional[float] = Field(
        None, description="Enable nested scanning for topotomo"
    )
    save_separate_dark_image: Optional[float] = Field(
        None, description="Save separate dark field images"
    )
    auto_update_ref: Optional[float] = Field(
        None, description="Automatically update references if set"
    )
    images_at_end_as_quali: Optional[float] = Field(
        None, description="Use images at end of scan for quality check"
    )
    live_correction: Optional[float] = Field(
        None, description="Enable live correction of dark fields"
    )
    mono_tune_on_ref: Optional[float] = Field(
        None, description="Tune monochromator before capturing flat images"
    )
    no_accel_corr: Optional[float] = Field(
        None, description="Disable acceleration correction"
    )
    open_slits_on_quali: Optional[float] = Field(
        None, description="Open slits for quality check images"
    )
    optics_eye_piece: Optional[float] = Field(
        None, description="Magnification factor from optics"
    )
    readout_time: Optional[SECONDS] = Field(
        None, description="Readout time of the camera"
    )
    flat_power: Optional[float] = Field(
        None, description="Power of the motor for capturing flat images"
    )
    rounding_correction: Optional[float] = Field(
        None, description="Apply rounding corrections to projections"
    )
    safe_time: Optional[SECONDS] = Field(
        None, description="Extra time to ensure safe readout"
    )
    shift_turns: Optional[float] = Field(
        None, description="Number of rotation turns to shift"
    )
    speed_corr_factor: Optional[float] = Field(
        None, description="Correction factor for rotation speed"
    )
    mono_tune_on_start: Optional[float] = Field(
        None, description="Tune monochromator before scan starts"
    )
    soft_version: Optional[str] = Field(
        None, description="Software version, hostname, and path"
    )
    vacuum_value: Optional[float] = Field(None, description="Vacuum measurement values")
    vacuum_name: Optional[str] = Field(None, description="Vacuum measurement names")
    sx0: Optional[MILLIMETERS] = Field(None, description="Focus position on X-axis")
    camera_time: Optional[SECONDS] = Field(
        None, description="Integration time of the camera"
    )
    i0: Optional[float] = Field(None, description="Incident beam intensity")
    it: Optional[float] = Field(None, description="Transmitted beam intensity")
    interlaced_roundtrip: Optional[float] = Field(
        None, description="Interlaced scanning: same or opposite directions"
    )
    scanning_mode: Optional[str] = Field(None, description="Mode of scanning")
    x_pixel_n: Optional[float] = Field(
        None, description="Number of pixels in the x-direction"
    )
    y_pixel_n: Optional[float] = Field(
        None, description="Number of pixels in the y-direction"
    )
    surface_dose: Optional[GRAY_PER_SECOND] = Field(
        None, description="Radiation dose at the surface"
    )
    voi_dose: Optional[GRAY_PER_SECOND] = Field(
        None, description="Radiation dose within the volume of interest (VOI)"
    )
    total_voi_dose: Optional[KILOGRAY] = Field(
        None, description="Total accumulated dose within the volume of interest (VOI)"
    )
    reference_description: Optional[str] = Field(
        None,
        description="Approach used to generate reference frames for flat field subtraction",
    )
    subframe_nb: Optional[float] = Field(None, description="Number of subframes")
    idNames: Optional[str] = Field(
        None, description="Insertion device for ID beamlines"
    )
    scanRadix: Optional[str] = Field(
        None,
        description="Common prefix for scan datasets, useful for locating original radiographs",
    )
    propagationDistance: Optional[MILLIMETERS] = Field(
        None, description="Distance between the sample and detector"
    )
    xStages: Optional[float] = Field(
        None, description="Number of scans in x-direction; allows 3D mosaic scans"
    )
    yStages: Optional[float] = Field(
        None, description="Number of scans in y-direction; allows 3D mosaic scans"
    )
    zStages: Optional[float] = Field(
        None, description="Number of scans in z-direction; allows 3D mosaic scans"
    )
    min32to16bits: Optional[float] = Field(
        None,
        description="Min value for scaling 32-bit float to 16-bit unsigned integer",
    )
    max32to16bits: Optional[float] = Field(
        None,
        description="Max value for scaling 32-bit float to 16-bit unsigned integer",
    )
    jp2CompressRatio: Optional[float] = Field(
        None, description="JPEG2000 compression ratio (default ~10x)"
    )
