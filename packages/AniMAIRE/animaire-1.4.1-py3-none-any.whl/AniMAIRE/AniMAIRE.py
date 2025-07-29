import numpy as np
import datetime as dt
import spaceweather as sw
from typing import Callable, List, Optional, Tuple, Union, Any

from .MAIREPLUS_spectrum import MAIREPLUS_spectrum, _set_function_references

from .utils import get_correctly_formatted_particle_dist_list, get_kp_index, validate_altitudes
from .anisotropic_MAIRE_engine.spectralCalculations.rigiditySpectrum import DLRmodelSpectrum, CommonModifiedPowerLawSpectrum, CommonModifiedPowerLawSpectrumSplit, PowerLawSpectrum
from .anisotropic_MAIRE_engine.spectralCalculations.pitchAngleDistribution import IsotropicPitchAngleDistribution, gaussianBeeckPitchAngleDistribution, isotropicPitchAngleDistribution, gaussianPitchAngleDistribution
from .anisotropic_MAIRE_engine.generalEngineInstance import generalEngineInstance, default_array_of_lats_and_longs
from .DoseRateFrame import DoseRateFrame
import logging

import datetime as dt
import logging
import numpy as np
import pandas as pd

def run_from_spectra(
        proton_rigidity_spectrum: Optional[Callable[[float], float]] = None,
        alpha_rigidity_spectrum: Optional[Callable[[float], float]] = None,
        reference_pitch_angle_latitude: float = 0.0,
        reference_pitch_angle_longitude: float = 45.0,
        proton_pitch_angle_distribution: Callable[[float, float], float] = isotropicPitchAngleDistribution(),
        alpha_pitch_angle_distribution: Callable[[float, float], float] = isotropicPitchAngleDistribution(),
        altitudes_in_kft: Optional[List[float]] = None,
        altitudes_in_km: Optional[List[float]] = None,
        Kp_index: Optional[int] = None,
        date_and_time: Optional[dt.datetime] = None,
        array_of_lats_and_longs: np.ndarray = default_array_of_lats_and_longs,
        cache_asymptotic_directions: bool = True,
        generate_NM_count_rates: bool = False,
        use_default_9_zeniths_azimuths: bool = False,
        use_OTSOpy: bool = True,
        asymp_dir_file: Optional[str] = None,
        record_full_output: bool = False,
        **mag_cos_kwargs,
) -> DoseRateFrame:
    """
    Perform a run to calculate dose rates across Earth's atmosphere based on proton, alpha particle + heavier ions, or proton + alpha particle + heavier ions spectra.

    Parameters:
    - proton_rigidity_spectrum: callable, optional
        Function describing the proton rigidity spectrum in units of cm-2 s-1 sr-1 (GV/n)-1.
    - alpha_rigidity_spectrum: callable, optional
        Function describing the alpha particle rigidity spectrum in units of cm-2 s-1 sr-1 (GV/n)-1.
    - reference_pitch_angle_latitude: float, optional
        Reference latitude in GEO coordinates representing a pitch angle of 0 in the supplied pitch angle distribution.
    - reference_pitch_angle_longitude: float, optional
        Reference longitude in GEO coordinates representing a pitch angle of 0 in the supplied pitch angle distribution.
    - proton_pitch_angle_distribution: callable, optional
        Function describing the proton pitch angle distribution.
    - alpha_pitch_angle_distribution: callable, optional
        Function describing the alpha particle pitch angle distribution.
    - altitudes_in_kft: list, optional
        List of altitudes in kilofeet to perform calculations for.
    - altitudes_in_km: list, optional
        List of altitudes in kilometers to perform calculations for.
    - Kp_index: int, optional
        Kp index representing geomagnetic conditions.
    - date_and_time: datetime, optional
        Date and time for the simulation.
    - array_of_lats_and_longs: array, optional
        Array of latitudes and longitudes to perform calculations for.
    - cache_asymptotic_directions: bool, optional
        Whether to cache the results of asymptotic direction calculations.
    - generate_NM_count_rates: bool, optional
        Whether to generate neutron monitor count rates.
    - use_default_9_zeniths_azimuths: bool, optional
        Whether to use the mean of nine different asymptotic directions to calculate dose rates.
    - use_OTSOpy: bool, optional
        Whether to use OTSOpy for asymptotic direction calculations instead of MAGNETOCOSMICS.
    - asymp_dir_file: str, optional
        Path to a file containing pre-calculated asymptotic directions.
    - record_full_output: bool, optional
        Whether to record full output attributes.
    - **mag_cos_kwargs: additional keyword arguments
        Additional arguments to pass to AsympDirsCalculator.

    Returns:
    - output_dose_rate_DF: DoseRateFrame
        DoseRateFrame containing the calculated dose rates and metadata.
    """

    # New check: if an asymp_dir_file is provided, do not allow other asymptotic direction parameters.
    if asymp_dir_file is not None:
        if (use_default_9_zeniths_azimuths or 
            any(key in mag_cos_kwargs for key in ["array_of_zeniths_and_azimuths"]) or 
            Kp_index is not None or 
            array_of_lats_and_longs is not default_array_of_lats_and_longs or
            date_and_time is not None or
            bool(mag_cos_kwargs)):
            raise ValueError("Error: When asymp_dir_file is provided, no additional asymptotic direction parameters, Kp_index, array_of_lats_and_longs, date_and_time, cache_magnetocosmics_run, or mag_cos_kwargs should be supplied.")

    if date_and_time is None:
        date_and_time = dt.datetime.utcnow()

    if date_and_time.tzinfo is None:
        logging.warning("The inputted date and time does not have timezone info. Assuming UTC.")
        date_and_time = date_and_time.replace(tzinfo=dt.timezone.utc)

    if Kp_index is None:
        Kp_index = get_kp_index(date_and_time)
    
    altitudes_in_km = validate_altitudes(altitudes_in_km, altitudes_in_kft)

    if (proton_rigidity_spectrum is None) and (alpha_rigidity_spectrum is None):
        raise Exception("Error: either a proton rigidity spectrum or an alpha rigidity spectrum must be specified!")
    
    list_of_particle_distributions = get_correctly_formatted_particle_dist_list(proton_rigidity_spectrum, 
                                                                                alpha_rigidity_spectrum, 
                                                                                reference_pitch_angle_latitude, 
                                                                                reference_pitch_angle_longitude, 
                                                                                proton_pitch_angle_distribution, 
                                                                                alpha_pitch_angle_distribution)

    
    engine_to_run = generalEngineInstance(list_of_particle_distributions,
                                          list_of_altitudes_km=altitudes_in_km,
                                          Kp_index=Kp_index,
                                          date_and_time=date_and_time,
                                          use_OTSOpy=use_OTSOpy,
                                          reference_latitude=reference_pitch_angle_latitude,
                                          reference_longitude=reference_pitch_angle_longitude,
                                          array_of_lats_and_longs=array_of_lats_and_longs,
                                          cache_magnetocosmics_runs=cache_asymptotic_directions,
                                          generate_NM_count_rates=generate_NM_count_rates,
                                          asymp_dir_file=asymp_dir_file)
    
    output_dose_rate_DF_data = engine_to_run.getAsymptoticDirsAndRun(use_default_9_zeniths_azimuths, record_full_output=record_full_output,  **mag_cos_kwargs)

    print("Success!")

    # Capture run parameters excluding potentially large or internal variables
    run_parameters = locals().copy()
    # Remove variables that are not direct inputs or are modified later/internal
    run_parameters.pop('mag_cos_kwargs', None) 
    run_parameters.pop('engine_to_run', None)
    run_parameters.pop('output_dose_rate_DF', None)
    run_parameters.pop('list_of_particle_distributions', None) # Added below specifically
    run_parameters.update(mag_cos_kwargs) # Add back mag_cos_kwargs flattened

    # Create DoseRateFrame instance
    output_dose_rate_DF = DoseRateFrame(
        data=output_dose_rate_DF_data,
        timestamp=date_and_time,
        particle_distributions=list_of_particle_distributions,
        run_parameters=run_parameters
    )

    return output_dose_rate_DF

