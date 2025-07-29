"""Command-line interface for WD Tag Heatmap."""

import argparse
import sys
from pathlib import Path
from typing import List

from . import __version__
from .generator import batch_process_images, generate_tag_heatmaps
from .models import AVAILABLE_MODELS, DEFAULT_MODEL


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="wd-tag-heatmap",
        description="Generate attention heatmaps for WD Tagger models",
        epilog="Example: wd-tag-heatmap image.jpg --threshold 0.5 --model SmilingWolf/wd-vit-large-tagger-v3"
    )
    
    parser.add_argument(
        "images",
        nargs="+",
        help="Path(s) to input image(s)"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="heatmap_outputs",
        help="Output directory (default: heatmap_outputs)"
    )
    
    parser.add_argument(
        "-m", "--model",
        default=DEFAULT_MODEL,
        choices=AVAILABLE_MODELS,
        help=f"Model to use (default: {DEFAULT_MODEL})"
    )
    
    parser.add_argument(
        "-t", "--threshold",
        type=float,
        default=0.35,
        help="Confidence threshold for tag detection (default: 0.35)"
    )
    
    parser.add_argument(
        "--no-individual",
        action="store_true",
        help="Don't save individual tag heatmaps"
    )
    
    parser.add_argument(
        "--no-grid",
        action="store_true",
        help="Don't save heatmap grid"
    )
    
    parser.add_argument(
        "--no-info",
        action="store_true",
        help="Don't save tag information file"
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List available models and exit"
    )
    
    return parser.parse_args()


def expand_paths(paths: List[str]) -> List[str]:
    """Expand glob patterns and return list of file paths."""
    expanded = []
    for path_str in paths:
        path = Path(path_str)
        if "*" in path_str:
            # Handle glob patterns
            parent = path.parent if path.parent.exists() else Path(".")
            pattern = path.name
            expanded.extend([str(p) for p in parent.glob(pattern) if p.is_file()])
        elif path.is_file():
            expanded.append(str(path))
        else:
            print(f"Warning: {path} is not a file, skipping")
    
    return expanded


def main():
    """Main CLI entry point."""
    args = parse_args()
    
    # Handle --list-models
    if args.list_models:
        print("Available models:")
        for model in AVAILABLE_MODELS:
            default_marker = " (default)" if model == DEFAULT_MODEL else ""
            print(f"  - {model}{default_marker}")
        sys.exit(0)
    
    # Expand file paths (handle globs)
    image_paths = expand_paths(args.images)
    
    if not image_paths:
        print("Error: No valid image files found")
        sys.exit(1)
    
    # Process images
    if len(image_paths) == 1:
        # Single image
        print(f"Processing: {image_paths[0]}")
        print("=" * 50)
        
        try:
            heatmaps, grid, labels = generate_tag_heatmaps(
                image_path=image_paths[0],
                output_dir=args.output,
                model_repo=args.model,
                threshold=args.threshold,
                save_individual_tags=not args.no_individual,
                save_grid=not args.no_grid,
                save_tags_info=not args.no_info
            )
            
            print(f"\n✓ Successfully generated {len(heatmaps)} heatmaps")
            print(f"✓ Results saved to: {args.output}/")
            
            # Print summary
            print("\nDetected tags summary:")
            print(f"- Rating tags: {len(labels.rating)}")
            print(f"- Character tags: {len(labels.character)}")
            print(f"- General tags: {len(labels.general)}")
            
            if len(heatmaps) > 0:
                print("\nTop 5 tags by confidence:")
                for i, heatmap in enumerate(heatmaps[:5]):
                    print(f"  {i+1}. {heatmap.label}: {heatmap.score:.3f}")
                    
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
    else:
        # Multiple images
        print(f"Processing {len(image_paths)} images...")
        print("=" * 50)
        
        batch_process_images(
            image_paths=image_paths,
            output_dir=args.output,
            model_repo=args.model,
            threshold=args.threshold,
            save_individual_tags=not args.no_individual,
            save_grid=not args.no_grid,
            save_tags_info=not args.no_info
        )
        
        print(f"\n✓ Batch processing complete")
        print(f"✓ Results saved to: {args.output}/")


if __name__ == "__main__":
    main()