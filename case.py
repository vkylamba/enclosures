import cadquery as cq

# Parameters
box_length = 103  # mm
box_width = 54    # mm
box_height = 50   # mm
wall_thickness = 2.5  # increased for DIN rail strength

# DIN rail channel parameters (TS35 standard - enclosure snaps onto 35mm DIN rail)
din_rail_width = 35.0           # TS35 standard rail width (mm)
din_clearance = 0.3             # clearance per side for slide fit (mm)
din_channel_inner = din_rail_width + 2 * din_clearance  # inner channel width
din_guide_height = 10.0         # guide wall height below enclosure (mm)
din_fixed_thick = 3.0           # fixed hook side wall thickness (mm)
din_spring_thick = 2.0          # spring clip wall thickness - thinner for flex (mm)
din_hook_reach = 2.5            # inward hook depth to catch rail lip (mm)
din_hook_thick = 1.5            # vertical thickness of hook shelf (mm)
din_spring_interference = 0.3   # extra reach on spring side for snap-fit (mm)

# Fillet parameters
ext_fillet_r = 2.0      # outer vertical corners + bottom edges
lid_fillet_r = 1.5      # lid outer edges
din_fillet_r = 1.5      # DIN rail wall-to-base junction strength

# Outer dimensions (box_length/width/height are inner cavity dimensions)
outer_length = box_length + 2 * wall_thickness
outer_width = box_width + 2 * wall_thickness
outer_height = box_height + 2 * wall_thickness  # floor + cavity + top (top gets split off)

lcd_cutout = (66, 16)
lcd_offset = ((box_length - lcd_cutout[0]) / 2, (box_width - lcd_cutout[1]) / 2)
lid_height = box_height / 5

# Push button on lid (right side of LCD)
push_button_dia = 7  # mm, panel-mount momentary button

# Arduino Mega mounting-hole centres from board drawing (mm)
# Origin is board bottom-left, independent of enclosure dimensions.
board_length = 101.6
board_width = 53.3
mega_mounts = [
    (14.0, 2.5),    # First from bottom left
    (15.3, 50.8),   # First from top left
    (64.8, 7.6),    # Second from bottom left
    (64.8, 35.5),   # Second from top left
    (93.0, 2.5),    # Third from bottom left
    (88.9, 48.2),   # Third from top left
]
mount_dia = 3

# Cutouts on side walls
usb_cut_arduino = (10, 5)  # USB cutout for micro-USB and USB-C
rj45_cut = (16, 14)
audio_jack_dia = 6
num_audio_jacks = 4
first_audio_jack_center_from_left = 7.5
audio_jack_spacing_center_to_center = 12.8
audio_jack_center_height_from_bottom = 14
extra_audio_jack_center_from_left = 24.5

# Parameters for lid
lid_thickness = wall_thickness

# Snap-fit clip parameters
clip_bump_width = 5.0          # mm along wall
clip_bump_height = 2.0         # mm in Z
clip_bump_depth = 0.5          # mm protrusion from skirt
clip_y_positions = [-12, 12]   # mm from center, on each X-wall
clip_groove_extra = 0.4        # total clearance added to groove vs bump (0.2/side)
clip_groove_depth = 0.7        # mm pocket into base wall

# Alignment ledge
ledge_depth = 0.75             # mm step inward from cavity wall at top
ledge_height = 2.0             # mm tall

# Pry slot parameters (screwdriver lid removal, all 4 walls, cut from outside)
pry_slot_width = 6.0           # mm along wall
pry_slot_depth = 2.0           # mm inward from outer wall face
pry_slot_height = 2.5          # mm down from base wall top
pry_slot_x_positions = [-15, 15]  # mm from center, for Y walls (along length)
pry_slot_y_positions = [-10, 10]  # mm from center, for X walls (along width)

# Create base (box without top wall)
outer = cq.Workplane("XY").box(outer_length, outer_width, outer_height)
outer = outer.edges("|Z").fillet(ext_fillet_r)   # 4 vertical corners → round
outer = outer.edges("<Z").fillet(ext_fillet_r)   # bottom edges → round
inner = (cq.Workplane("XY")
         .workplane(offset=-outer_height/2 + wall_thickness)
         .rect(box_length, box_width)
         .extrude(outer_height - wall_thickness))
base = outer.cut(inner)

# Remove the top wall from the base
base = base.faces(">Z").workplane(-lid_thickness).split(keepBottom=True)

# Mounting holes on bottom wall (inside)
for (x, y) in mega_mounts:
    base = base.cut(
        cq.Workplane("XY")
        .workplane(offset=-outer_height/2 + wall_thickness)
        .pushPoints([(x - board_length/2, y - board_width/2)])
        .circle(mount_dia/2)
        .extrude(-wall_thickness)
    )

# Power barrel jack: 9mm diameter from bottom and left-side horizontal offset
# On YZ wall sketch: first coord is horizontal across wall, second is vertical.
power_jack_dia = 9
# In CadQuery, Y=0 is box center, so:
power_center_y = - outer_height / 2 + power_jack_dia / 2 + 3 # 3mm offset from bottom
# Horizontal placement from left side of wall
power_center_z = -outer_width / 2 + power_jack_dia / 2 + 5