def run_from_power_law_gaussian_distribution(
        J0: float, gamma: float, deltaGamma: float, sigma: float, 
        reference_pitch_angle_latitude: float, reference_pitch_angle_longitude: float, 
        Kp_index: Optional[int] = None, date_and_time: Optional[dt.datetime] = None,
        use_split_spectrum: bool = False,
        asymp_dir_file: Optional[str] = None,
        **kwargs
) -> DoseRateFrame:
    """
    Perform a run to calculate dose rates using a combined power law rigidity spectrum and Gaussian pitch angle distribution.

    Parameters:
    - J0: float
        Normalization factor for the rigidity spectrum.
    - gamma: float
        Spectral index for the rigidity spectrum.
    - deltaGamma: float
        Modification factor for the spectral index.
    - sigma: float
        Standard deviation for the Gaussian pitch angle distribution.
    - reference_pitch_angle_latitude: float
        Reference latitude in GEO coordinates representing a pitch angle of 0.
    - reference_pitch_angle_longitude: float
        Reference longitude in GEO coordinates representing a pitch angle of 0.
    - Kp_index: int
        Kp index representing geomagnetic conditions.
    - date_and_time: datetime
        Date and time for the simulation.
    - use_split_spectrum: bool, optional
        Whether to use a split spectrum.
    - **kwargs: additional keyword arguments
        Additional arguments to pass to run_from_spectra.

    Returns:
    - output_dose_rate_DF: DoseRateFrame
        DataFrame containing the calculated dose rates.
    """
    spec_to_use = CommonModifiedPowerLawSpectrumSplit if use_split_spectrum else CommonModifiedPowerLawSpectrum

    return run_from_spectra(
        proton_rigidity_spectrum=spec_to_use(J0, gamma, deltaGamma),
        reference_pitch_angle_latitude=reference_pitch_angle_latitude,
        reference_pitch_angle_longitude=reference_pitch_angle_longitude,
        proton_pitch_angle_distribution=gaussianPitchAngleDistribution(normFactor=1,sigma=sigma),
        Kp_index=Kp_index,date_and_time=date_and_time,
        asymp_dir_file=asymp_dir_file,
        **kwargs,
    )

