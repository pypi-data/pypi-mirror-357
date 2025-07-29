#!/usr/bin/env python3
"""
Tests for json2png_annotation library
"""
import os
import json
import tempfile
import unittest
from PIL import Image
from json2png_annotation.converter import convert_single_annotation

class TestConversion(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a test annotation
        self.test_annotation = {
            "image.jpg": {
                "regions": {
                    "0": {
                        "shape_attributes": {
                            "all_points_x": [100, 200, 200, 100],
                            "all_points_y": [100, 100, 200, 200]
                        }
                    }
                }
            }
        }
    
    def test_convert_single_annotation(self):
        """Test converting a single annotation to a PNG mask."""
        output_path = os.path.join(self.temp_dir, "test_mask.png")
        
        # Convert the annotation
        result_path = convert_single_annotation(
            self.test_annotation,
            output_path=output_path,
            width=400,
            height=400
        )
        
        # Check that the file was created
        self.assertTrue(os.path.exists(result_path))
        self.assertEqual(output_path, result_path)
        
        # Check that the file is a valid image
        img = Image.open(result_path)
        self.assertEqual(img.size, (400, 400))
        self.assertEqual(img.mode, "L")  # L mode for grayscale
        
        # Check some pixels (square is filled with white)
        pixel_data = list(img.getdata())
        
        # Check a pixel inside the square (should be white)
        pixel_index = 150 * img.width + 150
        self.assertEqual(pixel_data[pixel_index], 255)
        
        # Check a pixel outside the square (should be black)
        pixel_index = 50 * img.width + 50
        self.assertEqual(pixel_data[pixel_index], 0)

if __name__ == "__main__":
    unittest.main() 