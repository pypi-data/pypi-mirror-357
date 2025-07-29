#import cudf.pandas
#cudf.pandas.install()

import numpy as np
import pandas as pd
import datetime as dt
import sys
import ParticleRigidityCalculationTools as PRCT
from joblib import Memory
import tqdm
tqdm.tqdm.pandas()

from spacepy.coordinates import Coords as spaceCoords
from spacepy.time import Ticktock as spaceTicktock
import numba

from .spectralCalculations.particleDistribution import particleDistribution
from .spectralCalculations.momentaDistribution import momentaDistribution
from .spectralCalculations.pitchAngleDistribution import IsotropicPitchAngleDistribution

memory_asymp_dirs = Memory("./cacheAsymptoticDirectionOutputs", verbose=0)

m0 = 1.67262192e-27 #kg
c = 299792458.0 #m/s
protonCharge = 1.60217663e-19 #C
protonRestEnergy = m0 * (c**2)

global get_apply_method
def get_apply_method(DF_or_Series: pd.DataFrame) -> callable:
    """
    Determine the appropriate apply method based on the debugging state.

    Parameters:
    - DF_or_Series: pd.DataFrame
        The DataFrame or Series to apply the method to.

    Returns:
    - callable
        The appropriate apply method.
    """
    if hasattr(sys, 'gettrace') and sys.gettrace() is not None:
        print("debug mode being used: setting AniMAIRE to use progress_apply rather than running in parallel!")
        apply_method = DF_or_Series.progress_apply
    else:
        #print("not in debug mode: setting AniMAIRE to use parallel_apply!")
        apply_method = DF_or_Series.parallel_apply
        
    return apply_method

def generate_asymp_dir_DF(dataframeToFillFrom: pd.DataFrame, IMFlatitude: float, IMFlongitude: float, datetime_to_run_across_UTC: dt.datetime, cache: bool) -> pd.DataFrame:
    """
    Generate a DataFrame of asymptotic directions with pitch angles.

    Parameters:
    - dataframeToFillFrom: pd.DataFrame
        The DataFrame to fill from.
    - IMFlatitude: float
        The latitude of the Interplanetary Magnetic Field (IMF).
    - IMFlongitude: float
        The longitude of the Interplanetary Magnetic Field (IMF).
    - datetime_to_run_across_UTC: dt.datetime
        The datetime to run across in UTC.
    - cache: bool
        Whether to cache the results.

    Returns:
    - pd.DataFrame
        The DataFrame with asymptotic directions and pitch angles.
    """
    new_asymp_dir_DF = dataframeToFillFrom.copy()

    #new_asymp_dir_DF["Energy"] = PRCT.convertParticleRigidityToEnergy(dataframeToFillFrom["Rigidity"], particleMassAU = 1, particleChargeAU = 1)

    print("assigning asymptotic coordinates")
    if cache == False:
        asymptoticDirectionList = convertAsymptoticDirectionsToPitchAngle(dataframeToFillFrom, IMFlatitude, IMFlongitude, datetime_to_run_across_UTC)
    else:
        cachedConvertAsympDirFunc = memory_asymp_dirs.cache(convertAsymptoticDirectionsToPitchAngle)
        asymptoticDirectionList = cachedConvertAsympDirFunc(dataframeToFillFrom, IMFlatitude, IMFlongitude, datetime_to_run_across_UTC)

    print("successfully converted asymptotic directions")

    new_asymp_dir_DF["angleBetweenIMFinRadians"] = asymptoticDirectionList

    return new_asymp_dir_DF

def convertAsymptoticDirectionsToPitchAngle(dataframeToFillFrom: pd.DataFrame, IMFlatitude: float, IMFlongitude: float, datetime_to_run_across_UTC: dt.datetime) -> pd.Series:
    """
    Convert asymptotic directions to pitch angles.

    Parameters:
    - dataframeToFillFrom: pd.DataFrame
        The DataFrame to fill from.
    - IMFlatitude: float
        The latitude of the Interplanetary Magnetic Field (IMF).
    - IMFlongitude: float
        The longitude of the Interplanetary Magnetic Field (IMF).
    - datetime_to_run_across_UTC: dt.datetime
        The datetime to run across in UTC.

    Returns:
    - pd.Series
        The Series with pitch angles.
    """
    print("acquiring pitch angles...")
    from pandarallel import pandarallel
    pandarallel.initialize(progress_bar=True)
    pitch_angle_list = get_apply_method(dataframeToFillFrom)(lambda dataframe_row: get_pitch_angle_for_DF_analytic(IMFlatitude, IMFlongitude, dataframe_row["Lat"], dataframe_row["Long"]), axis=1)

    return pitch_angle_list

