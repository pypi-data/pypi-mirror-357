# holotol_framework/__init__.py

__version__ = "0.1.2"

# Import main classes and functions for easy access
from .data_loader import NCBIDataLoader
from .data_processor import BiologicalDataProcessor
from .framework import ExtendedHoloToLFramework
from .pipeline import comprehensive_ncbi_holotol_pipeline

# Define what gets imported when someone does "from holotol_framework import *"
__all__ = [
    "NCBIDataLoader",
    "BiologicalDataProcessor", 
    "ExtendedHoloToLFramework",
    "comprehensive_ncbi_holotol_pipeline"
]
