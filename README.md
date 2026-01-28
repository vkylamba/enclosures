# PCB Enclosure Generator

A collection of Python scripts to generate 3D-printable enclosures for popular development boards like Raspberry Pi, Arduino Uno, Arduino Mega, and custom PCBs with LCD displays.

## Overview

This project uses [CadQuery](https://cadquery.readthedocs.io/) to programmatically design custom enclosures with precise cutouts for connectors, mounting holes, and displays. The generated models can be exported as STEP, STL, and SVG files for 3D printing or further CAD work.

## Features

- **Parametric Design**: Easy customization through Python parameters
- **Multiple Export Formats**: STEP, STL, and SVG output
- **Precise Cutouts**: Pre-configured cutouts for common connectors (USB, RJ45, audio jacks, power)
- **Mounting Holes**: Compatible with standard PCB mounting hole patterns
- **LCD Support**: Built-in LCD display cutouts
- **Two-Piece Design**: Separate base and lid components with screw mounting

## Supported Boards

Currently includes enclosure designs for:
- Arduino Mega (with LCD display)
- Custom PCBs (easily adaptable)

*More board templates coming soon: Raspberry Pi, Arduino Uno, etc.*

## Requirements

### Installation

CadQuery works best when installed via conda:

```bash
# Create a new conda environment
conda create -n cadquery-env python=3.11 -y

# Activate the environment
conda activate cadquery-env

# Install CadQuery
conda install -c conda-forge cadquery -y
```

Alternatively, you can install via pip (though conda is recommended):

```bash
pip install -r requirements.txt
```

## Usage

### Method 1: Using the Shell Script

The provided shell script automatically activates the conda environment and runs the script:

```bash
chmod +x run_cadquery.sh
./run_cadquery.sh
```

### Method 2: Manual Execution

```bash
# Activate conda environment
source /opt/anaconda3/etc/profile.d/conda.sh
conda activate cadquery-env

# Run the script
python case.py
```

## Output Files

The scripts generate the following files:

- `lcd_arduino_enclosure_base.step` - Base enclosure in STEP format
- `lcd_arduino_enclosure_base.stl` - Base enclosure for 3D printing
- `lcd_arduino_enclosure_base.svg` - 2D vector drawing of base
- `lcd_arduino_enclosure_lid.step` - Lid enclosure in STEP format
- `lcd_arduino_enclosure_lid.stl` - Lid enclosure for 3D printing
- `lcd_arduino_enclosure_lid.svg` - 2D vector drawing of lid

## Customization

The enclosures are highly customizable. Edit the parameters at the top of the Python script:

```python
# Box dimensions
box_length = 103  # mm
box_width = 54    # mm
box_height = 50   # mm
wall_thickness = 2.5

# LCD cutout
lcd_cutout = (66, 16)

# Mounting holes (add/modify as needed)
mega_mounts = [
    (5, 5), (5, 48), (97, 5), (97, 48),
    (5, 26), (97, 26)
]

# Connector cutouts
usb_cut_arduino = (10, 5)
rj45_cut = (16, 14)
audio_jack_dia = 7
```

## Current Enclosure: Arduino Mega with LCD

The `case.py` script generates an enclosure with:
- **Dimensions**: 103mm × 54mm × 50mm
- **Features**:
  - LCD display cutout (66mm × 16mm) on top lid
  - 6 mounting holes for Arduino Mega
  - Power barrel jack cutout (9mm diameter)
  - USB cutout for Arduino programming
  - RJ45 ethernet port cutout
  - 4× 3.5mm audio jack cutouts
  - Screw boss mounting system for secure lid attachment

## 3D Printing Tips

1. **Wall Thickness**: Default 2.5mm works well for most printers
2. **Support Material**: May be needed for overhangs on cutouts
3. **Layer Height**: 0.2mm recommended for good quality
4. **Infill**: 20-30% is sufficient for structural integrity
5. **Material**: PLA or PETG recommended

## Project Structure

```
.
├── case.py              # Main enclosure generator script
├── requirements.txt          # Python dependencies
├── run_cadquery.sh          # Helper script to run with conda
├── lcd_arduino_enclosure*.step  # Generated STEP files
├── lcd_arduino_enclosure*.stl   # Generated STL files (for 3D printing)
└── README.md                # This file
```

## Contributing

Contributions are welcome! To add support for new boards:

1. Create a new Python script based on `case.py`
2. Adjust dimensions and mounting holes for your target board
3. Update connector cutouts as needed
4. Submit a pull request

## License

This project is open source. Feel free to use and modify for your own projects.

## Resources

- [CadQuery Documentation](https://cadquery.readthedocs.io/)
- [CadQuery Examples](https://github.com/CadQuery/cadquery/tree/master/examples)
- [Arduino Dimensions](https://www.arduino.cc/en/Main/Products)
- [Raspberry Pi Dimensions](https://www.raspberrypi.org/documentation/)

## Troubleshooting

### CadQuery Import Error
Make sure you're using the conda environment:
```bash
conda activate cadquery-env
```

### STEP File Won't Open
Ensure you have a compatible CAD viewer installed:
- FreeCAD (free, open source)
- Fusion 360 (free for personal use)
- SolidWorks, Onshape, etc.

### 3D Print Doesn't Fit
Check your printer's calibration and adjust the `wall_thickness` parameter if needed.

## Roadmap

- [ ] Raspberry Pi 4 enclosure
- [ ] Arduino Uno enclosure
- [ ] Arduino Nano enclosure
- [ ] Custom PCB template generator
- [ ] Web-based customization interface
- [ ] Fan mount support
- [ ] Cable management features

---

**Happy Making! 🛠️**
