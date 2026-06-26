import cadquery as cq

# Parameters
# Arduino Mega hat footprint dimensions from measurements and reference PNG (mm)
HAT_HEIGHT = 20  # mm
WALL_THICKNESS = 2.5

# Arduino Mega board drawing dimensions from reference PNG (mm)
# Keep these aligned with tests: 106.5 x 57.0 inner cavity.
BOARD_RAW_LENGTH = 105.0
BOARD_RAW_WIDTH = 55.5
BOX_LENGTH = BOARD_RAW_LENGTH + 1.5  # add margin for silkscreen and measurement uncertainty
BOX_WIDTH = BOARD_RAW_WIDTH + 1.5  # add margin for silkscreen and measurement uncertainty
BOX_HEIGHT = 50  # mm, from case.py

# Mounting-hole centres from board drawing (mm), origin at board bottom-left.
# Pattern in drawing: 3 x-columns (14.0, 64.8, 88.9) with 3 y-levels
# where holes exist at: left(top,bottom), middle(mid,bottom), right(top,bottom).

MEGA_MOUNTS = [
    (14.75, 3.25),   # First from bottom left
    (16.05, 51.55),  # First from top left
    (65.55, 8.35),   # Second from bottom left
    (65.55, 36.25),  # Second from top left
    (93.75, 3.25),   # Third from bottom left
    (89.65, 48.95),  # Third from top left
]

MOUNT_BOSS_DIA = 5.0  # mm, locator boss sized to fit Arduino 4mm board holes
MOUNT_BOSS_HEIGHT = 3.0  # mm, standoff height above inner floor
MOUNT_BOSS_PILOT_DIA = 2.4  # mm, pilot hole for self-tapping screw

# Side-wall connector specs from case.py / drawing notes (mm)
USB_CUT_W = 15
USB_CUT_H = 8
RJ45_CUT_W = 15
RJ45_CUT_H = 15
POWER_JACK_W = 10
POWER_JACK_H = 15

# Offsets on YZ side-wall sketch in case.py (mm)
# For Mona 1.3
USB_BOTTOM_OFFSET = 0
USB_FROM_RIGHT = 13.5
POWER_FROM_LEFT = 8
BOTTOM_OFFSET = 7 
AUDIO_JACK_CENTER_HEIGHT_FROM_BOTTOM = 16
RJ_45_BOTTOM_OFFSET = 15
RJ45_FROM_RIGHT = 13.5

# For Mona 1.4
# USB_BOTTOM_OFFSET = 15
# USB_FROM_RIGHT = 25
# POWER_FROM_LEFT = 6
# BOTTOM_OFFSET = 7
# AUDIO_JACK_CENTER_HEIGHT_FROM_BOTTOM = 6.5
# RJ_45_BOTTOM_OFFSET = 0
# RJ45_FROM_RIGHT = 5

# Audio Jack from left
AUDIO_JACK_DIA = 7.35  # mm, 1/4" stereo jack clearance
FIRST_AUDIO_JACK_CENTER_FROM_LEFT = 8
AUDIO_JACK_SPACING_1_TO_2 = 12.8
AUDIO_JACK_SPACING_2_TO_3 = 16.4
AUDIO_JACK_SPACING_3_TO_4 = 12.8
NUMBER_OF_AUDIO_JACKS = 4
EXTRA_AUDIO_JACK_CENTER_FROM_LEFT = 29

JACKS_DISTANCES_FROM_WALL =[
    0,
    AUDIO_JACK_SPACING_1_TO_2,
    AUDIO_JACK_SPACING_1_TO_2 + AUDIO_JACK_SPACING_2_TO_3, 
    AUDIO_JACK_SPACING_1_TO_2 + AUDIO_JACK_SPACING_2_TO_3 + AUDIO_JACK_SPACING_3_TO_4
]