def run_from_double_power_law_gaussian_distribution(
        J0: float, gamma: float, deltaGamma: float, sigma_1: float, sigma_2: float,
        B: float, alpha_prime: float,
        reference_pitch_angle_latitude: float, reference_pitch_angle_longitude: float, 
        Kp_index: Optional[int] = None, date_and_time: Optional[dt.datetime] = None,
        use_split_spectrum: bool = False,
        asymp_dir_file: Optional[str] = None,
        **kwargs
) -> DoseRateFrame:
    """
    Perform a run to calculate dose rates using a double power law rigidity spectrum and Gaussian pitch angle distribution.

    Parameters:
    - J0: float
        Normalization factor for the rigidity spectrum.
    - gamma: float
        Spectral index for the rigidity spectrum.
    - deltaGamma: float
        Modification factor for the spectral index.
    - sigma_1: float
        Standard deviation for the first Gaussian pitch angle distribution.
    - sigma_2: float
        Standard deviation for the second Gaussian pitch angle distribution.
    - B: float
        Scaling factor for the second Gaussian pitch angle distribution.
    - alpha_prime: float
        Shift factor for the second Gaussian pitch angle distribution.
    - reference_pitch_angle_latitude: float
        Reference latitude in GEO coordinates representing a pitch angle of 0.
    - reference_pitch_angle_longitude: float
        Reference longitude in GEO coordinates representing a pitch angle of 0.
    - Kp_index: int
        Kp index representing geomagnetic conditions.
    - date_and_time: datetime
        Date and time for the simulation.
    - use_split_spectrum: bool, optional
        Whether to use a split spectrum.
    - **kwargs: additional keyword arguments
        Additional arguments to pass to run_from_spectra.

    Returns:
    - output_dose_rate_DF: DoseRateFrame
        DataFrame containing the calculated dose rates.
    """
    spec_to_use = CommonModifiedPowerLawSpectrumSplit if use_split_spectrum else lambda J0,gamma,deltaGamma:CommonModifiedPowerLawSpectrum(J0,gamma,deltaGamma, lowerLimit=0.814529,upperLimit=21.084584)

    return run_from_spectra(
        proton_rigidity_spectrum=spec_to_use(J0, gamma, deltaGamma),
        reference_pitch_angle_latitude=reference_pitch_angle_latitude,
        reference_pitch_angle_longitude=reference_pitch_angle_longitude,
        proton_pitch_angle_distribution=gaussianPitchAngleDistribution(normFactor=1,sigma=sigma_1) + (B * gaussianPitchAngleDistribution(normFactor=1,sigma=sigma_2,alpha=alpha_prime)),
        Kp_index=Kp_index,date_and_time=date_and_time,
        asymp_dir_file=asymp_dir_file,
        **kwargs,
    )

