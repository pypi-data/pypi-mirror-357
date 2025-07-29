#!/usr/bin/env python3
"""
Simple example showing how to use json2png_annotation library
"""
import os
import json
from json2png_annotation import convert_annotations
from json2png_annotation.converter import convert_single_annotation

def main():
    # Example 1: Convert all JSON files in a directory
    output_files = convert_annotations(
        input_folder="./data/annotations",
        output_folder="./data/masks",
        width=800,
        height=600
    )
    print(f"Generated {len(output_files)} PNG files")
    
    # Example 2: Convert a single JSON file with custom dimensions
    # First create a sample JSON annotation
    os.makedirs("./data/examples", exist_ok=True)
    
    # Create a simple annotation with a square and a triangle
    sample_annotation = {
        "image.jpg": {
            "regions": {
                "0": {
                    "shape_attributes": {
                        "all_points_x": [100, 200, 200, 100],
                        "all_points_y": [100, 100, 200, 200]
                    }
                },
                "1": {
                    "shape_attributes": {
                        "all_points_x": [300, 400, 350],
                        "all_points_y": [300, 300, 400]
                    }
                }
            }
        }
    }
    
    # Save to a file
    sample_file = os.path.join("./data/examples", "sample.json")
    with open(sample_file, "w") as f:
        json.dump(sample_annotation, f)
    
    # Convert using the library
    convert_single_annotation(
        sample_annotation,
        output_path="./data/examples/sample_mask.png",
        width=500,
        height=500
    )
    
    print("Generated sample mask at ./data/examples/sample_mask.png")
    
if __name__ == "__main__":
    main() 