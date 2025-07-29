"""Main generator functions for WD Tag Heatmap."""

from pathlib import Path
from typing import List, Tuple

from PIL import Image

from .data import Heatmap, ImageLabels, LabelData
from .models import DEFAULT_MODEL, load_labels_hf, load_model_and_transform
from .processing import process_heatmap
from .utils import preprocess_image


def generate_tag_heatmaps(
    image_path: str,
    output_dir: str = "heatmap_outputs",
    model_repo: str = DEFAULT_MODEL,
    threshold: float = 0.35,
    save_individual_tags: bool = True,
    save_grid: bool = True,
    save_tags_info: bool = True
) -> Tuple[List[Heatmap], Image.Image, ImageLabels]:
    """
    Generate attention heatmaps for each tag detected in an image.
    
    Args:
        image_path: Path to the input image
        output_dir: Directory to save output heatmaps
        model_repo: Model repository to use for tagging
        threshold: Confidence threshold for tag detection
        save_individual_tags: Whether to save individual heatmap for each tag
        save_grid: Whether to save the grid of all heatmaps
        save_tags_info: Whether to save tag information as text file
    
    Returns:
        Tuple of (heatmaps list, heatmap grid image, image labels)
    
    Example:
        >>> from wd_tag_heatmap import generate_tag_heatmaps
        >>> heatmaps, grid, labels = generate_tag_heatmaps(
        ...     "anime_girl.jpg",
        ...     output_dir="results",
        ...     threshold=0.35
        ... )
        >>> print(f"Found {len(heatmaps)} tags")
    """
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True, parents=True)
    
    # Create subdirectories for organization
    if save_individual_tags:
        tags_dir = output_path / "individual_tags"
        tags_dir.mkdir(exist_ok=True, parents=True)
    
    # Load and preprocess image
    image = Image.open(image_path)
    image_name = Path(image_path).stem
    
    # Load model and transform
    model, transform = load_model_and_transform(model_repo)
    
    # Load labels
    labels: LabelData = load_labels_hf(model_repo)
    
    # Preprocess image
    processed_image = preprocess_image(image, (448, 448))
    tensor_image = transform(processed_image).unsqueeze(0)
    
    # Get heatmaps and predictions
    heatmaps, heatmap_grid, image_labels = process_heatmap(
        model, tensor_image, labels, threshold
    )
    
    # Save outputs
    if save_individual_tags and heatmaps:
        print(f"Saving {len(heatmaps)} individual tag heatmaps...")
        for i, heatmap in enumerate(heatmaps):
            # Clean tag name for filename
            clean_tag = heatmap.label.replace("/", "_").replace("\\", "_").replace(":", "_")
            filename = f"{image_name}_{i:03d}_{clean_tag}_{heatmap.score:.3f}.png"
            filepath = tags_dir / filename
            heatmap.image.save(filepath)
            print(f"  Saved: {filename}")
    
    if save_grid:
        grid_path = output_path / f"{image_name}_heatmap_grid.png"
        heatmap_grid.save(grid_path)
        print(f"Saved heatmap grid: {grid_path}")
    
    if save_tags_info:
        # Save tag information to text file
        info_path = output_path / f"{image_name}_tags_info.txt"
        with open(info_path, 'w', encoding='utf-8') as f:
            f.write(f"Image: {image_path}\n")
            f.write(f"Model: {model_repo}\n")
            f.write(f"Threshold: {threshold}\n")
            f.write(f"Total tags detected: {len(heatmaps)}\n\n")
            
            f.write("=== Caption ===\n")
            f.write(f"{image_labels.caption}\n\n")
            
            f.write("=== Booru Tags ===\n")
            f.write(f"{image_labels.booru}\n\n")
            
            f.write("=== Ratings ===\n")
            for tag, score in image_labels.rating.items():
                f.write(f"{tag}: {score:.4f}\n")
            
            f.write("\n=== Character Tags ===\n")
            for tag, score in image_labels.character.items():
                f.write(f"{tag}: {score:.4f}\n")
            
            f.write("\n=== General Tags ===\n")
            for tag, score in image_labels.general.items():
                f.write(f"{tag}: {score:.4f}\n")
            
            f.write("\n=== All Detected Tags with Scores ===\n")
            for heatmap in heatmaps:
                f.write(f"{heatmap.label}: {heatmap.score:.4f}\n")
        
        print(f"Saved tag information: {info_path}")
    
    return heatmaps, heatmap_grid, image_labels


def batch_process_images(
    image_paths: List[str],
    output_dir: str = "heatmap_outputs",
    model_repo: str = DEFAULT_MODEL,
    threshold: float = 0.35,
    save_individual_tags: bool = True,
    save_grid: bool = True,
    save_tags_info: bool = True
) -> None:
    """
    Process multiple images and generate heatmaps for each.
    
    Args:
        image_paths: List of paths to input images
        output_dir: Base directory to save outputs
        model_repo: Model repository to use
        threshold: Confidence threshold
        save_individual_tags: Whether to save individual heatmaps
        save_grid: Whether to save grid images
        save_tags_info: Whether to save tag information
    
    Example:
        >>> from wd_tag_heatmap import batch_process_images
        >>> batch_process_images(
        ...     ["image1.jpg", "image2.png"],
        ...     output_dir="batch_results"
        ... )
    """
    for image_path in image_paths:
        print(f"\nProcessing: {image_path}")
        try:
            # Create subdirectory for each image
            image_name = Path(image_path).stem
            image_output_dir = Path(output_dir) / image_name
            
            generate_tag_heatmaps(
                image_path=image_path,
                output_dir=str(image_output_dir),
                model_repo=model_repo,
                threshold=threshold,
                save_individual_tags=save_individual_tags,
                save_grid=save_grid,
                save_tags_info=save_tags_info
            )
            print(f"Successfully processed: {image_path}")
        except Exception as e:
            print(f"Error processing {image_path}: {str(e)}")