# Pluggable end-wall panels (snap tabs into floor + Y-wall holes)
PLUG_PANEL_CLEARANCE = 0.2                  # mm, hole clearance around snap tabs
PLUG_PANEL_THICKNESS = WALL_THICKNESS
PLUG_SNAP_TAB_SPAN = WALL_THICKNESS         # mm, tab length along wall face
PLUG_SNAP_TAB_THICK = 3 * WALL_THICKNESS    # mm, tab width on panel face


def add_snap_tab_holes(base, tab_center_x, floor_inner_z, panel_z_center):
    """Cut floor + Y-wall retention holes for a pluggable end panel."""
    snap_hole_span = PLUG_SNAP_TAB_SPAN + PLUG_PANEL_CLEARANCE
    snap_hole_thick = PLUG_SNAP_TAB_THICK + PLUG_PANEL_CLEARANCE

    floor_tab_hole = (cq.Workplane("XY")
        .workplane(offset=floor_inner_z)
        .center(tab_center_x, 0)
        .rect(snap_hole_span, snap_hole_thick)
        .extrude(-(WALL_THICKNESS + 0.2)))
    base = base.cut(floor_tab_hole)

    for y_sign in [-1, 1]:
        y_inner_face = y_sign * BOX_WIDTH / 2
        tab_hole = (cq.Workplane("XZ")
            .workplane(offset=y_inner_face)
            .center(tab_center_x, panel_z_center)
            .rect(snap_hole_span, snap_hole_thick)
            .extrude(y_sign * (WALL_THICKNESS + 0.2)))
        base = base.cut(tab_hole)
    return base


def add_snap_tabs(panel, tab_center_x, floor_inner_z, panel_z_center):
    """Add floor + Y-edge snap tabs to a pluggable end panel."""
    panel = panel.union(
        cq.Workplane("XY")
        .workplane(offset=floor_inner_z)
        .center(tab_center_x, 0)
        .rect(WALL_THICKNESS, PLUG_SNAP_TAB_THICK)
        .extrude(-WALL_THICKNESS))

    for y_sign in [-1, 1]:
        y_edge = y_sign * BOX_WIDTH / 2
        side_tab = (cq.Workplane("XZ")
            .workplane(offset=y_edge)
            .center(tab_center_x, panel_z_center)
            .rect(PLUG_SNAP_TAB_SPAN, PLUG_SNAP_TAB_THICK)
            .extrude(y_sign * WALL_THICKNESS))
        panel = panel.union(side_tab)
    return panel

# Bottom mounting slots for external DIN rail clamps (2x oval for adjustment)
DIN_CLAMP_HOLE_DIA = 4.2       # mm, M4-style clearance (slot width)
DIN_CLAMP_SLOT_ELONGATION = 4.0  # mm extra length along X for wiggle room
DIN_CLAMP_HOLE_SPACING = 70.0  # mm, center-to-center along enclosure length


# Fillet parameters
EXT_FILLET_R = 2.0      # outer vertical corners + bottom edges
LID_FILLET_R = 1.5      # lid outer edges

# Outer dimensions (box_length/width/height are inner cavity dimensions)
OUTER_LENGTH = BOX_LENGTH + 2 * WALL_THICKNESS
OUTER_WIDTH = BOX_WIDTH + 2 * WALL_THICKNESS
OUTER_HEIGHT = BOX_HEIGHT + 2 * WALL_THICKNESS  # floor + cavity + top (top gets split off)

LCD_CUTOUT = (68, 18)
LCD_OFFSET = ((BOX_LENGTH - LCD_CUTOUT[0]) / 2, (BOX_WIDTH - LCD_CUTOUT[1]) / 2)
LID_HEIGHT = BOX_HEIGHT / 5

