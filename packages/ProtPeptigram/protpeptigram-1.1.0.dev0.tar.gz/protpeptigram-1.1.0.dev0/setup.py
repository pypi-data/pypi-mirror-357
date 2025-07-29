from setuptools import setup, find_packages
import os
import re

# Read the version from __init__.py
with open(os.path.join('ProtPeptigram', '__init__.py'), 'r') as f:
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
    version = version_match.group(1) if version_match else '0.1.0'

# Read long description from README.md
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ProtPeptigram',
    version=version,
    author='Sanjay Krishna',
    author_email='sanjay.sondekoppagopalakrishna@monash.edu',
    description='Mapping peptides to source protein for immunopeptidiomics data analysis',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Sanpme66/ProtPeptigram',
    project_urls={
        'Documentation': 'https://github.com/Sanpme66/ProtPeptigram',
        'Bug Reports': 'https://github.com/Sanpme66/ProtPeptigram/issues',
        'Source Code': 'https://github.com/Sanpme66/ProtPeptigram',
    },
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
    install_requires=[
        'pandas>=1.3.0',
        'numpy>=1.20.0',
        'matplotlib>=3.4.0',
        'seaborn>=0.11.0',
        'biopython>=1.79',
        'rich>=10.0.0',
        'rich-argparse>=0.5.0',
        'click>=8.0.0',
    ],
    entry_points={
        'console_scripts': [
            'protpeptigram=ProtPeptigram.main:main',
        ],
    },
    include_package_data=True,
    package_data={
        'ProtPeptigram': ['data/*'],
    },
    zip_safe=False,
    keywords=['proteomics', 'peptides', 'visualization', 'bioinformatics', 'immunopeptidome'],
)