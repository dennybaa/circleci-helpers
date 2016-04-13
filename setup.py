#!/usr/bin/env python
import os.path

from setuptools import setup, find_packages
from dist_utils import fetch_requirements
from dist_utils import apply_vagrant_workaround

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REQUIREMENTS_FILE = os.path.join(BASE_DIR, 'requirements.txt')

install_reqs, dep_links = fetch_requirements(REQUIREMENTS_FILE)

apply_vagrant_workaround()
setup(
    name='circleci-helpers',
    version='0.1.1',
    description='Provides useful helpers for Circle CI',
    author='Denis Baryshev',
    author_email='dennybaa@gmail.com',
    install_requires=install_reqs,
    dependency_links=dep_links,
    packages=find_packages(exclude=['setuptools', 'tests']),
    include_package_data=True,
    license="MIT",
    url='https://github.com/dennybaa/circleci-helpers',
    entry_points={
        'console_scripts': [
            'circle-matrix = circleci_helpers.matrix.main:main'
        ]
    }
)
