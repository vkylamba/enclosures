import cadquery as cq

# Parameters
box_length = 103  # mm
box_width = 54    # mm
box_height = 50   # mm
wall_thickness = 2.5
lcd_cutout = (66, 16)
lcd_offset = ((box_length - lcd_cutout[0]) / 2, (box_width - lcd_cutout[1]) / 2)
lid_height = box_height / 5

# Arduino Mega Mounting Holes (Approx spacing)
mega_mounts = [
    (5, 5), (5, 48), (97, 5), (97, 48),
    (5, 26), (97, 26)
]
mount_dia = 3

# Cutouts on side walls
usb_cut_arduino = (10, 5)  # USB cutout for micro-USB and USB-C
rj45_cut = (16, 14)
audio_jack_dia = 7
num_audio_jacks = 4

# Parameters for lid and screw bosses
lid_thickness = wall_thickness
screw_boss_dia = 7
screw_hole_dia = 3
screw_offset = 8  # distance from each edge

# Create base (box without top wall)
outer = cq.Workplane("XY").box(box_length, box_width, box_height)
inner = (cq.Workplane("XY")
         .workplane(offset=wall_thickness)
         .rect(box_length - 2*wall_thickness, box_width - 2*wall_thickness)
         .extrude(box_height - wall_thickness))
base = outer.cut(inner)

# Remove the top wall from the base
base = base.faces(">Z").workplane(-lid_thickness).split(keepBottom=True)

# Mounting holes on bottom wall (inside)
for (x, y) in mega_mounts:
    base = base.cut(
        cq.Workplane("XY")
        .workplane(offset=wall_thickness)
        .pushPoints([(x - box_length/2, y - box_width/2)])
        .circle(mount_dia/2)
        .extrude(-wall_thickness)
    )

# Power barrel jack: 9mm diameter at (30.5, 7.5) from bottom-right (not center)
# Calculate Y from bottom (vertical), Z from right (horizontal)
power_jack_dia = 9
# In CadQuery, Y=0 is box center, so:
power_center_y = - box_height / 2 + power_jack_dia / 2 + 3 # 3mm offset from bottom
# For Z, right edge is +box_width/2, so subtract offset from +box_width/2
power_center_z = box_width / 2 - power_jack_dia / 2 - 5 # 5mm offset from left edge

power_jack_cutout = (cq.Workplane("YZ")
                     .workplane(offset=-box_length/2)
                     .center(power_center_z, power_center_y)
                     .circle(power_jack_dia/2)
                     .extrude(wall_thickness))
base = base.cut(power_jack_cutout)

# USB cutout on left wall (Arduino Uno spec)
# USB: At (13.5, 7.5) from bottom-left
usb_center_y = - box_height / 2 + usb_cut_arduino[1] / 2 + 3  # 3mm offset from bottom 
usb_center_z = usb_cut_arduino[0] / 2 - box_width / 2 + 13.5  # 13.5mm from left edge
usb_cutout = (cq.Workplane("YZ")
              .workplane(offset=-box_length/2)
              .center(usb_center_z, usb_center_y)
              .rect(usb_cut_arduino[0], usb_cut_arduino[1])
              .extrude(wall_thickness))
base = base.cut(usb_cutout)

# RJ45 cutout: right above USB cutout (on left wall)
rj45_gap = 10  # mm gap between USB and RJ45
rj45_center_y = usb_center_y + usb_cut_arduino[1] / 2 + rj45_gap + rj45_cut[1]/2
rj45_cutout = (cq.Workplane("YZ")
               .workplane(offset=-box_length/2)
               .center(usb_center_z, rj45_center_y)
               .rect(rj45_cut[0], rj45_cut[1])
               .extrude(wall_thickness))
base = base.cut(rj45_cutout)

# 4x 3.5mm jack cutouts on right wall
spacing = box_width / (num_audio_jacks + 1)
jack_positions = [((i+1)*spacing - box_width/2, 0) for i in range(num_audio_jacks)]
for pos in jack_positions:
    jack_hole = (cq.Workplane("YZ")
                 .workplane(offset=box_length/2)
                 .pushPoints([pos])
                 .circle(audio_jack_dia/2)
                 .extrude(-wall_thickness))
    base = base.cut(jack_hole)


# Add screw bosses to base (at 4 corners, inset by screw_offset)
# REPLACE with screw posts on left and right walls (2 per wall, near corners)
side_screw_hole_dia_inner = 2
side_screw_offset_y = lid_height / 2
side_screw_offset_x = box_length/2 - 8  # near front/back edge

