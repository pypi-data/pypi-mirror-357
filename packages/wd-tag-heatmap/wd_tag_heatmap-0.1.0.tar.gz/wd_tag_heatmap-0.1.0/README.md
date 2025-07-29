# WD Tag Heatmap

Generate attention heatmaps for WD Tagger models - visualize which parts of an image contribute to each tag prediction.

![Example heatmap grid](https://example.com/heatmap-grid.png)

## Features

- 🎯 Generate individual attention heatmaps for each detected tag
- 🖼️ Create grid visualizations of all tag heatmaps
- 📊 Export detailed tag information with confidence scores
- 🚀 Support for multiple WD Tagger v3 models
- 💻 Easy to use Python API and CLI
- 🔧 Batch processing support

## Installation

```bash
pip install wd-tag-heatmap
```

For development:
```bash
git clone https://github.com/yourusername/wd-tag-heatmap
cd wd-tag-heatmap
pip install -e ".[dev]"
```

## Quick Start

### Python API

```python
from wd_tag_heatmap import generate_tag_heatmaps

# Generate heatmaps for a single image
heatmaps, grid, labels = generate_tag_heatmaps(
    "anime_girl.jpg",
    output_dir="results",
    threshold=0.35
)

print(f"Found {len(heatmaps)} tags")
print(f"Caption: {labels.caption}")
```

### Command Line

```bash
# Process single image
wd-tag-heatmap image.jpg

# With custom settings
wd-tag-heatmap image.jpg --output results --threshold 0.5 --model SmilingWolf/wd-vit-large-tagger-v3

# Batch process
wd-tag-heatmap *.jpg --output batch_results
```

## Usage Examples

### Basic Usage

```python
from wd_tag_heatmap import generate_tag_heatmaps

# Simple usage with defaults
heatmaps, grid, labels = generate_tag_heatmaps("my_image.png")
```

### Custom Configuration

```python
from wd_tag_heatmap import generate_tag_heatmaps, AVAILABLE_MODELS

# Use a different model and threshold
heatmaps, grid, labels = generate_tag_heatmaps(
    "my_image.jpg",
    output_dir="custom_output",
    model_repo="SmilingWolf/wd-convnext-tagger-v3",
    threshold=0.5,
    save_individual_tags=True,
    save_grid=True,
    save_tags_info=True
)

# Access results programmatically
for heatmap in heatmaps[:5]:
    print(f"{heatmap.label}: {heatmap.score:.3f}")
```

### Batch Processing

```python
from wd_tag_heatmap import batch_process_images

# Process multiple images
image_paths = ["img1.jpg", "img2.png", "img3.jpg"]
batch_process_images(
    image_paths,
    output_dir="batch_results",
    threshold=0.35
)
```

### Working with Results

```python
# Get results without saving files
heatmaps, grid, labels = generate_tag_heatmaps(
    "image.jpg",
    save_individual_tags=False,
    save_grid=False,
    save_tags_info=False
)

# Access tag information
print(f"Rating tags: {labels.rating}")
print(f"Character tags: {labels.character}")
print(f"General tags: {list(labels.general.keys())[:10]}")

# Work with heatmap images
for heatmap in heatmaps[:3]:
    # heatmap.image is a PIL Image
    heatmap.image.show()
```

## Available Models

- `SmilingWolf/wd-convnext-tagger-v3`
- `SmilingWolf/wd-swinv2-tagger-v3`
- `SmilingWolf/wd-vit-tagger-v3` (default)
- `SmilingWolf/wd-vit-large-tagger-v3`
- `SmilingWolf/wd-eva02-large-tagger-v3`

## Output Structure

```
output_dir/
├── image_name_heatmap_grid.png      # Grid of all heatmaps
├── image_name_tags_info.txt         # Detailed tag information
└── individual_tags/                 # Individual heatmap images
    ├── image_name_000_1girl_0.996.png
    ├── image_name_001_solo_0.975.png
    └── ...
```

## Requirements

- Python 3.8+
- PyTorch 2.0+
- CUDA GPU recommended for faster processing

## API Reference

### `generate_tag_heatmaps()`

Main function to generate heatmaps for a single image.

**Parameters:**
- `image_path` (str): Path to input image
- `output_dir` (str): Directory for outputs (default: "heatmap_outputs")
- `model_repo` (str): Model repository (default: "SmilingWolf/wd-vit-tagger-v3")
- `threshold` (float): Confidence threshold (default: 0.35)
- `save_individual_tags` (bool): Save individual heatmaps (default: True)
- `save_grid` (bool): Save grid image (default: True)
- `save_tags_info` (bool): Save tag information (default: True)

**Returns:**
- `heatmaps` (List[Heatmap]): List of heatmap objects
- `grid` (Image): Grid visualization
- `labels` (ImageLabels): Tag information

### `batch_process_images()`

Process multiple images in batch.

**Parameters:**
- `image_paths` (List[str]): List of image paths
- Other parameters same as `generate_tag_heatmaps()`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [WD Tagger models](https://huggingface.co/SmilingWolf) by SmilingWolf
- Built with [timm](https://github.com/rwightman/pytorch-image-models)

## Citation

If you use this tool in your research, please cite:

```bibtex
@software{wd-tag-heatmap,
  title = {WD Tag Heatmap: Attention Visualization for Anime Image Tagging},
  author = {Your Name},
  year = {2024},
  url = {https://github.com/yourusername/wd-tag-heatmap}
}
```