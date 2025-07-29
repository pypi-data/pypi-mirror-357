"""
Setup script for the AniMAIRE package.
"""

from setuptools import find_packages, setup
import os
import glob as gb

# get requirements for installation
lib_folder = os.path.dirname(os.path.realpath(__file__))
requirement_path = lib_folder + '/requirements.txt'
install_requires = []
if os.path.isfile(requirement_path):
    with open(requirement_path) as f:
        install_requires = f.read().splitlines()
        print("install requires:")
        print(install_requires)

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='AniMAIRE',
    packages=find_packages(exclude='pytests'),
    package_data={"AniMAIRE":[
                                "anisotropic_MAIRE_engine/data/*.csv",
                                "anisotropic_MAIRE_engine/rigidityPredictor/data/*.pkl"
                                         ]},
    version='1.4.1',
    description='Python library for running the anisotropic version of MAIRE+',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Space Environment and Protection Group, University of Surrey',
    license='CC By-NC-SA 4.0',
    url='https://github.com/ssc-maire/AniMAIRE-public',
    keywords='anisotropic MAIRE+ atmospheric ionizing radiation dose rates cosmic rays ground level enhancements GLEs protons alpha particles neutrons effective ambient equivalent aircraft aviation Earth solar system sun space magnetic field',
    install_requires=['numpy >= 1.21.6',
                        'pandarallel >= 1.6.3',
                        'pandas >= 1.3.5',
                        'ParticleRigidityCalculationTools >= 1.5.4',
                        'scipy >= 1.7.3',
                        'setuptools >= 45.2.0',
                        'spacepy >= 0.3.0',
                        'tqdm >= 4.65.0',
                        'plotly >= 5.9.0',
                        'numba >= 0.57.1',
                        'metpy >= 1.5.1',
                        'CosRayModifiedISO >= 1.2.9',
                        'AsympDirsCalculator >= 1.0.8',
                        'seaborn >= 0.13.2',
                        'geopandas >= 0.11.1',
                        'joblib >= 1.2.0',
                        'spaceweather >= 0.2.4',
                        'atmosphericRadiationDoseAndFlux >= 1.0.3',
                        'kpindex >= 2.0.0',
                        'ipywidgets >= 8.1.5',
                        'dask >= 2022.0.0',
                        'pyarrow >= 12.0.0',
                        'matplotlib >= 3.10.1',
                        'cartopy >= 0.22.0',
                        'netCDF4 >= 1.7.2',
                        'imageio >= 2.37.0',
                        'psutil >= 7.0.0',
                        'OTSO >= 1.0.16',
                        'geopy >= 2.0.0',
                        'pynverse >= 0.1.4.6',
                        'xgboost >= 1.6.0'],
    #install_requires,
    setup_requires=['pytest-runner','wheel'],
    tests_require=['pytest'],
)
