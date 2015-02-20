import os
import re
import glob
from setuptools import (setup, find_packages)
from pip.req import parse_requirements

def version(package):
    """
    Return package version as listed in the `__init__.py` `__version__`
    variable.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)
    

def requires():
    with open('requirements.txt') as f:
      return f.read().splitlines()


def readme():
    with open("README.rst") as f:
        return f.read()


setup(
    name = 'qiprofile-rest-client',
    version = version('qiprofile_rest_client'),
    author = 'OHSU Knight Cancer Institute',
    author_email = 'loneyf@ohsu.edu',
    packages = find_packages(),
    include_package_data = True,
    scripts = glob.glob('bin/*'),
    url = 'http://qiprofile-rest-client.readthedocs.org/en/latest/',
    description = 'qiprofile-rest-client interacts with a qiprofile REST server.',
    long_description = readme(),
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Environment :: Web Environment',
        'Intended Audience :: Science/Research',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Natural Language :: English'
    ],
    install_requires = requires()
)