def run_from_power_law_Beeck_gaussian_distribution(
        J0: float, gamma: float, deltaGamma: float, A: float, B: float, 
        reference_pitch_angle_latitude: float, reference_pitch_angle_longitude: float, 
        Kp_index: Optional[int] = None, date_and_time: Optional[dt.datetime] = None,
        use_split_spectrum: bool = False,
        asymp_dir_file: Optional[str] = None,
        **kwargs
) -> DoseRateFrame:
    """
    Perform a run to calculate dose rates using a power law rigidity spectrum and Beeck Gaussian pitch angle distribution.

    Parameters:
    - J0: float
        Normalization factor for the rigidity spectrum.
    - gamma: float
        Spectral index for the rigidity spectrum.
    - deltaGamma: float
        Modification factor for the spectral index.
    - A: float
        Parameter A for the Beeck Gaussian pitch angle distribution.
    - B: float
        Parameter B for the Beeck Gaussian pitch angle distribution.
    - reference_pitch_angle_latitude: float
        Reference latitude in GEO coordinates representing a pitch angle of 0.
    - reference_pitch_angle_longitude: float
        Reference longitude in GEO coordinates representing a pitch angle of 0.
    - Kp_index: int
        Kp index representing geomagnetic conditions.
    - date_and_time: datetime
        Date and time for the simulation.
    - use_split_spectrum: bool, optional
        Whether to use a split spectrum.
    - **kwargs: additional keyword arguments
        Additional arguments to pass to run_from_spectra.

    Returns:
    - output_dose_rate_DF: DoseRateFrame
        DataFrame containing the calculated dose rates.
    """
    spec_to_use = CommonModifiedPowerLawSpectrum if use_split_spectrum else CommonModifiedPowerLawSpectrumSplit

    return run_from_spectra(
        proton_rigidity_spectrum=spec_to_use(J0, gamma, deltaGamma),
        reference_pitch_angle_latitude=reference_pitch_angle_latitude,
        reference_pitch_angle_longitude=reference_pitch_angle_longitude,
        proton_pitch_angle_distribution=gaussianBeeckPitchAngleDistribution(normFactor=1,A=A,B=B),
        Kp_index=Kp_index,date_and_time=date_and_time,
        asymp_dir_file=asymp_dir_file,
        **kwargs,
    )

def run_from_DLR_cosmic_ray_model(
        OULU_count_rate_in_seconds: Optional[float] = None,
        W_parameter: Optional[float] = None,
        Kp_index: Optional[int] = None,
        date_and_time: Optional[dt.datetime] = None,
        asymp_dir_file: Optional[str] = None,
        **kwargs
) -> DoseRateFrame:
    """
    Perform a run to calculate dose rates using the DLR cosmic ray model.

    Parameters:
    - OULU_count_rate_in_seconds: float, optional
        OULU count rate in seconds.
    - W_parameter: float, optional
        W parameter for the DLR model.
    - Kp_index: int, optional
        Kp index representing geomagnetic conditions.
    - date_and_time: datetime, optional
        Date and time for the simulation.
    - **kwargs: additional keyword arguments
        Additional arguments to pass to run_from_spectra.

    Returns:
    - output_dose_rate_DF: DoseRateFrame
        DataFrame containing the calculated dose rates.
    """
    if (W_parameter is None) and (OULU_count_rate_in_seconds is None):
        print("As no OULU count rates or W parameters were specified, the count rate of OULU in the past will be determined using the supplied date and time for the purposes of calculating the incoming spectra.")
        DLR_model_date_and_time = date_and_time
    else:
        DLR_model_date_and_time = None

    return run_from_spectra(
        proton_rigidity_spectrum=DLRmodelSpectrum(atomicNumber=1, date_and_time=DLR_model_date_and_time, OULUcountRateInSeconds=OULU_count_rate_in_seconds, W_parameter=W_parameter),
        alpha_rigidity_spectrum=DLRmodelSpectrum(atomicNumber=2, date_and_time=DLR_model_date_and_time, OULUcountRateInSeconds=OULU_count_rate_in_seconds, W_parameter=W_parameter),
        Kp_index=Kp_index,date_and_time=date_and_time,
        asymp_dir_file=asymp_dir_file,
        **kwargs,
    )

# Set function references to avoid circular imports - do this after defining the functions
_set_function_references(run_from_DLR_cosmic_ray_model, run_from_spectra)