# Living hinge press tab on lid (right side of LCD, actuates 6x6 mm tactile switch)
LIVING_HINGE_THICKNESS = 0.5   # mm, thin flex layer at hinge (print in PETG)
LIVING_HINGE_WIDTH = 3.0       # mm, hinge span in Y
TAB_LENGTH = 10.0              # mm, press tab extent in X
TAB_WIDTH = 8.0                # mm, press tab span in Y
TAB_GAP_FROM_LCD = 3.0         # mm, gap from LCD right edge to hinge
SLOT_CLEARANCE = 0.6           # mm, kerf around tab freeing it on 3 sides

# 6x6x5 mm DIP tactile switch holder (lid inner side, behind living hinge tab)
SWITCH_BODY_W = 6.0              # mm, switch footprint width/depth
SWITCH_BODY_H = 5.0              # mm, switch body height into lid
SWITCH_CLEARANCE = 0.15          # mm, cavity clearance per side
SWITCH_HOLDER_WALL = 1.0         # mm, retention wall thickness around cavity
SWITCH_HOLDER_LIP = 0.45         # mm, inward snap lip to retain switch body
SWITCH_HOLDER_LIP_HEIGHT = 0.8   # mm, lip vertical extent at cavity floor
SWITCH_PLUNGER_GAP = 0.4         # mm, air gap between flex tab and plunger at rest
SWITCH_SUPPORT_FLOOR = 1.0       # mm, bridge floor thickness (fixed skirt tie-in)

# Parameters for lid
LID_THICKNESS = WALL_THICKNESS

# LCD holder clip parameters on cap inner side 
# https://radiant-display.com/products/16x2-lcd-display-module-rd1602b
LCD_MODULE_OUTER_W = 80 + 2 * WALL_THICKNESS + 2  # 80mm PCB + 2x1.5mm bezel
LCD_MODULE_OUTER_H = 36 + 2 * WALL_THICKNESS + 2  # 36mm PCB + 2x1.5mm bezel
LCD_MODULE_HEIGHT = 8.5 + WALL_THICKNESS + 1  # 8.5mm PCB + 1.5mm bezel + 1mm clearance
LCD_CLIP_EDGE_INSET = 1.5
LCD_CLIP_SPAN = 8.0
LCD_CLIP_THICKNESS = 3.0
LCD_CLIP_HOLD_OVERLAP = 1.0
LCD_CLIP_DEPTH = LCD_MODULE_HEIGHT - LCD_CLIP_HOLD_OVERLAP + 0.3
LCD_PCB_THICKNESS = 1.6
LCD_CLIP_GROOVE_DEPTH = 1.2
LCD_CLIP_GROOVE_MARGIN = 0.6
LCD_CLIP_GROOVE_TOP_OFFSET = 2.0
LCD_CLIP_SNAP_LIP = 0.7
LCD_CLIP_SNAP_LIP_HEIGHT = 1.0
LCD_CLIP_SNAP_LIP_Z_OFFSET = 1.0

# Snap-fit clip parameters
CLIP_BUMP_WIDTH = 5.0          # mm along wall
CLIP_BUMP_HEIGHT = 2.0         # mm in Z
CLIP_BUMP_DEPTH = 0.3          # mm protrusion from skirt (gentle engagement)
CLIP_Y_POSITIONS = [0]         # mm from center, on each X-wall (1 centered clip per wall)
CLIP_X_POSITIONS = [0]         # mm from center, on each Y-wall (1 centered clip per wall)

# Pry chamfer parameters (screwdriver lid removal, 2 opposing Y-walls)
PRY_CHAMFER_SPAN = 10.0        # mm along wall (width of chamfered section)
PRY_CHAMFER_DEPTH = 1.5        # mm vertical drop (45° bevel at parting line)

