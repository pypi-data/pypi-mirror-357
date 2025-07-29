"""Utility functions for WD Tag Heatmap."""

import math
from typing import List, Tuple

from PIL import Image


def pil_ensure_rgb(image: Image.Image) -> Image.Image:
    """Convert image to RGB format."""
    # Convert to RGB/RGBA if not already (deals with palette images etc.)
    if image.mode not in ["RGB", "RGBA"]:
        image = image.convert("RGBA") if "transparency" in image.info else image.convert("RGB")
    # Convert RGBA to RGB with white background
    if image.mode == "RGBA":
        canvas = Image.new("RGBA", image.size, (255, 255, 255))
        canvas.alpha_composite(image)
        image = canvas.convert("RGB")
    return image


def pil_pad_square(
    image: Image.Image,
    fill: Tuple[int, int, int] = (255, 255, 255),
) -> Image.Image:
    """Pad image to square format."""
    w, h = image.size
    # Get the largest dimension so we can pad to a square
    px = max(image.size)
    # Pad to square with white background
    canvas = Image.new("RGB", (px, px), fill)
    canvas.paste(image, ((px - w) // 2, (px - h) // 2))
    return canvas


def preprocess_image(
    image: Image.Image,
    size_px: int | Tuple[int, int],
    upscale: bool = True,
) -> Image.Image:
    """Preprocess an image to be square and centered on a white background."""
    if isinstance(size_px, int):
        size_px = (size_px, size_px)

    # Ensure RGB and pad to square
    image = pil_ensure_rgb(image)
    image = pil_pad_square(image)

    # Resize to target size
    if image.size[0] < size_px[0] or image.size[1] < size_px[1]:
        if upscale is False:
            raise ValueError("Image is smaller than target size, and upscaling is disabled")
        image = image.resize(size_px, Image.LANCZOS)
    if image.size[0] > size_px[0] or image.size[1] > size_px[1]:
        image.thumbnail(size_px, Image.BICUBIC)

    return image


def pil_make_grid(
    images: List[Image.Image],
    max_cols: int = 8,
    padding: int = 4,
    bg_color: Tuple[int, int, int] = (40, 42, 54),  # Dracula background color
    partial_rows: bool = True,
) -> Image.Image:
    """Create a grid of images."""
    if not images:
        raise ValueError("No images provided")
        
    n_cols = min(math.floor(math.sqrt(len(images))), max_cols)
    n_rows = math.ceil(len(images) / n_cols)

    # If the final row is not full and partial_rows is False, remove a row
    if n_cols * n_rows > len(images) and not partial_rows:
        n_rows -= 1

    # Assumes all images are same size
    image_width, image_height = images[0].size

    canvas_width = ((image_width + padding) * n_cols) + padding
    canvas_height = ((image_height + padding) * n_rows) + padding

    canvas = Image.new("RGB", (canvas_width, canvas_height), bg_color)
    for i, img in enumerate(images):
        x = (i % n_cols) * (image_width + padding) + padding
        y = (i // n_cols) * (image_height + padding) + padding
        canvas.paste(img, (x, y))

    return canvas