power_jack_cutout = (cq.Workplane("YZ")
                     .workplane(offset=-outer_length/2)
                     .center(power_center_z, power_center_y)
                     .circle(power_jack_dia/2)
                     .extrude(wall_thickness))
base = base.cut(power_jack_cutout)

# USB cutout on left wall
# USB horizontal placement measured from right side of wall
usb_center_y = - outer_height / 2 + usb_cut_arduino[1] / 2 + 3  # 3mm offset from bottom 
usb_center_z = outer_width / 2 - usb_cut_arduino[0] / 2 - 13.5
usb_cutout = (cq.Workplane("YZ")
              .workplane(offset=-outer_length/2)
              .center(usb_center_z, usb_center_y)
              .rect(usb_cut_arduino[0], usb_cut_arduino[1])
              .extrude(wall_thickness))
base = base.cut(usb_cutout)

# RJ45 cutout: right above USB cutout (on left wall)
rj45_gap = 10  # mm gap between USB and RJ45
rj45_center_y = usb_center_y + usb_cut_arduino[1] / 2 + rj45_gap + rj45_cut[1]/2
rj45_cutout = (cq.Workplane("YZ")
               .workplane(offset=-outer_length/2)
               .center(usb_center_z, rj45_center_y)
               .rect(rj45_cut[0], rj45_cut[1])
               .extrude(wall_thickness))
base = base.cut(rj45_cutout)

# 4x 3.5mm jack cutouts on right wall
jack_center_z = -outer_height / 2 + audio_jack_center_height_from_bottom
jack_positions = [
    (
        -outer_width / 2 + first_audio_jack_center_from_left
        + i * audio_jack_spacing_center_to_center,
        jack_center_z,
    )
    for i in range(num_audio_jacks)
]
for pos in jack_positions:
    jack_hole = (cq.Workplane("YZ")
                 .workplane(offset=outer_length/2)
                 .pushPoints([pos])
                 .circle(audio_jack_dia/2)
                 .extrude(-wall_thickness))
    base = base.cut(jack_hole)

# Extra audio jacks on both adjacent Y walls from the 4-jack wall (top view).
extra_audio_jack_center_x = outer_length / 2 - extra_audio_jack_center_from_left
for y_offset in (-outer_width / 2, outer_width / 2):
    extra_jack_hole = (cq.Workplane("XZ")
                       .workplane(offset=y_offset)
                       .center(extra_audio_jack_center_x, jack_center_z)
                       .circle(audio_jack_dia/2)
                       .extrude(wall_thickness, both=True))
    base = base.cut(extra_jack_hole)


# DIN rail mounting channel on bottom of enclosure
# Two guide walls with inward-facing L-shaped hooks form a channel
# that snaps onto a standard TS35 DIN rail.
# Fixed hook side hooks first, then spring clip side snaps on.
din_channel_len = outer_length - 10  # slightly shorter than enclosure
base_z = -outer_height / 2

# --- Fixed hook side (positive Y) ---
# Guide wall extending downward from enclosure bottom
fw_inner = din_channel_inner / 2
fw_outer = fw_inner + din_fixed_thick
fixed_wall = (cq.Workplane("XY")
    .workplane(offset=base_z)
    .center(0, (fw_inner + fw_outer) / 2)
    .rect(din_channel_len, din_fixed_thick)
    .extrude(-din_guide_height))

# Fixed hook: horizontal shelf at bottom of wall, extending inward
fh_inner = fw_inner - din_hook_reach
fixed_hook = (cq.Workplane("XY")
    .workplane(offset=base_z - din_guide_height)
    .center(0, (fh_inner + fw_outer) / 2)
    .rect(din_channel_len, fw_outer - fh_inner)
    .extrude(din_hook_thick))

# --- Spring clip side (negative Y) ---
# Guide wall - thinner than fixed side to allow flex for snap-on
sw_inner = -din_channel_inner / 2
sw_outer = sw_inner - din_spring_thick
spring_wall = (cq.Workplane("XY")
    .workplane(offset=base_z)
    .center(0, (sw_inner + sw_outer) / 2)
    .rect(din_channel_len, din_spring_thick)
    .extrude(-din_guide_height))

# Spring hook: extends inward with extra interference for snap-fit
sh_inner = sw_inner + din_hook_reach + din_spring_interference
spring_hook = (cq.Workplane("XY")
    .workplane(offset=base_z - din_guide_height)
    .center(0, (sw_outer + sh_inner) / 2)
    .rect(din_channel_len, sh_inner - sw_outer)
    .extrude(din_hook_thick))

# Combine channel parts and union with base
din_channel = fixed_wall.union(fixed_hook).union(spring_wall).union(spring_hook)
din_channel = din_channel.edges(">Z").fillet(din_fillet_r / 2)
base = base.union(din_channel)

