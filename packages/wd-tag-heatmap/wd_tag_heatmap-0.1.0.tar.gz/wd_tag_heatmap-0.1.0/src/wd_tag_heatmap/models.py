"""Model management for WD Tag Heatmap."""

from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd
import timm
import torch
from huggingface_hub import hf_hub_download
from huggingface_hub.utils import HfHubHTTPError
from timm.data import create_transform, resolve_data_config
from timm.models import VisionTransformer
from torch import Tensor, nn
from torchvision import transforms as T

from .data import LabelData

# Available models
AVAILABLE_MODELS = [
    "SmilingWolf/wd-convnext-tagger-v3",
    "SmilingWolf/wd-swinv2-tagger-v3",
    "SmilingWolf/wd-vit-tagger-v3",
    "SmilingWolf/wd-vit-large-tagger-v3",
    "SmilingWolf/wd-eva02-large-tagger-v3",
]

DEFAULT_MODEL = "SmilingWolf/wd-vit-tagger-v3"

# Model cache
model_cache: Dict[str, VisionTransformer] = {}
transform_cache: Dict[str, T.Compose] = {}

# Device to use
torch_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class RGBtoBGR(nn.Module):
    """Convert RGB to BGR color format."""
    
    def forward(self, x: Tensor) -> Tensor:
        if x.ndim == 4:
            return x[:, [2, 1, 0], :, :]
        return x[[2, 1, 0], :, :]


def model_device(model: nn.Module) -> torch.device:
    """Get the device of a model."""
    return next(model.parameters()).device


@lru_cache(maxsize=5)
def load_labels_hf(
    repo_id: str,
    revision: Optional[str] = None,
    token: Optional[str] = None,
) -> LabelData:
    """Load label data from Hugging Face hub."""
    try:
        csv_path = hf_hub_download(
            repo_id=repo_id, filename="selected_tags.csv", revision=revision, token=token
        )
        csv_path = Path(csv_path).resolve()
    except HfHubHTTPError as e:
        raise FileNotFoundError(f"selected_tags.csv failed to download from {repo_id}") from e

    df: pd.DataFrame = pd.read_csv(csv_path, usecols=["name", "category"])
    tag_data = LabelData(
        names=df["name"].tolist(),
        rating=list(np.where(df["category"] == 9)[0]),
        general=list(np.where(df["category"] == 0)[0]),
        character=list(np.where(df["category"] == 4)[0]),
    )

    return tag_data


def load_model_and_transform(repo_id: str) -> Tuple[VisionTransformer, T.Compose]:
    """Load model and transform from repository."""
    global transform_cache
    global model_cache

    if model_cache.get(repo_id, None) is None:
        # Save model to cache
        model_cache[repo_id] = timm.create_model("hf-hub:" + repo_id, pretrained=True).eval()
    model = model_cache[repo_id]

    if transform_cache.get(repo_id, None) is None:
        transforms = create_transform(**resolve_data_config(model.pretrained_cfg, model=model))
        # Hack in the RGBtoBGR transform, save to cache
        transform_cache[repo_id] = T.Compose(transforms.transforms + [RGBtoBGR()])
    transform = transform_cache[repo_id]

    return model, transform