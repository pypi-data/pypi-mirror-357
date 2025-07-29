"""Data structures for WD Tag Heatmap."""

from dataclasses import dataclass
from typing import Dict, List

import numpy as np
from PIL import Image


@dataclass
class Heatmap:
    """Container for a single tag's heatmap."""
    
    label: str
    score: float
    image: Image.Image


@dataclass
class LabelData:
    """Container for model label information."""
    
    names: List[str]
    rating: List[np.int64]
    general: List[np.int64]
    character: List[np.int64]


@dataclass
class ImageLabels:
    """Container for image tagging results."""
    
    caption: str
    booru: str
    rating: Dict[str, float]
    general: Dict[str, float]
    character: Dict[str, float]