@numba.jit(nopython=True)
def get_pitch_angle_for_DF_analytic(IMFlatitude: float, IMFlongitude: float, asymptotic_dir_latitude: float, asymptotic_dir_longitude: float) -> float:
    """
    Calculate the pitch angle for a DataFrame row analytically.

    Parameters:
    - IMFlatitude: float
        The latitude of the Interplanetary Magnetic Field (IMF).
    - IMFlongitude: float
        The longitude of the Interplanetary Magnetic Field (IMF).
    - asymptotic_dir_latitude: float
        The latitude of the asymptotic direction.
    - asymptotic_dir_longitude: float
        The longitude of the asymptotic direction.

    Returns:
    - float
        The pitch angle in radians.
    """
    IMFlatitude_rad = IMFlatitude * (np.pi / 180.0)
    IMFlongitude_rad = IMFlongitude * (np.pi / 180.0)
    asymptotic_dir_latitude_rad = asymptotic_dir_latitude * (np.pi / 180.0)
    asymptotic_dir_longitude_rad = asymptotic_dir_longitude * (np.pi / 180.0)

    cos_pitch_angle = (np.sin(asymptotic_dir_latitude_rad) * np.sin(IMFlatitude_rad)) + \
                      (np.cos(asymptotic_dir_latitude_rad) * np.cos(IMFlatitude_rad) * np.cos(asymptotic_dir_longitude_rad - IMFlongitude_rad))
    
    pitch_angle = np.arccos(cos_pitch_angle)

    return pitch_angle

def acquireWeightingFactors(asymptotic_direction_DF: pd.DataFrame, particle_dist: particleDistribution) -> pd.DataFrame:
    """
    Acquire weighting factors for asymptotic directions.

    Parameters:
    - asymptotic_direction_DF: pd.DataFrame
        The DataFrame with asymptotic directions.
    - particle_dist: particleDistribution
        The particle distribution.

    Returns:
    - pd.DataFrame
        The DataFrame with weighting factors.
    """

    from pandarallel import pandarallel
    pandarallel.initialize(progress_bar=True)
    
    momentaDist = particle_dist.momentum_distribution
    new_asymptotic_direction_DF = asymptotic_direction_DF.copy()

    # Check if we have an isotropic pitch angle distribution with fast mode
    is_isotropic_fast = (isinstance(momentaDist.getPitchAngleDistribution(), IsotropicPitchAngleDistribution) and 
                        getattr(momentaDist.getPitchAngleDistribution(), 'use_fast_calculation', False))

    if not is_isotropic_fast:
        # find weighting factors from the angles and rigidities
        def pitchAngleFunctionToUse(row):
            """
            Calculate the pitch angle distribution value for a given row.
            
            Args:
                row: DataFrame row containing angleBetweenIMFinRadians and Rigidity
                
            Returns:
                The pitch angle distribution value
            """
            return momentaDist.getPitchAngleDistribution()(row["angleBetweenIMFinRadians"], row["Rigidity"])
        
        def fullRigidityPitchWeightingFactorFunctionToUse(row):
            """
            Calculate the combined rigidity and pitch angle weighting factor for a given row.
            
            Args:
                row: DataFrame row containing angleBetweenIMFinRadians and Rigidity
                
            Returns:
                The combined rigidity and pitch angle weighting factor
            """
            return momentaDist(row["angleBetweenIMFinRadians"], row["Rigidity"])

        print("calculating pitch angle weighting factors...")
        new_asymptotic_direction_DF["PitchAngleWeightingFactor"] = get_apply_method(new_asymptotic_direction_DF)(pitchAngleFunctionToUse, axis=1)

        new_asymptotic_direction_DF["Filter"] = (new_asymptotic_direction_DF["Filter"] == 1) * 1

        print("calculating rigidity weighting factors...")
        new_asymptotic_direction_DF["RigidityWeightingFactor"] = get_apply_method(new_asymptotic_direction_DF["Rigidity"])(momentaDist.getRigiditySpectrum())

        print("calculating rigidity + pitch combined weighting factors...")
        all_weighted_asymp_dirs = get_apply_method(new_asymptotic_direction_DF)(fullRigidityPitchWeightingFactorFunctionToUse, axis=1)
        new_asymptotic_direction_DF["fullRigidityPitchWeightingFactor"] = all_weighted_asymp_dirs * (new_asymptotic_direction_DF["Filter"] == 1)
    else:
        # For isotropic fast mode, set pitch angle factor to 1 and full rigidity pitch factor to rigidity factor
        print("using isotropic fast mode: setting pitch angle weighting factors to 1")
        new_asymptotic_direction_DF["PitchAngleWeightingFactor"] = 1.0
        new_asymptotic_direction_DF["Filter"] = (new_asymptotic_direction_DF["Filter"] == 1) * 1
        
        print("calculating rigidity weighting factors...")
        new_asymptotic_direction_DF["RigidityWeightingFactor"] = get_apply_method(new_asymptotic_direction_DF["Rigidity"])(momentaDist.getRigiditySpectrum())
        
        print("setting full rigidity pitch weighting factors equal to rigidity weighting factors...")
        new_asymptotic_direction_DF["fullRigidityPitchWeightingFactor"] = new_asymptotic_direction_DF["RigidityWeightingFactor"] * (new_asymptotic_direction_DF["Filter"] == 1)
    
    print("calculating energy + pitch combined weighting factors...")
    print("converting rigidities to energies...")
    new_asymptotic_direction_DF["Energy"] = PRCT.convertParticleRigidityToEnergy(new_asymptotic_direction_DF["Rigidity"], 
                                                                      particleMassAU=particle_dist.particle_species.atomicMass, 
                                                                      particleChargeAU=particle_dist.particle_species.atomicNumber)
    print("converting rigidity spectrum to energy spectrum...")
    energySpectrum = PRCT.convertParticleRigiditySpecToEnergySpec(new_asymptotic_direction_DF["Rigidity"],
                                                                  new_asymptotic_direction_DF["fullRigidityPitchWeightingFactor"],
                                                                  particleMassAU=particle_dist.particle_species.atomicMass, 
                                                                  particleChargeAU=particle_dist.particle_species.atomicNumber)

    new_asymptotic_direction_DF["fullEnergyPitchWeightingFactor"] = energySpectrum["Energy distribution values"]

    return new_asymptotic_direction_DF

