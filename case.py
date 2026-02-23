import cadquery as cq

# Parameters
# Arduino Mega hat footprint dimensions from measurements and reference PNG (mm)
HAT_HEIGHT = 20  # mm
WALL_THICKNESS = 2.5
BOARD_RAW_LENGTH = 102.7
BOARD_RAW_WIDTH = 54.5

# Arduino Mega board drawing dimensions from reference PNG (mm)
BOX_LENGTH = BOARD_RAW_LENGTH + 1.5  # add margin for silkscreen and measurement uncertainty
BOX_WIDTH = BOARD_RAW_WIDTH + 1.5  # add margin for silkscreen and measurement uncertainty
BOX_HEIGHT = 50  # mm, from case.py

# Mounting-hole centres from board drawing (mm), origin at board bottom-left.
# Pattern in drawing: 3 x-columns (14.0, 64.8, 88.9) with 3 y-levels
# where holes exist at: left(top,bottom), middle(mid,bottom), right(top,bottom).

MEGA_MOUNTS = [
    (14.0, 2.5),    # First from bottom left
    (15.3, 50.8),   # First from top left
    (64.8, 7.6),    # Second from bottom left
    (64.8, 35.5),   # Second from top left
    (93.0, 2.5),    # Third from bottom left
    (88.9, 48.2),   # Third from top left
]
MOUNT_DIA = 3.2  # mm, diameter of mounting holes (slightly larger than M3 screws for clearance)
MOUNT_BOSS_DIA = 3.8  # mm, locator boss sized to fit Arduino 4mm board holes
MOUNT_BOSS_HEIGHT = 3.0  # mm, standoff height above inner floor
MOUNT_BOSS_PILOT_DIA = 2.4  # mm, pilot hole for self-tapping screw

# Side-wall connector specs from case.py / drawing notes (mm)
USB_CUT_W = 10
USB_CUT_H = 5
RJ45_CUT_W = 16
RJ45_CUT_H = 14
RJ45_GAP = 10
POWER_JACK_DIA = 9

# Offsets on YZ side-wall sketch in case.py (mm)
USB_FROM_RIGHT = 13.5
POWER_FROM_LEFT = 5
BOTTOM_OFFSET = 5.5

# Audio Jack from left
AUDIO_JACK_DIA = 6
AUDIO_JACK_CENTER_HEIGHT_FROM_BOTTOM = 14
FIRST_AUDIO_JACK_CENTER_FROM_LEFT = 7.5
AUDIO_JACK_SPACING_CENTER_TO_CENTER = 12.8
NUMBER_OF_AUDIO_JACKS = 4
EXTRA_AUDIO_JACK_CENTER_FROM_LEFT = 24.5


# DIN rail channel parameters (TS35 standard - enclosure snaps onto 35mm DIN rail)
DIN_RAIL_WIDTH = 35.0           # TS35 standard rail width (mm)
DIN_CLEARANCE = 0.3             # clearance per side for slide fit (mm)
DIN_CHANNEL_INNER = DIN_RAIL_WIDTH + 2 * DIN_CLEARANCE  # inner channel width
DIN_GUIDE_HEIGHT = 10.0         # guide wall height below enclosure (mm)
DIN_FIXED_THICK = 3.0           # fixed hook side wall thickness (mm)
DIN_SPRING_THICK = 2.0          # spring clip wall thickness - thinner for flex (mm)
DIN_HOOK_REACH = 2.5            # inward hook depth to catch rail lip (mm)
DIN_HOOK_THICK = 1.5            # vertical thickness of hook shelf (mm)
DIN_SPRING_INTERFERENCE = 0.3   # extra reach on spring side for snap-fit (mm)

# Fillet parameters
EXT_FILLET_R = 2.0      # outer vertical corners + bottom edges
LID_FILLET_R = 1.5      # lid outer edges
DIN_FILLET_R = 1.5      # DIN rail wall-to-base junction strength

