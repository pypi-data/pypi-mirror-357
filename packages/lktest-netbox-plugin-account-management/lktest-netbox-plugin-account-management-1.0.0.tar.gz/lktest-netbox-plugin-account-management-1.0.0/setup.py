"""
Setup
"""

import os.path
import codecs
from setuptools import find_packages, setup

readme = os.path.join(os.path.dirname(__file__), 'README.md')

with open(readme, encoding='utf-8') as fh:
    long_description = fh.read()


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


setup(
    name='lktest-netbox-plugin-account-management',
    version=get_version('adestis_netbox_plugin_account_management/version.py'),
    description='ADESTIS Account Management',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/adestis/netbox-account-management',
    author='ADESTIS GmbH',
    author_email='pypi@adestis.de',
    maintainer="ADESTIS GmbH",
    maintainer_email='pypi@adestis.de',
    install_requires=[
        "paramiko"
    ],
    packages=find_packages(),
    include_package_data=True,
    license='GPLv3',
    keywords=['netbox', 'netbox-plugin', 'plugin'],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Framework :: Django',
        'Programming Language :: Python :: 3'
    ],
    project_urls={
        "Source": "https://github.com/adestis/netbox-account-management",
    },
)