# Alignment ledge: narrows the cavity opening at the top so the skirt registers snugly
base_top_z = outer_height/2 - lid_thickness
ledge_outer = (cq.Workplane("XY")
    .workplane(offset=base_top_z - ledge_height)
    .rect(box_length, box_width)
    .extrude(ledge_height))
ledge_inner = (cq.Workplane("XY")
    .workplane(offset=base_top_z - ledge_height)
    .rect(box_length - 2*ledge_depth, box_width - 2*ledge_depth)
    .extrude(ledge_height))
base = base.union(ledge_outer.cut(ledge_inner))


# Clip grooves in base inner X-walls (4 rectangular pockets for snap-fit bumps)
groove_w = clip_bump_width + clip_groove_extra
groove_h = clip_bump_height + clip_groove_extra
lid_seated_origin_z = base_top_z - lid_height / 2
groove_center_z = lid_seated_origin_z + (-lid_height/2 + 1.0 + clip_bump_height/2)

for x_sign in [-1, 1]:
    wall_inner_x = x_sign * box_length / 2
    for y_pos in clip_y_positions:
        groove = (cq.Workplane("YZ")
            .workplane(offset=wall_inner_x)
            .center(y_pos, groove_center_z)
            .rect(groove_w, groove_h)
            .extrude(x_sign * clip_groove_depth))
        base = base.cut(groove)

# Pry slots on all 4 walls for screwdriver lid removal (cut from outer face inward)
# Y walls (front -Y and back +Y)
for x_pos in pry_slot_x_positions:
    for y_sign in [-1, 1]:
        slot = (cq.Workplane("XZ")
            .workplane(offset=y_sign * outer_width / 2)
            .center(x_pos, base_top_z - pry_slot_height / 2)
            .rect(pry_slot_width, pry_slot_height)
            .extrude(-y_sign * pry_slot_depth))
        base = base.cut(slot)

# X walls (left -X and right +X)
for y_pos in pry_slot_y_positions:
    for x_sign in [-1, 1]:
        slot = (cq.Workplane("YZ")
            .workplane(offset=x_sign * outer_length / 2)
            .center(y_pos, base_top_z - pry_slot_height / 2)
            .rect(pry_slot_width, pry_slot_height)
            .extrude(-x_sign * pry_slot_depth))
        base = base.cut(slot)


# Create lid (inset design: top plate rests on base walls, skirt fits inside)
lid_clearance = 0.75  # mm per side (room for clip bumps)
skirt_outer_l = box_length - 2 * lid_clearance
skirt_outer_w = box_width - 2 * lid_clearance
skirt_height = lid_height - lid_thickness  # skirt below the top plate

# Top plate covers the base opening
top_plate = (cq.Workplane("XY")
    .workplane(offset=lid_height / 2 - lid_thickness)
    .rect(outer_length, outer_width)
    .extrude(lid_thickness))

# Hollow skirt drops inside the base cavity
skirt_solid = (cq.Workplane("XY")
    .workplane(offset=-lid_height / 2)
    .rect(skirt_outer_l, skirt_outer_w)
    .extrude(skirt_height))
skirt_void = (cq.Workplane("XY")
    .workplane(offset=-lid_height / 2)
    .rect(skirt_outer_l - 2 * wall_thickness, skirt_outer_w - 2 * wall_thickness)
    .extrude(skirt_height))
box_lid = top_plate.union(skirt_solid.cut(skirt_void))

# Snap-fit clip bumps on skirt outer X-faces
bump_center_z = -lid_height/2 + 1.0 + clip_bump_height/2

for x_sign in [-1, 1]:
    skirt_face_x = x_sign * skirt_outer_l / 2
    for y_pos in clip_y_positions:
        bump = (cq.Workplane("YZ")
            .workplane(offset=skirt_face_x)
            .center(y_pos, bump_center_z)
            .rect(clip_bump_width, clip_bump_height)
            .extrude(x_sign * clip_bump_depth))
        box_lid = box_lid.union(bump)

# Add LCD cutout to lid
box_lid = (box_lid.faces(">Z")
       .workplane()
       .center(lcd_offset[0] + lcd_cutout[0]/2 - box_length/2,
               lcd_offset[1] + lcd_cutout[1]/2 - box_width/2)
       .rect(lcd_cutout[0], lcd_cutout[1])
       .cutThruAll())

# Add push button cutout on lid, to the right of the LCD
lcd_center_x = lcd_offset[0] + lcd_cutout[0]/2 - box_length/2
lcd_center_y = lcd_offset[1] + lcd_cutout[1]/2 - box_width/2
push_btn_x = lcd_center_x + lcd_cutout[0]/2 + push_button_dia/2 + 3  # 3mm gap
push_btn_y = lcd_center_y
box_lid = (box_lid.faces(">Z")
       .workplane()
       .center(push_btn_x, push_btn_y)
       .circle(push_button_dia/2)
       .cutThruAll())

# Fillet lid top edges for comfort when handling
box_lid = box_lid.edges(">Z").fillet(lid_fillet_r / 2)

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