# Outer dimensions (box_length/width/height are inner cavity dimensions)
OUTER_LENGTH = BOX_LENGTH + 2 * WALL_THICKNESS
OUTER_WIDTH = BOX_WIDTH + 2 * WALL_THICKNESS
OUTER_HEIGHT = BOX_HEIGHT + 2 * WALL_THICKNESS  # floor + cavity + top (top gets split off)

LCD_CUTOUT = (66, 16)
LCD_OFFSET = ((BOX_LENGTH - LCD_CUTOUT[0]) / 2, (BOX_WIDTH - LCD_CUTOUT[1]) / 2)
LID_HEIGHT = BOX_HEIGHT / 5

# Push button on lid (right side of LCD)
PUSH_BUTTON_DIA = 7  # mm, panel-mount momentary button

# Parameters for lid
LID_THICKNESS = WALL_THICKNESS

# Snap-fit clip parameters
CLIP_BUMP_WIDTH = 5.0          # mm along wall
CLIP_BUMP_HEIGHT = 2.0         # mm in Z
CLIP_BUMP_DEPTH = 0.5          # mm protrusion from skirt
CLIP_Y_POSITIONS = [-12, 12]   # mm from center, on each X-wall
CLIP_GROOVE_EXTRA = 0.4        # total clearance added to groove vs bump (0.2/side)
CLIP_GROOVE_DEPTH = 0.7        # mm pocket into base wall

# Alignment ledge
LEDGE_DEPTH = 0.75             # mm step inward from cavity wall at top
LEDGE_HEIGHT = 2.0             # mm tall

# Pry slot parameters (screwdriver lid removal, all 4 walls, cut from outside)
PRY_SLOT_WIDTH = 6.0           # mm along wall
PRY_SLOT_DEPTH = 2.0           # mm inward from outer wall face
PRY_SLOT_HEIGHT = 2.5          # mm down from base wall top
PRY_SLOT_X_POSITIONS = [-15, 15]  # mm from center, for Y walls (along length)
PRY_SLOT_Y_POSITIONS = [-10, 10]  # mm from center, for X walls (along width)

# Create base (box without top wall)
outer = cq.Workplane("XY").box(OUTER_LENGTH, OUTER_WIDTH, OUTER_HEIGHT)
outer = outer.edges("|Z").fillet(EXT_FILLET_R)   # 4 vertical corners → round
outer = outer.edges("<Z").fillet(EXT_FILLET_R)   # bottom edges → round
inner = (cq.Workplane("XY")
         .workplane(offset=-OUTER_HEIGHT/2 + WALL_THICKNESS)
         .rect(BOX_LENGTH, BOX_WIDTH)
         .extrude(OUTER_HEIGHT - WALL_THICKNESS))
base = outer.cut(inner)

# Remove the top wall from the base
base = base.faces(">Z").workplane(-LID_THICKNESS).split(keepBottom=True)

# Mounting bosses on bottom wall (inside)
for (x, y) in MEGA_MOUNTS:
    base = base.union(
        cq.Workplane("XY")
        .workplane(offset=-OUTER_HEIGHT/2 + WALL_THICKNESS)
        .pushPoints([(x - BOARD_RAW_LENGTH/2, y - BOARD_RAW_WIDTH/2)])
        .circle(MOUNT_BOSS_DIA/2)
        .extrude(MOUNT_BOSS_HEIGHT)
    )

# Pilot holes in bosses for screw fastening
for (x, y) in MEGA_MOUNTS:
    base = base.cut(
        cq.Workplane("XY")
        .workplane(offset=-OUTER_HEIGHT/2 + WALL_THICKNESS + MOUNT_BOSS_HEIGHT)
        .pushPoints([(x - BOARD_RAW_LENGTH/2, y - BOARD_RAW_WIDTH/2)])
        .circle(MOUNT_BOSS_PILOT_DIA/2)
        .extrude(-MOUNT_BOSS_HEIGHT)
    )

