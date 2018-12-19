from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name='tobiiglassesctrl',
    version='2.0-b1',
    description='A Python controller for Tobii Pro Glasses 2',
    url='https://github.com/ddetommaso/TobiiProGlasses2_PyCtrl',
    download_url='https://github.com/ddetommaso/TobiiProGlasses2_PyCtrl/archive/2.0-b1.tar.gz',
    install_requires=['netifaces'],
    author='Davide De Tommaso',
    author_email='ing.davidedetommaso@gmail.com',
    keywords=['eye-tracker','tobii','glasses', 'tobii pro glasses 2', 'tobii glasses', 'eye tracking'],
    packages=find_packages(exclude=['examples*']),
    classifiers = [
                'Programming Language :: Python :: 2.7',
                'Programming Language :: Python :: 3.5'
    ],
)
