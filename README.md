# Spanish Playing Cards Extractor

This repository contains tools for extracting individual playing cards from sheet/tilemap images. It includes both specialized scripts for specific card models and a robust, unified script that handles multiple layouts and background types.

## Features

- **Unified Extraction**: A single script (`ExtractCardsUnified.py`) that works across different card sheets.
- **Robust Detection**: Uses OpenCV to identify cards on various backgrounds (black, white, or complex).
- **Auto-Deskewing**: Automatically straightens slightly rotated or misaligned cards using perspective transforms.
- **Intelligent Sorting**: Groups detected cards into rows and columns based on their spatial coordinates for consistent naming.
- **Customizable**: Supports custom suit naming and grid configurations.
- **Clean Results**: Applies a slight internal crop to remove any remaining border or background residue.

## Repository Structure

- `Braja Espanola/`: Contains a full Spanish deck sheet and its specific extraction script.
- `Modelo Cádiz/`: Contains a "Cádiz pattern" sheet and its specific extraction script.
- `Modelo Nacional/`: Contains a "Spanish National pattern" sheet and its specific extraction script.
- `ExtractCardsUnified.py`: The robust, unified extraction tool.
- `LICENSE`: Creative Commons Attribution 4.0 International license.

## Installation

To use these scripts, you need Python 3 and the following dependencies:

```bash
pip install opencv-python-headless numpy Pillow
```

## Usage

### Unified Extraction (Recommended)

The `ExtractCardsUnified.py` script is designed to be the most robust and versatile tool in this repository. It uses computer vision to detect and extract cards.

Run it directly to process all three provided examples:

```bash
python3 ExtractCardsUnified.py
```

To use it in your own code:

```python
from ExtractCardsUnified import extract_cards

# Example: Process a custom sheet
extract_cards(
    image_path="path/to/your/sheet.png",
    output_dir="extracted_output",
    suit_names=["oros", "copas", "espadas", "bastos"],
    cards_per_row=12
)
```

### Specialized Scripts

Each subfolder contains a specialized script tailored for its respective image. These are useful for understanding simpler extraction methods like fixed-grid slicing or basic thresholding.

- `Braja Espanola/ExtractBraja.py`: Uses a dynamic detection method based on a black background threshold.
- `Modelo Cádiz/ExtractCadiz.py`: Uses a fixed mathematical grid with manual trimming.
- `Modelo Nacional/ExtractNacional.py`: Uses a fixed mathematical grid with manual trimming.

## Technical Details

The unified script follows this pipeline:
1. **Preprocessing**: Grayscale conversion and Gaussian blurring.
2. **Edge Detection**: Canny algorithm to find card boundaries.
3. **Contour Analysis**: Identifies card-like shapes based on area and aspect ratio.
4. **Perspective Transform**: Straightens each card by mapping its four corners to a perfect rectangle.
5. **Spatial Sorting**: Groups cards into rows (by Y-coordinate) and sorts each row (by X-coordinate).
6. **Output**: Saves each card with a clean name based on its grid position.

## License

This project is licensed under the [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE) license.