# Power barrel jack: 9mm diameter from bottom and left-side horizontal offset
# On YZ wall sketch: first coord is horizontal across wall, second is vertical.
power_jack_dia = 9
# In CadQuery, Y=0 is box center, so:
power_center_y = - OUTER_HEIGHT / 2 + power_jack_dia / 2 + BOTTOM_OFFSET
# Horizontal placement from left side of wall
power_center_z = -OUTER_WIDTH / 2 + power_jack_dia / 2 + POWER_FROM_LEFT

power_jack_cutout = (cq.Workplane("YZ")
                     .workplane(offset=-OUTER_LENGTH/2)
                     .center(power_center_z, power_center_y)
                     .circle(power_jack_dia/2)
                     .extrude(WALL_THICKNESS))
base = base.cut(power_jack_cutout)

# USB cutout on left wall
usb_cut_arduino = (USB_CUT_W, USB_CUT_H)  # width and height of cutout on wall
# USB horizontal placement measured from right side of wall
usb_center_y = - OUTER_HEIGHT / 2 + usb_cut_arduino[1] / 2 + BOTTOM_OFFSET
usb_center_z = OUTER_WIDTH / 2 - usb_cut_arduino[0] / 2 - USB_FROM_RIGHT
usb_cutout = (cq.Workplane("YZ")
              .workplane(offset=-OUTER_LENGTH/2)
              .center(usb_center_z, usb_center_y)
              .rect(usb_cut_arduino[0], usb_cut_arduino[1])
              .extrude(WALL_THICKNESS))
base = base.cut(usb_cutout)

# RJ45 cutout: right above USB cutout (on left wall)
rj45_cut = (RJ45_CUT_W, RJ45_CUT_H)  # width and height of cutout on wall
rj45_gap = 10  # mm gap between USB and RJ45
rj45_center_y = usb_center_y + usb_cut_arduino[1] / 2 + rj45_gap + rj45_cut[1]/2
rj45_cutout = (cq.Workplane("YZ")
               .workplane(offset=-OUTER_LENGTH/2)
               .center(usb_center_z, rj45_center_y)
               .rect(rj45_cut[0], rj45_cut[1])
               .extrude(WALL_THICKNESS))
base = base.cut(rj45_cutout)

# 4x 3.5mm jack cutouts on right wall
jack_center_z = -OUTER_HEIGHT / 2 + AUDIO_JACK_CENTER_HEIGHT_FROM_BOTTOM + BOTTOM_OFFSET
jack_positions = [
    (
        -OUTER_WIDTH / 2
        + FIRST_AUDIO_JACK_CENTER_FROM_LEFT
        + i * AUDIO_JACK_SPACING_CENTER_TO_CENTER,
        jack_center_z,
    )
    for i in range(4)
]
for pos in jack_positions:
    jack_hole = (cq.Workplane("YZ")
                .workplane(offset=OUTER_LENGTH / 2)
                .center(pos[0], pos[1])
                .circle(AUDIO_JACK_DIA/2)
                .extrude(-WALL_THICKNESS))
    base = base.cut(jack_hole)

# Extra audio jacks on both adjacent Y walls from the 4-jack wall (top view).
extra_audio_jack_center_x = OUTER_LENGTH / 2 - EXTRA_AUDIO_JACK_CENTER_FROM_LEFT
extra_jack_hole = (cq.Workplane("XZ")
                   .center(extra_audio_jack_center_x, jack_center_z)
                   .circle(AUDIO_JACK_DIA/2)
                   .extrude(OUTER_WIDTH + 2 * WALL_THICKNESS, both=True))
base = base.cut(extra_jack_hole)


# DIN rail mounting channel on bottom of enclosure
# Two guide walls with inward-facing L-shaped hooks form a channel
# that snaps onto a standard TS35 DIN rail.
# Fixed hook side hooks first, then spring clip side snaps on.
din_channel_len = OUTER_LENGTH - 10  # slightly shorter than enclosure
base_z = -OUTER_HEIGHT / 2

# --- Fixed hook side (positive Y) ---
# Guide wall extending downward from enclosure bottom
fw_inner = DIN_CHANNEL_INNER / 2
fw_outer = fw_inner + DIN_FIXED_THICK
fixed_wall = (cq.Workplane("XY")
    .workplane(offset=base_z)
    .center(0, (fw_inner + fw_outer) / 2)
    .rect(din_channel_len, DIN_FIXED_THICK)
    .extrude(-DIN_GUIDE_HEIGHT))

