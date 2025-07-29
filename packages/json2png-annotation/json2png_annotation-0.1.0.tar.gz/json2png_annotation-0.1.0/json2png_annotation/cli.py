#!/usr/bin/env python3
import argparse
from .converter import convert_annotations

def main():
    """Command line interface for json2png_annotation."""
    parser = argparse.ArgumentParser(
        description="Convert JSON annotation files to PNG mask images"
    )
    parser.add_argument(
        "-i", "--input", 
        required=True, 
        help="Input folder containing JSON annotation files"
    )
    parser.add_argument(
        "-o", "--output", 
        required=True, 
        help="Output folder for PNG mask images"
    )
    parser.add_argument(
        "-w", "--width", 
        type=int, 
        default=800, 
        help="Width of the output mask images (default: 800)"
    )
    parser.add_argument(
        "-t", "--height", 
        type=int, 
        default=800, 
        help="Height of the output mask images (default: 800)"
    )
    parser.add_argument(
        "-p", "--pattern", 
        help="Optional filename pattern to filter JSON files"
    )
    
    args = parser.parse_args()
    
    generated_files = convert_annotations(
        args.input, 
        args.output, 
        args.width, 
        args.height,
        args.pattern
    )
    
    print(f"Generated {len(generated_files)} PNG mask files in {args.output}")
    
if __name__ == "__main__":
    main() 