# Left wall screw holes (Y = ±box_width/2, X = ±side_screw_offset_x)
for y in [box_width/2, -box_width/2]:
    for x in [side_screw_offset_x, -side_screw_offset_x]:
        base = base.faces(">Y" if y > 0 else "<Y").workplane(centerOption="CenterOfMass").center(x, box_height/2 - side_screw_offset_y).circle(side_screw_hole_dia_inner/2).cutThruAll()


# Create lid
# Create box (outer)
outer_lid = cq.Workplane("XY").box(box_length + 2*wall_thickness, box_width + 2*wall_thickness, lid_height)
# Hollow it out
inner_lid = (cq.Workplane("XY")
         .workplane(offset=wall_thickness)
         .rect(box_length, box_width)
         .extrude(lid_height - wall_thickness))
box_lid = outer_lid.cut(inner_lid)

# Add LCD cutout to lid
box_lid = (box_lid.faces(">Z")
       .workplane()
       .center(lcd_offset[0] + lcd_cutout[0]/2 - box_length/2,
               lcd_offset[1] + lcd_cutout[1]/2 - box_width/2)
       .rect(lcd_cutout[0], lcd_cutout[1])
       .cutThruAll())

side_screw_hole_dia_outer = 3
# Add matching screw holes for side walls
for y in [lid_height/2, -lid_height/2]:
    for x in [side_screw_offset_x + wall_thickness, -side_screw_offset_x - wall_thickness]:
        box_lid = box_lid.faces(">Y" if y > 0 else "<Y").workplane(centerOption="CenterOfMass").center(x, lid_height/2 - side_screw_offset_y).circle(side_screw_hole_dia_outer/2).cutThruAll()

def create_visualization_notebook(model, output_dir="wall_views"):
    """
    Create a Jupyter notebook for 3D visualization
    """
    import os
    import json
    
    notebook_file = os.path.join(output_dir, "enclosure_visualization.ipynb")
    
    # Create notebook content
    notebook_content = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Arduino Enclosure Visualization\\n",
                    "\\n",
                    "This notebook provides 3D visualization of the Arduino enclosure design."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "source": [
                    "import cadquery as cq\\n",
                    "from jupyter_cadquery import show, set_defaults\\n",
                    "\\n",
                    "# Set default rendering options\\n",
                    "set_defaults(axes=True, grid=True)"
                ]
            },
            {
                "cell_type": "code", 
                "execution_count": None,
                "metadata": {},
                "source": [
                    "# Load the enclosure model\\n",
                    "try:\\n",
                    "    enclosure = cq.importers.importStep('lcd_arduino_enclosure.step')\\n",
                    "    print('Enclosure loaded successfully!')\\n",
                    "except:\\n",
                    "    print('Could not load STEP file. Please run the main script first.')"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None, 
                "metadata": {},
                "source": [
                    "# Display the 3D model\\n",
                    "show(enclosure)"
                ]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python", 
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.11.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    
    try:
        with open(notebook_file, 'w') as f:
            json.dump(notebook_content, f, indent=2)
        print(f"Generated Jupyter notebook: {notebook_file}")
        print("To use: cd wall_views && jupyter lab enclosure_visualization.ipynb")
    except Exception as e:
        print(f"Could not create notebook: {e}")

def preview_enclosure(base, lid, show_preview=False, export_file=False, create_notebook=False):
    """
    Preview and/or export the enclosure model (base and lid)
    
    Args:
        model: CadQuery Workplane object
        show_preview: Whether to show 3D preview (requires jupyter-cadquery or cq-editor)
        export_file: Whether to export STEP file
        generate_images: Whether to generate 2D wall images
        create_notebook: Whether to create a Jupyter notebook for visualization
    """
    if export_file:
        cq.exporters.export(base, 'output/lcd_arduino_enclosure_base.step')
        cq.exporters.export(base, 'output/lcd_arduino_enclosure_base.stl', 'STL')
        cq.exporters.export(base, 'output/lcd_arduino_enclosure_base.svg', 'SVG')
        cq.exporters.export(lid, 'output/lcd_arduino_enclosure_lid.step')
        cq.exporters.export(lid, 'output/lcd_arduino_enclosure_lid.stl', 'STL')
        cq.exporters.export(lid, 'output/lcd_arduino_enclosure_lid.svg', 'SVG')
        print("Exported 'lcd_arduino_enclosure_base.step' and 'lcd_arduino_enclosure_lid.step'")
    
    if create_notebook:
        create_visualization_notebook(base)
    
    if show_preview:
        print("3D preview disabled by default. Use the Jupyter notebook for interactive visualization.")

# Export and create notebook
preview_enclosure(base, box_lid, show_preview=False, export_file=True, create_notebook=False)
