"""Image processing and heatmap generation for WD Tag Heatmap."""

import math
from typing import Dict, List, Tuple

import colorcet as cc
import numpy as np
import torch
from matplotlib.colors import LinearSegmentedColormap
from PIL import Image, ImageDraw, ImageFont
from timm.models import VisionTransformer
from torch import Tensor
from torch.nn import functional as F

from .data import Heatmap, ImageLabels, LabelData
from .models import model_device
from .utils import pil_make_grid


def get_tags(
    probs: Tensor,
    labels: LabelData,
    gen_threshold: float,
    char_threshold: float,
) -> Tuple[str, str, Dict[str, float], Dict[str, float], Dict[str, float]]:
    """Extract tags from model predictions."""
    # Convert indices+probs to labels
    probs = list(zip(labels.names, probs.numpy()))

    # First 4 labels are actually ratings
    rating_labels = dict([probs[i] for i in labels.rating])

    # General labels, pick any where prediction confidence > threshold
    gen_labels = [probs[i] for i in labels.general]
    gen_labels = dict([x for x in gen_labels if x[1] > gen_threshold])
    gen_labels = dict(sorted(gen_labels.items(), key=lambda item: item[1], reverse=True))

    # Character labels, pick any where prediction confidence > threshold
    char_labels = [probs[i] for i in labels.character]
    char_labels = dict([x for x in char_labels if x[1] > char_threshold])
    char_labels = dict(sorted(char_labels.items(), key=lambda item: item[1], reverse=True))

    # Combine general and character labels, sort by confidence
    combined_names = [x for x in gen_labels]
    combined_names.extend([x for x in char_labels])

    # Convert to a string suitable for use as a training caption
    caption = ", ".join(combined_names).replace("(", "\\(").replace(")", "\\)")
    booru = caption.replace("_", " ")

    return caption, booru, rating_labels, char_labels, gen_labels


@torch.no_grad()
def render_heatmap(
    image: Tensor,
    gradients: Tensor,
    image_feats: Tensor,
    image_probs: Tensor,
    image_labels: List[str],
    cmap: LinearSegmentedColormap = cc.m_linear_bmy_10_95_c71,
    pos_embed_dim: int = 784,
    image_size: Tuple[int, int] = (448, 448),
    add_text: bool = True,
    partial_rows: bool = True,
) -> Tuple[List[Heatmap], Image.Image]:
    """Render attention heatmaps for detected tags."""
    # Calculate heatmap dimensions
    image_hmaps = gradients.mean(2, keepdim=True).mul(image_feats.unsqueeze(0)).squeeze()
    hmap_dim = int(math.sqrt(image_hmaps.mean(-1).numel() / len(image_labels)))
    image_hmaps = image_hmaps.mean(-1).reshape(len(image_labels), -1)
    image_hmaps = image_hmaps[..., -hmap_dim ** 2:]
    image_hmaps = image_hmaps.reshape(len(image_labels), hmap_dim, hmap_dim)
    image_hmaps = image_hmaps.max(torch.zeros_like(image_hmaps))

    image_hmaps /= image_hmaps.reshape(image_hmaps.shape[0], -1).max(-1)[0].unsqueeze(-1).unsqueeze(-1)
    # Normalize to 0-1
    image_hmaps = torch.stack([(x - x.min()) / (x.max() - x.min()) for x in image_hmaps]).unsqueeze(1)
    # Interpolate to input image size
    image_hmaps = F.interpolate(image_hmaps, size=image_size, mode="bilinear").squeeze(1)

    hmap_imgs: List[Heatmap] = []
    for tag, hmap, score in zip(image_labels, image_hmaps, image_probs.cpu()):
        # Convert tensors to numpy arrays
        image_pixels = image.add(1).mul(127.5).squeeze().permute(1, 2, 0).cpu().numpy().astype(np.uint8)
        hmap_pixels = cmap(hmap.cpu().numpy(), bytes=True)[:, :, :3]
        
        # Create PIL images
        image_pil = Image.fromarray(image_pixels)
        hmap_pil = Image.fromarray(hmap_pixels)
        
        # Blend images
        blended = Image.blend(image_pil, hmap_pil, alpha=0.5)
        
        # Add text if requested
        if add_text and tag is not None:
            draw = ImageDraw.Draw(blended)
            # Try to use a default font, fall back to PIL default if not available
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
            except:
                font = ImageFont.load_default()
            
            draw.text((10, 10), tag, fill=(255, 255, 255), font=font)
            draw.text((10, 40), f"{score:.3f}", fill=(255, 255, 255), font=font)
        
        hmap_imgs.append(Heatmap(tag, score.item(), blended))

    hmap_imgs = sorted(hmap_imgs, key=lambda x: x.score, reverse=True)
    hmap_grid = pil_make_grid([x.image for x in hmap_imgs], partial_rows=partial_rows)

    return hmap_imgs, hmap_grid


def process_heatmap(
    model: VisionTransformer,
    image: Tensor,
    labels: LabelData,
    threshold: float = 0.5,
    partial_rows: bool = True,
) -> Tuple[List[Heatmap], Image.Image, ImageLabels]:
    """Process image and generate heatmaps."""
    torch_device = model_device(model)

    with torch.set_grad_enabled(True):
        features = model.forward_features(image.to(torch_device))
        probs = model.forward_head(features)
        probs = F.sigmoid(probs).squeeze(0)

        probs_mask = probs > threshold
        heatmap_probs = probs[probs_mask]

        label_indices = torch.nonzero(probs_mask, as_tuple=False).squeeze(1)
        image_labels = [labels.names[label_indices[i]] for i in range(len(label_indices))]

        eye = torch.eye(heatmap_probs.shape[0], device=torch_device)
        grads = torch.autograd.grad(
            outputs=heatmap_probs,
            inputs=features,
            grad_outputs=eye,
            is_grads_batched=True,
            retain_graph=True,
        )
        grads = grads[0].detach().requires_grad_(False)[:, 0, :, :].unsqueeze(1)

    with torch.set_grad_enabled(False):
        hmap_imgs, hmap_grid = render_heatmap(
            image=image,
            gradients=grads,
            image_feats=features,
            image_probs=heatmap_probs,
            image_labels=image_labels,
            partial_rows=partial_rows,
        )

        caption, booru, ratings, character, general = get_tags(
            probs=probs.cpu(),
            labels=labels,
            gen_threshold=threshold,
            char_threshold=threshold,
        )
        labels = ImageLabels(caption, booru, ratings, general, character)

    return hmap_imgs, hmap_grid, labels