# Fixed hook: horizontal shelf at bottom of wall, extending inward
fh_inner = fw_inner - DIN_HOOK_REACH
fixed_hook = (cq.Workplane("XY")
    .workplane(offset=base_z - DIN_GUIDE_HEIGHT)
    .center(0, (fh_inner + fw_outer) / 2)
    .rect(din_channel_len, fw_outer - fh_inner)
    .extrude(DIN_HOOK_THICK))

# --- Spring clip side (negative Y) ---
# Guide wall - thinner than fixed side to allow flex for snap-on
sw_inner = -DIN_CHANNEL_INNER / 2
sw_outer = sw_inner - DIN_SPRING_THICK
spring_wall = (cq.Workplane("XY")
    .workplane(offset=base_z)
    .center(0, (sw_inner + sw_outer) / 2)
    .rect(din_channel_len, DIN_SPRING_THICK)
    .extrude(-DIN_GUIDE_HEIGHT))

# Spring hook: extends inward with extra interference for snap-fit
sh_inner = sw_inner + DIN_HOOK_REACH + DIN_SPRING_INTERFERENCE
spring_hook = (cq.Workplane("XY")
    .workplane(offset=base_z - DIN_GUIDE_HEIGHT)
    .center(0, (sw_outer + sh_inner) / 2)
    .rect(din_channel_len, sh_inner - sw_outer)
    .extrude(DIN_HOOK_THICK))

# Combine channel parts and union with base
din_channel = fixed_wall.union(fixed_hook).union(spring_wall).union(spring_hook)
din_channel = din_channel.edges(">Z").fillet(DIN_FILLET_R / 2)
base = base.union(din_channel)

# Alignment ledge: narrows the cavity opening at the top so the skirt registers snugly
base_top_z = OUTER_HEIGHT/2 - LID_THICKNESS
ledge_outer = (cq.Workplane("XY")
    .workplane(offset=base_top_z - LEDGE_HEIGHT)
    .rect(BOX_LENGTH, BOX_WIDTH)
    .extrude(LEDGE_HEIGHT))
ledge_inner = (cq.Workplane("XY")
    .workplane(offset=base_top_z - LEDGE_HEIGHT)
    .rect(BOX_LENGTH - 2*LEDGE_DEPTH, BOX_WIDTH - 2*LEDGE_DEPTH)
    .extrude(LEDGE_HEIGHT))
base = base.union(ledge_outer.cut(ledge_inner))


# Clip grooves in base inner X-walls (4 rectangular pockets for snap-fit bumps)
groove_w = CLIP_BUMP_WIDTH + CLIP_GROOVE_EXTRA
groove_h = CLIP_BUMP_HEIGHT + CLIP_GROOVE_EXTRA
lid_seated_origin_z = base_top_z - LID_HEIGHT / 2
groove_center_z = lid_seated_origin_z + (-LID_HEIGHT/2 + 1.0 + CLIP_BUMP_HEIGHT/2)

for x_sign in [-1, 1]:
    wall_inner_x = x_sign * BOX_LENGTH / 2
    for y_pos in CLIP_Y_POSITIONS:
        groove = (cq.Workplane("YZ")
            .workplane(offset=wall_inner_x)
            .center(y_pos, groove_center_z)
            .rect(groove_w, groove_h)
            .extrude(x_sign * CLIP_GROOVE_DEPTH))
        base = base.cut(groove)

# Pry slots on all 4 walls for screwdriver lid removal (cut from outer face inward)
# Y walls (front -Y and back +Y)
for x_pos in PRY_SLOT_X_POSITIONS:
    for y_sign in [-1, 1]:
        slot = (cq.Workplane("XZ")
            .workplane(offset=y_sign * OUTER_WIDTH / 2)
            .center(x_pos, base_top_z - PRY_SLOT_HEIGHT / 2)
            .rect(PRY_SLOT_WIDTH, PRY_SLOT_HEIGHT)
            .extrude(-y_sign * PRY_SLOT_DEPTH))
        base = base.cut(slot)