# Create base (box without top wall)
outer = cq.Workplane("XY").box(OUTER_LENGTH, OUTER_WIDTH, OUTER_HEIGHT)
outer = outer.edges("|Z").fillet(EXT_FILLET_R)   # 4 vertical corners → round
outer = outer.edges("<Z").fillet(EXT_FILLET_R)   # bottom edges → round
inner = (cq.Workplane("XY")
         .workplane(offset=-OUTER_HEIGHT/2 + WALL_THICKNESS)
         .rect(OUTER_LENGTH, BOX_WIDTH)  # open both ends for pluggable panels
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

# Pluggable end panels: snap holes in floor + Y walls (+X audio, -X USB/power/RJ45).
floor_inner_z = -OUTER_HEIGHT / 2 + WALL_THICKNESS
base_top_z = OUTER_HEIGHT / 2 - LID_THICKNESS
panel_height = base_top_z - floor_inner_z
panel_z_center = (floor_inner_z + base_top_z) / 2
plus_x_tab_x = OUTER_LENGTH / 2 - WALL_THICKNESS
minus_x_tab_x = -OUTER_LENGTH / 2 + WALL_THICKNESS

base = add_snap_tab_holes(base, plus_x_tab_x, floor_inner_z, panel_z_center)
base = add_snap_tab_holes(base, minus_x_tab_x, floor_inner_z, panel_z_center)

# +X pluggable audio panel with 4 audio jack holes.
jack_center_z = -OUTER_HEIGHT / 2 + AUDIO_JACK_CENTER_HEIGHT_FROM_BOTTOM + BOTTOM_OFFSET
jack_positions = [
    (
        -OUTER_WIDTH / 2
        + FIRST_AUDIO_JACK_CENTER_FROM_LEFT
        + JACKS_DISTANCES_FROM_WALL[i - 1],
        jack_center_z,
    )
    for i in range(4)
]
audio_panel = (cq.Workplane("YZ")
    .workplane(offset=OUTER_LENGTH / 2 - PLUG_PANEL_THICKNESS)
    .center(0, panel_z_center)
    .rect(BOX_WIDTH, panel_height)
    .extrude(PLUG_PANEL_THICKNESS))

# Add audio jack holes to the audio panel
for pos in jack_positions:
    jack_hole = (cq.Workplane("YZ")
        .workplane(offset=OUTER_LENGTH / 2 - PLUG_PANEL_THICKNESS / 2)
        .center(pos[0], pos[1])
        .circle(AUDIO_JACK_DIA / 2)
        .extrude(PLUG_PANEL_THICKNESS + 0.2, both=True))
    audio_panel = audio_panel.cut(jack_hole)

# Add snap tabs to the audio panel
audio_panel = add_snap_tabs(audio_panel, plus_x_tab_x, floor_inner_z, panel_z_center)

# -X pluggable connector panel with USB, power, and RJ45 cutouts.
power_center_y = -OUTER_HEIGHT / 2 + POWER_JACK_H / 2 + BOTTOM_OFFSET
power_center_z = -OUTER_WIDTH / 2 + POWER_JACK_W / 2 + POWER_FROM_LEFT
usb_center_y = -OUTER_HEIGHT / 2 + USB_CUT_H / 2 + BOTTOM_OFFSET + USB_BOTTOM_OFFSET
usb_center_z = OUTER_WIDTH / 2 - USB_CUT_W / 2 - USB_FROM_RIGHT
rj45_center_y =  -OUTER_HEIGHT / 2 + RJ45_CUT_H / 2 + BOTTOM_OFFSET + RJ_45_BOTTOM_OFFSET
rj45_center_z = OUTER_WIDTH / 2 - RJ45_CUT_W / 2 - RJ45_FROM_RIGHT

connector_panel = (cq.Workplane("YZ")
    .workplane(offset=-OUTER_LENGTH / 2 + PLUG_PANEL_THICKNESS)
    .center(0, panel_z_center)
    .rect(BOX_WIDTH, panel_height)
    .extrude(-PLUG_PANEL_THICKNESS))
minus_x_cut_x = -OUTER_LENGTH / 2 + PLUG_PANEL_THICKNESS / 2
for cut_w, cut_h, cut_y, cut_z in [
    (POWER_JACK_W, POWER_JACK_H, power_center_y, power_center_z),
    (USB_CUT_W, USB_CUT_H, usb_center_y, usb_center_z),
    (RJ45_CUT_W, RJ45_CUT_H, rj45_center_y, rj45_center_z),
]:
    connector_panel = connector_panel.cut(
        cq.Workplane("YZ")
        .workplane(offset=minus_x_cut_x)
        .center(cut_z, cut_y)
        .rect(cut_w, cut_h)
        .extrude(PLUG_PANEL_THICKNESS + 0.2, both=True))
connector_panel = add_snap_tabs(connector_panel, minus_x_tab_x, floor_inner_z, panel_z_center)

# Extra audio jacks on both adjacent Y walls from the 4-jack wall (top view).
extra_audio_jack_center_x = OUTER_LENGTH / 2 - EXTRA_AUDIO_JACK_CENTER_FROM_LEFT
extra_jack_hole = (cq.Workplane("XZ")
                   .center(extra_audio_jack_center_x, jack_center_z)
                   .circle(AUDIO_JACK_DIA/2)
                   .extrude(OUTER_WIDTH + 2 * WALL_THICKNESS, both=True))
base = base.cut(extra_jack_hole)

# base_top_z already defined above for pluggable audio wall
# Two oval slots in the bottom floor for screw-mounting DIN rail clamps (elongated along X)
din_hole_x = DIN_CLAMP_HOLE_SPACING / 2
for x_sign in [-1, 1]:
    din_slot = (cq.Workplane("XY")
        .workplane(offset=-OUTER_HEIGHT / 2)
        .center(x_sign * din_hole_x, 0)
        .slot2D(DIN_CLAMP_HOLE_DIA + DIN_CLAMP_SLOT_ELONGATION, DIN_CLAMP_HOLE_DIA, angle=0)
        .extrude(WALL_THICKNESS + 1.0))
    base = base.cut(din_slot)

# Pry chamfers on opposing Y-walls (front and back) for screwdriver lid removal.
# A 45° bevel on the base wall top edge creates a wedge gap for screwdriver entry.
for y_sign in [-1, 1]:
    pry_slot = (cq.Workplane("XZ")
        .workplane(offset=y_sign * OUTER_WIDTH / 2)
        .center(0, base_top_z - PRY_CHAMFER_DEPTH / 2)
        .rect(PRY_CHAMFER_SPAN, PRY_CHAMFER_DEPTH)
        .extrude(-y_sign * WALL_THICKNESS))
    base = base.cut(pry_slot)


# Create lid (inset design: top plate rests on base walls, skirt fits inside)
lid_clearance = 0.2  # mm per side (0.1mm interference with 0.3mm clip bumps for snap engagement)
skirt_outer_l = BOX_LENGTH - 2 * lid_clearance
skirt_outer_w = BOX_WIDTH - 2 * lid_clearance
skirt_height = LID_HEIGHT - LID_THICKNESS  # skirt below the top plate

# Top plate covers the base opening
top_plate = (cq.Workplane("XY")
    .workplane(offset=LID_HEIGHT / 2 - LID_THICKNESS)
    .rect(OUTER_LENGTH, OUTER_WIDTH)
    .extrude(LID_THICKNESS))
top_plate = top_plate.edges("|Z").fillet(EXT_FILLET_R)  # match base outer corner radii

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

CLIP_CHAMFER_HEIGHT = 0.8  # mm, lead-in taper on insertion side of bump

for x_sign in [-1, 1]:
    skirt_face_x = x_sign * skirt_outer_l / 2
    for y_pos in CLIP_Y_POSITIONS:
        bump = (cq.Workplane("YZ")
            .workplane(offset=skirt_face_x)
            .center(y_pos, bump_center_z)
            .rect(CLIP_BUMP_WIDTH, CLIP_BUMP_HEIGHT)
            .extrude(x_sign * CLIP_BUMP_DEPTH))
        # Lead-in chamfer: triangular cut on top of bump for smooth insertion
        chamfer_cut = (cq.Workplane("YZ")
            .workplane(offset=skirt_face_x)
            .center(y_pos - CLIP_BUMP_WIDTH/2, bump_center_z + CLIP_BUMP_HEIGHT/2 - CLIP_CHAMFER_HEIGHT)
            .lineTo(CLIP_BUMP_WIDTH, 0)
            .lineTo(CLIP_BUMP_WIDTH, CLIP_CHAMFER_HEIGHT)
            .close()
            .extrude(x_sign * CLIP_BUMP_DEPTH))
        box_lid = box_lid.union(bump).cut(chamfer_cut)

# Snap-fit clip bumps on skirt outer Y-faces
for y_sign in [-1, 1]:
    skirt_face_y = y_sign * skirt_outer_w / 2
    for x_pos in CLIP_X_POSITIONS:
        bump = (cq.Workplane("XZ")
            .workplane(offset=skirt_face_y)
            .center(x_pos, bump_center_z)
            .rect(CLIP_BUMP_WIDTH, CLIP_BUMP_HEIGHT)
            .extrude(y_sign * CLIP_BUMP_DEPTH))
        # Lead-in chamfer: triangular cut on top of bump for smooth insertion
        chamfer_cut = (cq.Workplane("XZ")
            .workplane(offset=skirt_face_y)
            .center(x_pos - CLIP_BUMP_WIDTH/2, bump_center_z + CLIP_BUMP_HEIGHT/2 - CLIP_CHAMFER_HEIGHT)
            .lineTo(CLIP_BUMP_WIDTH, 0)
            .lineTo(CLIP_BUMP_WIDTH, CLIP_CHAMFER_HEIGHT)
            .close()
            .extrude(y_sign * CLIP_BUMP_DEPTH))
        box_lid = box_lid.union(bump).cut(chamfer_cut)

# Add LCD cutout to lid
box_lid = (box_lid.faces(">Z")
       .workplane()
       .center(LCD_OFFSET[0] + LCD_CUTOUT[0]/2 - BOX_LENGTH/2,
               LCD_OFFSET[1] + LCD_CUTOUT[1]/2 - BOX_WIDTH/2)
       .rect(LCD_CUTOUT[0], LCD_CUTOUT[1])
       .cutThruAll())

# Fillet lid top edges before living hinge cuts (thin tab geometry breaks fillet kernel)
box_lid = box_lid.edges(">Z").fillet(LID_FILLET_R * 0.6)  # ~0.9mm; larger fails on complex geometry

# Living hinge press tab on lid, to the right of the LCD (replaces panel-mount button hole)
lcd_center_x = LCD_OFFSET[0] + LCD_CUTOUT[0]/2 - BOX_LENGTH/2
lcd_center_y = LCD_OFFSET[1] + LCD_CUTOUT[1]/2 - BOX_WIDTH/2
lcd_right_x = lcd_center_x + LCD_CUTOUT[0] / 2

hinge_left_x = lcd_right_x + TAB_GAP_FROM_LCD
hinge_center_x = hinge_left_x + LIVING_HINGE_WIDTH / 2 + TAB_LENGTH + SLOT_CLEARANCE
tab_left_x = hinge_left_x + LIVING_HINGE_WIDTH + SLOT_CLEARANCE
tab_right_x = tab_left_x + TAB_LENGTH
tab_center_x = (tab_left_x + tab_right_x) / 2
tab_center_y = lcd_center_y

hinge_cut_depth = LID_THICKNESS - LIVING_HINGE_THICKNESS
slot_span_y = TAB_WIDTH + 2 * SLOT_CLEARANCE
top_plate_top_z = LID_HEIGHT / 2

# Thin the hinge strip so only a flexible bridge connects tab to lid
hinge_thin = (cq.Workplane("XY")
    .workplane(offset=top_plate_top_z)
    .center(hinge_center_x, tab_center_y)
    .rect(LIVING_HINGE_WIDTH, slot_span_y)
    .extrude(-hinge_cut_depth))
box_lid = box_lid.cut(hinge_thin)

# U-slot through-cuts free the tab on three sides (hinge remains on -X / LCD side)
right_slot = (cq.Workplane("XY")
    .workplane(offset=top_plate_top_z)
    .center(hinge_left_x + TAB_GAP_FROM_LCD, tab_center_y)
    .rect(SLOT_CLEARANCE, slot_span_y)
    .extrude(-(LID_THICKNESS + 0.1)))
box_lid = box_lid.cut(right_slot)

top_slot = (cq.Workplane("XY")
    .workplane(offset=top_plate_top_z)
    .center(tab_center_x, tab_center_y + TAB_WIDTH / 2 + SLOT_CLEARANCE / 2)
    .rect(TAB_LENGTH + SLOT_CLEARANCE, SLOT_CLEARANCE)
    .extrude(-(LID_THICKNESS + 0.1)))
box_lid = box_lid.cut(top_slot)

bottom_slot = (cq.Workplane("XY")
    .workplane(offset=top_plate_top_z)
    .center(tab_center_x, tab_center_y - TAB_WIDTH / 2 - SLOT_CLEARANCE / 2)
    .rect(TAB_LENGTH + SLOT_CLEARANCE, SLOT_CLEARANCE)
    .extrude(-(LID_THICKNESS + 0.1)))
box_lid = box_lid.cut(bottom_slot)

# 6x6x5 mm DIP tactile switch holder on FIXED skirt bridge (not the flex tab).
# The living hinge tab floats above; pressing it deflects down onto the stationary switch.
inner_face_z = LID_HEIGHT / 2 - LID_THICKNESS
skirt_inner_half_w = skirt_outer_w / 2 - WALL_THICKNESS

switch_cavity_size = SWITCH_BODY_W + 2 * WALL_THICKNESS
switch_top_z = inner_face_z - SWITCH_PLUNGER_GAP
switch_bottom_z = switch_top_z - SWITCH_BODY_H
switch_floor_z = switch_bottom_z - SWITCH_SUPPORT_FLOOR

# Bridge spans between fixed skirt Y-walls so the holder cannot move with the flex tab
switch_bridge = (cq.Workplane("XY")
    .workplane(offset=switch_floor_z)
    .center(tab_center_x, tab_center_y)
    .rect(switch_cavity_size + 2, switch_cavity_size + 2)  # extra 2mm to ensure bridge is solidly attached to skirt walls
    .extrude(SWITCH_SUPPORT_FLOOR))
box_lid = box_lid.union(switch_bridge)

# Cup walls rise from the bridge floor under the tab (independent of flex tab sheet)
switch_wall_base_z = switch_floor_z + SWITCH_SUPPORT_FLOOR
for dx, dy, wall_w, wall_h in [
    (0, switch_cavity_size / 2 + SWITCH_HOLDER_WALL / 2,
     switch_cavity_size, SWITCH_HOLDER_WALL),
    (0, -(switch_cavity_size / 2 + SWITCH_HOLDER_WALL / 2),
     switch_cavity_size, SWITCH_HOLDER_WALL),
]:
    wall = (cq.Workplane("XY")
        .workplane(offset=switch_wall_base_z)
        .center(tab_center_x + dx, tab_center_y + dy)
        .rect(wall_w, wall_h)
        .extrude(SWITCH_BODY_H))
    box_lid = box_lid.union(wall)

switch_cavity = (cq.Workplane("XY")
    .workplane(offset=switch_top_z)
    .center(tab_center_x, tab_center_y)
    .rect(switch_cavity_size, switch_cavity_size)
    .extrude(-(SWITCH_BODY_H + 0.1)))
box_lid = box_lid.cut(switch_cavity)


# LCD holder clips on lid inner side (4x, one per wall, to retain LCD PCB edges).
x_clip_center = LCD_MODULE_OUTER_W / 2 - LCD_CLIP_EDGE_INSET
y_clip_center = LCD_MODULE_OUTER_H / 2 - LCD_CLIP_EDGE_INSET

# for x_sign in [-1, 1]:
for x_sign in [-1]:
    clip = (cq.Workplane("XY")
        .workplane(offset=inner_face_z)
        .center(x_sign * x_clip_center, 0)
        .rect(LCD_CLIP_THICKNESS, LCD_CLIP_SPAN)
        .extrude(-LCD_CLIP_DEPTH))
    box_lid = box_lid.union(clip)

for y_sign in [-1, 1]:
    clip = (cq.Workplane("XY")
        .workplane(offset=inner_face_z)
        .center(0, y_sign * y_clip_center)
        .rect(LCD_CLIP_SPAN, LCD_CLIP_THICKNESS)
        .extrude(-LCD_CLIP_DEPTH))
    box_lid = box_lid.union(clip)

# Add snap-fit retention lips at the free end of clips (away from top wall).
lip_span = (LCD_CLIP_SPAN - 2 * LCD_CLIP_GROOVE_MARGIN) - 1.0
lip_center_z = inner_face_z - LCD_CLIP_DEPTH + LCD_CLIP_SNAP_LIP_Z_OFFSET

# for x_sign in [-1, 1]:
for x_sign in [-1]:
    inward_face_x = x_sign * (x_clip_center - LCD_CLIP_THICKNESS / 2)
    lip = (cq.Workplane("YZ")
        .workplane(offset=inward_face_x)
        .center(0, lip_center_z)
        .rect(lip_span, LCD_CLIP_SNAP_LIP_HEIGHT)
        .extrude(-x_sign * LCD_CLIP_SNAP_LIP))
    box_lid = box_lid.union(lip)

for y_sign in [-1, 1]:
    inward_face_y = y_sign * (y_clip_center - LCD_CLIP_THICKNESS / 2)
    lip = (cq.Workplane("XZ")
        .workplane(offset=inward_face_y)
        .center(0, lip_center_z)
        .rect(lip_span, LCD_CLIP_SNAP_LIP_HEIGHT)
        .extrude(-y_sign * LCD_CLIP_SNAP_LIP))
    box_lid = box_lid.union(lip)

def preview_enclosure(base, lid, audio_panel, connector_panel, export_file=False):
    """Export the enclosure model (base, lid, and pluggable end panels) to STEP and STL files."""
    if export_file:
        cq.exporters.export(base, 'output/lcd_arduino_enclosure_base.stl', 'STL')
        cq.exporters.export(lid, 'output/lcd_arduino_enclosure_lid.stl', 'STL')
        cq.exporters.export(audio_panel, 'output/lcd_arduino_enclosure_audio_panel.stl', 'STL')
        cq.exporters.export(connector_panel, 'output/lcd_arduino_enclosure_connector_panel.stl', 'STL')
        print("Exported base, lid, audio_panel, and connector_panel STL files")

        # Assembled view: lid positioned on base for fit check
        lid_z_offset = (OUTER_HEIGHT / 2 - LID_THICKNESS) - (LID_HEIGHT / 2 - LID_THICKNESS)
        assembly = cq.Assembly()
        assembly.add(base, name="base", color=cq.Color("gray"))
        assembly.add(lid, name="lid", loc=cq.Location((0, 0, lid_z_offset)), color=cq.Color("steelblue"))
        assembly.add(audio_panel, name="audio_panel", color=cq.Color("orange"))
        assembly.add(connector_panel, name="connector_panel", color=cq.Color("green"))
        assembly.toCompound().exportStep('output/lcd_arduino_enclosure_assembled.step')
        print("Exported 'lcd_arduino_enclosure_assembled.step' (lid + panels on base)")

# Export models
preview_enclosure(base, box_lid, audio_panel, connector_panel, export_file=True)