def run_maireplus_spectrum(
    neutron_monitor_1_percentage_increase: float,
    neutron_monitor_2_percentage_increase: float,
    normalisation_monitor_percentage_increase: float,
    OULU_gcr_count_rate_in_seconds: float,
    datetime: Union[dt.datetime, np.datetime64],
    kp_index: Optional[int] = None,
    neutron_monitor_1_location: Tuple[float, float, float] = (65.0, 25.0, 0.0),
    neutron_monitor_2_location: Tuple[float, float, float] = (50.0, 5.0, 0.0),
    normalisation_monitor_location: Tuple[float, float, float] = (65.0, 25.0, 0.0),
    use_fast_calculation: bool = True,
    **kwargs: Any
) -> DoseRateFrame:
    """
    Run AniMAIRE with a MAIREPLUS spectrum directly.
    
    Parameters:
    -----------
    neutron_monitor_1_location : tuple
        (latitude, longitude, altitude) of first neutron monitor
    neutron_monitor_1_percentage_increase : float
        Percentage increase for first neutron monitor
    neutron_monitor_2_location : tuple
        (latitude, longitude, altitude) of second neutron monitor
    neutron_monitor_2_percentage_increase : float
        Percentage increase for second neutron monitor
    normalisation_monitor_location : tuple
        (latitude, longitude, altitude) of normalisation monitor
    normalisation_monitor_percentage_increase : float
        Percentage increase for normalisation monitor
    OULU_gcr_count_rate_in_seconds : float
        OULU GCR count rate in seconds
    datetime : datetime.datetime
        Date and time for the calculation
    kp_index : int, optional
        Kp index representing geomagnetic conditions.
    array_of_lats_and_longs : list, optional
        List of [latitude, longitude] pairs for calculation
    use_fast_calculation : bool
        Whether to use fast calculation mode for pitch angle distribution
    **kwargs : dict
        Additional arguments to pass to AniMAIRE.run_from_spectra
        
    Returns:
    --------
    DoseRateFrame
        Result from AniMAIRE calculation
    """

    # Handle both datetime and numpy.datetime64 objects
    if isinstance(datetime, np.datetime64):
        # Convert numpy.datetime64 to Python datetime
        datetime = pd.Timestamp(datetime).to_pydatetime()
    
    if hasattr(datetime, 'tzinfo') and datetime.tzinfo is None:
        logging.warning("The inputted date and time does not have timezone info. Assuming UTC.")
        datetime = datetime.replace(tzinfo=dt.timezone.utc)

    # Get Kp index if not provided
    if kp_index is None:
        kp_index = get_kp_index(datetime)
    
    # Create the MAIREPLUS spectrum
    spectrum = MAIREPLUS_spectrum(
        neutron_monitor_1_location=neutron_monitor_1_location,
        neutron_monitor_1_percentage_increase=neutron_monitor_1_percentage_increase,
        neutron_monitor_2_location=neutron_monitor_2_location,
        neutron_monitor_2_percentage_increase=neutron_monitor_2_percentage_increase,
        normalisation_monitor_location=normalisation_monitor_location,
        normalisation_monitor_percentage_increase=normalisation_monitor_percentage_increase,
        OULU_gcr_count_rate_in_seconds=OULU_gcr_count_rate_in_seconds,
        datetime=datetime,
        kp_index=kp_index
    )

    GCR_dose_rate_frame = run_from_DLR_cosmic_ray_model(
        OULU_count_rate_in_seconds=OULU_gcr_count_rate_in_seconds,
        date_and_time=datetime,
        Kp_index=kp_index,
        proton_pitch_angle_distribution=IsotropicPitchAngleDistribution(use_fast_calculation=use_fast_calculation),
        alpha_pitch_angle_distribution=IsotropicPitchAngleDistribution(use_fast_calculation=use_fast_calculation),
        **kwargs
    )
    
    # Run AniMAIRE with the spectrum
    GLE_dose_rate_frame = run_from_spectra(
        spectrum,
        proton_pitch_angle_distribution=IsotropicPitchAngleDistribution(use_fast_calculation=use_fast_calculation),
        date_and_time=datetime,
        Kp_index=kp_index,
        #array_of_lats_and_longs=array_of_lats_and_longs,
        **kwargs
    )

    return GLE_dose_rate_frame + GCR_dose_rate_frame




