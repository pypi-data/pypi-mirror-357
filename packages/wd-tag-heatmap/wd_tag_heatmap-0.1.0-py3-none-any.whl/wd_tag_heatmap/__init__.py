"""
WD Tag Heatmap - Attention visualization for WD Tagger models.

This package provides tools to generate attention heatmaps for each tag
detected by WD Tagger models, helping visualize which parts of an image
contribute to each tag prediction.
"""

from .generator import generate_tag_heatmaps, batch_process_images
from .models import AVAILABLE_MODELS, DEFAULT_MODEL
from .data import Heatmap, ImageLabels, LabelData

__version__ = "0.1.0"
__all__ = [
    "generate_tag_heatmaps",
    "batch_process_images",
    "AVAILABLE_MODELS",
    "DEFAULT_MODEL",
    "Heatmap",
    "ImageLabels",
    "LabelData",
]