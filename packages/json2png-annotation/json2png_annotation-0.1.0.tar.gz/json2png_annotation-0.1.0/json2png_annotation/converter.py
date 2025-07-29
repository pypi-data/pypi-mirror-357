import os
import json
from PIL import Image, ImageDraw
from typing import Dict, List, Tuple, Optional, Union

def convert_annotations(
    input_folder: str, 
    output_folder: str, 
    width: int = 800, 
    height: int = 800,
    filename_pattern: str = None
) -> List[str]:
    """
    Convert JSON annotation files in a folder to PNG masks and save them to another folder.

    Parameters:
        input_folder (str): Path to the folder containing JSON files.
        output_folder (str): Path to the folder to save PNG masks.
        width (int): Width of the output mask. Default is 800.
        height (int): Height of the output mask. Default is 800.
        filename_pattern (str): Optional pattern to filter JSON files. Default is None (all .json files).

    Returns:
        List[str]: List of paths to the generated PNG files.
    """
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    generated_files = []

    for file_name in os.listdir(input_folder):
        if not file_name.endswith('.json'):
            continue
            
        if filename_pattern and filename_pattern not in file_name:
            continue
            
        json_path = os.path.join(input_folder, file_name)
        output_paths = _process_json_file(json_path, output_folder, width, height)
        generated_files.extend(output_paths)

    return generated_files

def _process_json_file(
    json_path: str, 
    output_folder: str, 
    width: int, 
    height: int
) -> List[str]:
    """
    Process a single JSON file and convert its annotations to PNG masks.
    
    Parameters:
        json_path (str): Path to the JSON file.
        output_folder (str): Path to save the output PNG files.
        width (int): Width of the output mask.
        height (int): Height of the output mask.
        
    Returns:
        List[str]: Paths to the generated PNG files.
    """
    output_paths = []
    
    with open(json_path, 'r') as file:
        data = json.load(file)

    base_name = os.path.splitext(os.path.basename(json_path))[0]
    
    for image_name, image_data in data.items():
        if "regions" not in image_data:
            continue
            
        annotations = image_data["regions"]
        
        # Create a blank black image
        mask = Image.new("L", (width, height), 0)
        draw = ImageDraw.Draw(mask)

        # Draw each region
        for region in annotations.values():
            if "shape_attributes" not in region:
                continue
                
            shape_attrs = region["shape_attributes"]
            
            if "all_points_x" not in shape_attrs or "all_points_y" not in shape_attrs:
                continue
                
            points = list(zip(shape_attrs["all_points_x"], shape_attrs["all_points_y"]))
            draw.polygon(points, outline=255, fill=255)

        # Save the mask as a PNG image
        output_path = os.path.join(output_folder, f"{base_name}.png")
        mask.save(output_path)
        output_paths.append(output_path)
        
    return output_paths

def convert_single_annotation(
    json_data: Dict, 
    output_path: str, 
    width: int = 800, 
    height: int = 800
) -> str:
    """
    Convert a single JSON annotation object to a PNG mask.
    
    Parameters:
        json_data (Dict): JSON data containing annotations.
        output_path (str): Path to save the output PNG file.
        width (int): Width of the output mask. Default is 800.
        height (int): Height of the output mask. Default is 800.
        
    Returns:
        str: Path to the generated PNG file.
    """
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Create a blank black image
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    
    # Process all images in the JSON data
    for image_name, image_data in json_data.items():
        if "regions" not in image_data:
            continue
            
        annotations = image_data["regions"]
        
        # Draw each region
        for region in annotations.values():
            if "shape_attributes" not in region:
                continue
                
            shape_attrs = region["shape_attributes"]
            
            if "all_points_x" not in shape_attrs or "all_points_y" not in shape_attrs:
                continue
                
            points = list(zip(shape_attrs["all_points_x"], shape_attrs["all_points_y"]))
            draw.polygon(points, outline=255, fill=255)
    
    # Save the mask
    mask.save(output_path)
    return output_path 