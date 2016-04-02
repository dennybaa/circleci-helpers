#!/usr/bin/env python
import os.path

from setuptools import setup, find_packages
from dist_utils import fetch_requirements
from dist_utils import apply_vagrant_workaround

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REQUIREMENTS_FILE = os.path.join(BASE_DIR, 'requirements.txt')

install_reqs, dep_links = fetch_requirements(REQUIREMENTS_FILE)

# long_description = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

apply_vagrant_workaround()
setup(
    name='circleci-helpers',
    version='0.1.0',
    description='Extend your circle ci with matrix addon',
    long_description='asaasdas',
    author='Denis Baryshev',
    author_email='dennybaa@gmail.com',
    install_requires=install_reqs,
    dependency_links=dep_links,
    packages=find_packages(exclude=['setuptools', 'tests']),
    include_package_data=True,
    package_data={'circleci-helpers': ['*/*.yaml']},
    license="MIT",
    url='https://github.com/dennybaa/circleci-helpers',
)
