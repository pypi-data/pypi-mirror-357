# JSON2PNG Annotation Converter

A Python library for converting JSON annotation files (typically from annotation tools like MakesenseAI, VIA or LabelMe) to PNG mask images, useful for computer vision and machine learning tasks.

## Features

- Convert JSON annotation files to binary PNG masks
- Process multiple JSON files in a directory
- Customizable mask dimensions
- Filter JSON files by filename pattern
- Command-line interface for easy integration into pipelines
- Programmatic API for integration into Python projects

## Installation

### From PyPI (recommended)

```bash
pip install json2png-annotation
```

### From Source

```bash
git clone https://github.com/nguyentran4896/json2png-annotation.git
cd json2png-annotation
pip install -e .
```

## Usage

### Command-line Interface

```bash
# Basic usage
json2png -i /path/to/json/files -o /path/to/output/masks

# Custom dimensions
json2png -i /path/to/json/files -o /path/to/output/masks -w 1024 -t 768

# Filter JSON files by pattern
json2png -i /path/to/json/files -o /path/to/output/masks -p "car_"
```

### Python API

```python
from json2png_annotation import convert_annotations

# Convert all JSON files in a directory
output_files = convert_annotations(
    input_folder="/path/to/json/files",
    output_folder="/path/to/output/masks",
    width=800,
    height=800
)

print(f"Generated {len(output_files)} PNG files")

# With filename pattern filtering
output_files = convert_annotations(
    input_folder="/path/to/json/files",
    output_folder="/path/to/output/masks",
    filename_pattern="car_"
)

# Process a single JSON object
from json2png_annotation.converter import convert_single_annotation

with open("annotation.json", "r") as f:
    json_data = json.load(f)

output_path = convert_single_annotation(
    json_data,
    output_path="output_mask.png",
    width=800,
    height=800
)
```

## Input Format

The library expects JSON annotation files in the following format:

```json
{
  "image_name.jpg": {
    "regions": {
      "0": {
        "shape_attributes": {
          "all_points_x": [100, 200, 300, 100],
          "all_points_y": [100, 100, 200, 200]
        }
      },
      "1": {
        "shape_attributes": {
          "all_points_x": [400, 500, 500, 400],
          "all_points_y": [400, 400, 500, 500]
        }
      }
    }
  }
}
```

## Output

The output is a PNG image with black (0) background and white (255) polygon regions based on the coordinates in the JSON file.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request