def calculatePitchAngle_from_IMF_dir(interplanetary_mag_field: spaceCoords, asymptotic_direction: spaceCoords, datetime_to_run_across_UTC: dt.datetime) -> float:
    """
    Calculate the pitch angle from the Interplanetary Magnetic Field (IMF) direction.

    Parameters:
    - interplanetary_mag_field: spaceCoords
        The coordinates of the interplanetary magnetic field.
    - asymptotic_direction: spaceCoords
        The coordinates of the asymptotic direction.
    - datetime_to_run_across_UTC: dt.datetime
        The datetime to run across in UTC.

    Returns:
    - float
        The pitch angle in radians.
    """
    cartesianAsympDir = asymptotic_direction.convert("GEO", "car").data[0]
    GEOIMF = interplanetary_mag_field
    GEOIMF.ticks = spaceTicktock(datetime_to_run_across_UTC, "UTC")
    cartesianIMF = GEOIMF.convert("GEO", "car").data[0]
    return calculateAngleBetweenTheSpaceVectors(cartesianAsympDir, cartesianIMF)

def calculatePitchAngle(momentaDist: momentaDistribution, dfRow: pd.Series, datetime_to_run_across_UTC: dt.datetime) -> float:
    """
    Calculate the pitch angle.

    Parameters:
    - momentaDist: momentaDistribution
        The momenta distribution.
    - dfRow: pd.Series
        The DataFrame row.
    - datetime_to_run_across_UTC: dt.datetime
        The datetime to run across in UTC.

    Returns:
    - float
        The pitch angle in radians.
    """
    cartesianAsympDir = dfRow["Asymptotic Direction"].convert("GEO", "car").data[0]
    GEOIMF = momentaDist.getPitchAngleDistribution().interplanetary_mag_field
    GEOIMF.ticks = spaceTicktock(datetime_to_run_across_UTC, "UTC")
    cartesianIMF = GEOIMF.convert("GEO", "car").data[0]
    return calculateAngleBetweenTheSpaceVectors(cartesianAsympDir, cartesianIMF)

def calculateAngleBetweenTheSpaceVectors(cartesianAsympDir: np.ndarray, cartesianIMF: np.ndarray) -> float:
    """
    Calculate the angle between two space vectors.

    Parameters:
    - cartesianAsympDir: np.ndarray
        The Cartesian coordinates of the asymptotic direction.
    - cartesianIMF: np.ndarray
        The Cartesian coordinates of the interplanetary magnetic field.

    Returns:
    - float
        The angle between the vectors in radians.
    """
    dotProduct = np.dot(cartesianAsympDir, cartesianIMF)
    amplitude = np.linalg.norm(cartesianAsympDir) * np.linalg.norm(cartesianIMF)
    angleBetweenIMF = np.arccos(dotProduct / amplitude)
    return angleBetweenIMF