# X walls (left -X and right +X)
for y_pos in PRY_SLOT_Y_POSITIONS:
    for x_sign in [-1, 1]:
        slot = (cq.Workplane("YZ")
            .workplane(offset=x_sign * OUTER_LENGTH / 2)
            .center(y_pos, base_top_z - PRY_SLOT_HEIGHT / 2)
            .rect(PRY_SLOT_WIDTH, PRY_SLOT_HEIGHT)
            .extrude(-x_sign * PRY_SLOT_DEPTH))
        base = base.cut(slot)


# Create lid (inset design: top plate rests on base walls, skirt fits inside)
lid_clearance = 0.75  # mm per side (room for clip bumps)
skirt_outer_l = BOX_LENGTH - 2 * lid_clearance
skirt_outer_w = BOX_WIDTH - 2 * lid_clearance
skirt_height = LID_HEIGHT - LID_THICKNESS  # skirt below the top plate

# Top plate covers the base opening
top_plate = (cq.Workplane("XY")
    .workplane(offset=LID_HEIGHT / 2 - LID_THICKNESS)
    .rect(BOX_LENGTH, BOX_WIDTH)
    .extrude(LID_THICKNESS))

# Hollow skirt drops inside the base cavity
skirt_solid = (cq.Workplane("XY")
    .workplane(offset=-LID_HEIGHT / 2)
    .rect(skirt_outer_l, skirt_outer_w)
    .extrude(skirt_height))
skirt_void = (cq.Workplane("XY")
    .workplane(offset=-LID_HEIGHT / 2)
    .rect(skirt_outer_l - 2 * WALL_THICKNESS, skirt_outer_w - 2 * WALL_THICKNESS)
    .extrude(skirt_height))
box_lid = top_plate.union(skirt_solid.cut(skirt_void))

# Snap-fit clip bumps on skirt outer X-faces
bump_center_z = -LID_HEIGHT/2 + 1.0 + CLIP_BUMP_HEIGHT/2

for x_sign in [-1, 1]:
    skirt_face_x = x_sign * skirt_outer_l / 2
    for y_pos in CLIP_Y_POSITIONS:
        bump = (cq.Workplane("YZ")
            .workplane(offset=skirt_face_x)
            .center(y_pos, bump_center_z)
            .rect(CLIP_BUMP_WIDTH, CLIP_BUMP_HEIGHT)
            .extrude(x_sign * CLIP_BUMP_DEPTH))
        box_lid = box_lid.union(bump)

# Add LCD cutout to lid
lcd_cutout = (66, 16)
lcd_offset = ((BOX_LENGTH - lcd_cutout[0]) / 2, (BOX_WIDTH - lcd_cutout[1]) / 2)
lid_height = BOX_HEIGHT / 5

box_lid = (box_lid.faces(">Z")
       .workplane()
       .center(lcd_offset[0] + lcd_cutout[0]/2 - BOX_LENGTH/2,
               lcd_offset[1] + lcd_cutout[1]/2 - BOX_WIDTH/2)
       .rect(lcd_cutout[0], lcd_cutout[1])
       .cutThruAll())

# Add push button cutout on lid, to the right of the LCD
lcd_center_x = lcd_offset[0] + lcd_cutout[0]/2 - BOX_LENGTH/2
lcd_center_y = lcd_offset[1] + lcd_cutout[1]/2 - BOX_WIDTH/2
push_btn_x = lcd_center_x + lcd_cutout[0]/2 + PUSH_BUTTON_DIA/2 + 3  # 3mm gap
push_btn_y = lcd_center_y
box_lid = (box_lid.faces(">Z")
       .workplane()
       .center(push_btn_x, push_btn_y)
       .circle(PUSH_BUTTON_DIA/2)
       .cutThruAll())

# Fillet lid top edges for comfort when handling
box_lid = box_lid.edges(">Z").fillet(LID_FILLET_R / 2)

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
