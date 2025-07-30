#bin/python
# -*- coding: utf-8 -*-
"""
Created on 2023-10-02 16:00:00
"""
from warnings import filterwarnings
from rich.traceback import install
from ProtPeptigram.DataProcessor import PeptideDataProcessor
from ProtPeptigram.viz import ImmunoViz
install(show_locals=True)  # type: ignore

filterwarnings("ignore")
"""
Peptigram: peptides distribution across proteins

A Python package for mapping peptides to source protein and identifying high desnsity window to core prptides across diffrent source protein
"""

# Import main classes and functions
from ProtPeptigram.DataProcessor import PeptideDataProcessor
from ProtPeptigram.viz import ImmunoViz

#controll for __all__ to limit what is imported when using 'from module import *'
# __all__ = ['PeptideDataProcessor', 'ImmunoViz']

__version__ = "1.1.1-dev"
__author__ = "Sanjay Krishna,Prithvi Munday,Chen Li"
__email__ = "sanjay.sondekoppagopalakrishna@monash.edu"