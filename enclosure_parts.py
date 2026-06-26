from __future__ import annotations

from pathlib import Path

import cadquery as cq


OUTPUT_DIR = Path("output")

# Arduino Mega board and enclosure dimensions (mm)
WALL_THICKNESS = 2.5
BOARD_RAW_LENGTH = 105.0
BOARD_RAW_WIDTH = 55.5
BOX_LENGTH = BOARD_RAW_LENGTH + 1.5
BOX_WIDTH = BOARD_RAW_WIDTH + 1.5
BOX_HEIGHT = 50

MEGA_MOUNTS = [
    (14.75, 3.25),
    (16.05, 51.55),
    (65.55, 8.35),
    (65.55, 36.25),
    (93.75, 3.25),
    (89.65, 48.95),
]

MOUNT_BOSS_DIA = 5.0
MOUNT_BOSS_HEIGHT = 3.0
MOUNT_BOSS_PILOT_DIA = 2.4

# Side-wall connector specs (mm)
USB_CUT_W = 15
USB_CUT_H = 8
RJ45_CUT_W = 15
RJ45_CUT_H = 15
POWER_JACK_W = 10
POWER_JACK_H = 15

USB_FROM_RIGHT = 13.5
POWER_FROM_LEFT = 8

BOTTOM_OFFSET = 4
AUDIO_JACK_CENTER_HEIGHT_FROM_BOTTOM = 5.5
RJ45_GAP = 0

AUDIO_JACK_DIA = 6
FIRST_AUDIO_JACK_CENTER_FROM_LEFT = 8
AUDIO_JACK_SPACING_1_TO_2 = 12.8
AUDIO_JACK_SPACING_2_TO_3 = 16.4
AUDIO_JACK_SPACING_3_TO_4 = 12.8
NUMBER_OF_AUDIO_JACKS = 4
EXTRA_AUDIO_JACK_CENTER_FROM_LEFT = 26.5

JACKS_DISTANCES_FROM_WALL = [
    0,
    AUDIO_JACK_SPACING_1_TO_2,
    AUDIO_JACK_SPACING_1_TO_2 + AUDIO_JACK_SPACING_2_TO_3,
    AUDIO_JACK_SPACING_1_TO_2 + AUDIO_JACK_SPACING_2_TO_3 + AUDIO_JACK_SPACING_3_TO_4,
]

PLUG_PANEL_CLEARANCE = 0.2
PLUG_PANEL_THICKNESS = WALL_THICKNESS
PLUG_SNAP_TAB_SPAN = WALL_THICKNESS
PLUG_SNAP_TAB_THICK = 3 * WALL_THICKNESS

DIN_CLAMP_HOLE_DIA = 4.2
DIN_CLAMP_SLOT_ELONGATION = 4.0
DIN_CLAMP_HOLE_SPACING = 70.0

EXT_FILLET_R = 2.0
LID_FILLET_R = 1.5

OUTER_LENGTH = BOX_LENGTH + 2 * WALL_THICKNESS
OUTER_WIDTH = BOX_WIDTH + 2 * WALL_THICKNESS
OUTER_HEIGHT = BOX_HEIGHT + 2 * WALL_THICKNESS

LCD_CUTOUT = (66, 16)
LCD_OFFSET = ((BOX_LENGTH - LCD_CUTOUT[0]) / 2, (BOX_WIDTH - LCD_CUTOUT[1]) / 2)
LID_HEIGHT = BOX_HEIGHT / 5
LID_THICKNESS = WALL_THICKNESS

LIVING_HINGE_THICKNESS = 0.5
LIVING_HINGE_WIDTH = 3.0
TAB_LENGTH = 10.0
TAB_WIDTH = 8.0
TAB_GAP_FROM_LCD = 3.0
SLOT_CLEARANCE = 0.6

SWITCH_BODY_W = 6.0
SWITCH_BODY_H = 5.0
SWITCH_CLEARANCE = 0.15
SWITCH_HOLDER_WALL = 1.0
SWITCH_HOLDER_LIP = 0.45
SWITCH_HOLDER_LIP_HEIGHT = 0.8
SWITCH_PLUNGER_GAP = 0.4
SWITCH_SUPPORT_FLOOR = 1.0

LCD_MODULE_OUTER_W = 80.0
LCD_MODULE_OUTER_H = 35.7
LCD_MODULE_HEIGHT = 8.5
LCD_CLIP_EDGE_INSET = 1.5
LCD_CLIP_SPAN = 8.0
LCD_CLIP_THICKNESS = 3.0
LCD_CLIP_HOLD_OVERLAP = 1.0
LCD_CLIP_DEPTH = LCD_MODULE_HEIGHT - LCD_CLIP_HOLD_OVERLAP + 0.3
LCD_PCB_THICKNESS = 1.6
LCD_CLIP_GROOVE_MARGIN = 0.6
LCD_CLIP_SNAP_LIP = 0.7
LCD_CLIP_SNAP_LIP_HEIGHT = 1.0
LCD_CLIP_SNAP_LIP_Z_OFFSET = 1.0

CLIP_BUMP_WIDTH = 5.0
CLIP_BUMP_HEIGHT = 2.0
CLIP_BUMP_DEPTH = 0.3
CLIP_Y_POSITIONS = [0]
CLIP_X_POSITIONS = [0]

PRY_CHAMFER_SPAN = 10.0
PRY_CHAMFER_DEPTH = 1.5


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)


def export_shape(shape, step_filename: str, stl_filename: str | None = None) -> None:
    ensure_output_dir()
    cq.exporters.export(shape, str(OUTPUT_DIR / step_filename))
    if stl_filename is not None:
        cq.exporters.export(shape, str(OUTPUT_DIR / stl_filename), "STL")


def add_snap_tab_holes(base, tab_center_x, floor_inner_z, panel_z_center):
    snap_hole_span = PLUG_SNAP_TAB_SPAN + PLUG_PANEL_CLEARANCE
    snap_hole_thick = PLUG_SNAP_TAB_THICK + PLUG_PANEL_CLEARANCE

    floor_tab_hole = (
        cq.Workplane("XY")
        .workplane(offset=floor_inner_z)
        .center(tab_center_x, 0)
        .rect(snap_hole_span, snap_hole_thick)
        .extrude(-(WALL_THICKNESS + 0.2))
    )
    base = base.cut(floor_tab_hole)

    for y_sign in [-1, 1]:
        y_inner_face = y_sign * BOX_WIDTH / 2
        tab_hole = (
            cq.Workplane("XZ")
            .workplane(offset=y_inner_face)
            .center(tab_center_x, panel_z_center)
            .rect(snap_hole_span, snap_hole_thick)
            .extrude(y_sign * (WALL_THICKNESS + 0.2))
        )
        base = base.cut(tab_hole)
    return base


def add_snap_tabs(panel, tab_center_x, floor_inner_z, panel_z_center):
    panel = panel.union(
        cq.Workplane("XY")
        .workplane(offset=floor_inner_z)
        .center(tab_center_x, 0)
        .rect(WALL_THICKNESS, PLUG_SNAP_TAB_THICK)
        .extrude(-WALL_THICKNESS)
    )

    for y_sign in [-1, 1]:
        y_edge = y_sign * BOX_WIDTH / 2
        side_tab = (
            cq.Workplane("XZ")
            .workplane(offset=y_edge)
            .center(tab_center_x, panel_z_center)
            .rect(PLUG_SNAP_TAB_SPAN, PLUG_SNAP_TAB_THICK)
            .extrude(y_sign * WALL_THICKNESS)
        )
        panel = panel.union(side_tab)
    return panel


def build_base():
    outer = cq.Workplane("XY").box(OUTER_LENGTH, OUTER_WIDTH, OUTER_HEIGHT)
    outer = outer.edges("|Z").fillet(EXT_FILLET_R)
    outer = outer.edges("<Z").fillet(EXT_FILLET_R)
    inner = (
        cq.Workplane("XY")
        .workplane(offset=-OUTER_HEIGHT / 2 + WALL_THICKNESS)
        .rect(OUTER_LENGTH, BOX_WIDTH)
        .extrude(OUTER_HEIGHT - WALL_THICKNESS)
    )
    base = outer.cut(inner)
    base = base.faces(">Z").workplane(-LID_THICKNESS).split(keepBottom=True)

    for x, y in MEGA_MOUNTS:
        base = base.union(
            cq.Workplane("XY")
            .workplane(offset=-OUTER_HEIGHT / 2 + WALL_THICKNESS)
            .pushPoints([(x - BOARD_RAW_LENGTH / 2, y - BOARD_RAW_WIDTH / 2)])
            .circle(MOUNT_BOSS_DIA / 2)
            .extrude(MOUNT_BOSS_HEIGHT)
        )

    for x, y in MEGA_MOUNTS:
        base = base.cut(
            cq.Workplane("XY")
            .workplane(offset=-OUTER_HEIGHT / 2 + WALL_THICKNESS + MOUNT_BOSS_HEIGHT)
            .pushPoints([(x - BOARD_RAW_LENGTH / 2, y - BOARD_RAW_WIDTH / 2)])
            .circle(MOUNT_BOSS_PILOT_DIA / 2)
            .extrude(-MOUNT_BOSS_HEIGHT)
        )

    floor_inner_z = -OUTER_HEIGHT / 2 + WALL_THICKNESS
    base_top_z = OUTER_HEIGHT / 2 - LID_THICKNESS
    panel_height = base_top_z - floor_inner_z
    panel_z_center = (floor_inner_z + base_top_z) / 2
    plus_x_tab_x = OUTER_LENGTH / 2 - WALL_THICKNESS
    minus_x_tab_x = -OUTER_LENGTH / 2 + WALL_THICKNESS

    base = add_snap_tab_holes(base, plus_x_tab_x, floor_inner_z, panel_z_center)
    base = add_snap_tab_holes(base, minus_x_tab_x, floor_inner_z, panel_z_center)

    jack_center_z = -OUTER_HEIGHT / 2 + AUDIO_JACK_CENTER_HEIGHT_FROM_BOTTOM + BOTTOM_OFFSET
    jack_positions = [
        (
            -OUTER_WIDTH / 2 + FIRST_AUDIO_JACK_CENTER_FROM_LEFT + JACKS_DISTANCES_FROM_WALL[i - 1],
            jack_center_z,
        )
        for i in range(4)
    ]
    audio_panel = (
        cq.Workplane("YZ")
        .workplane(offset=OUTER_LENGTH / 2 - PLUG_PANEL_THICKNESS)
        .center(0, panel_z_center)
        .rect(BOX_WIDTH, panel_height)
        .extrude(PLUG_PANEL_THICKNESS)
    )
    for pos in jack_positions:
        jack_hole = (
            cq.Workplane("YZ")
            .workplane(offset=OUTER_LENGTH / 2 - PLUG_PANEL_THICKNESS / 2)
            .center(pos[0], pos[1])
            .circle(AUDIO_JACK_DIA / 2)
            .extrude(PLUG_PANEL_THICKNESS + 0.2, both=True)
        )
        audio_panel = audio_panel.cut(jack_hole)
    audio_panel = add_snap_tabs(audio_panel, plus_x_tab_x, floor_inner_z, panel_z_center)

    power_center_y = -OUTER_HEIGHT / 2 + POWER_JACK_H / 2 + BOTTOM_OFFSET
    power_center_z = -OUTER_WIDTH / 2 + POWER_JACK_W / 2 + POWER_FROM_LEFT
    usb_center_y = -OUTER_HEIGHT / 2 + USB_CUT_H / 2 + BOTTOM_OFFSET
    usb_center_z = OUTER_WIDTH / 2 - USB_CUT_W / 2 - USB_FROM_RIGHT
    rj45_center_y = usb_center_y + USB_CUT_H / 2 + RJ45_GAP + RJ45_CUT_H / 2

    connector_panel = (
        cq.Workplane("YZ")
        .workplane(offset=-OUTER_LENGTH / 2 + PLUG_PANEL_THICKNESS)
        .center(0, panel_z_center)
        .rect(BOX_WIDTH, panel_height)
        .extrude(-PLUG_PANEL_THICKNESS)
    )
    minus_x_cut_x = -OUTER_LENGTH / 2 + PLUG_PANEL_THICKNESS / 2
    for cut_w, cut_h, cut_y, cut_z in [
        (POWER_JACK_W, POWER_JACK_H, power_center_y, power_center_z),
        (USB_CUT_W, USB_CUT_H, usb_center_y, usb_center_z),
        (RJ45_CUT_W, RJ45_CUT_H, rj45_center_y, usb_center_z),
    ]:
        connector_panel = connector_panel.cut(
            cq.Workplane("YZ")
            .workplane(offset=minus_x_cut_x)
            .center(cut_z, cut_y)
            .rect(cut_w, cut_h)
            .extrude(PLUG_PANEL_THICKNESS + 0.2, both=True)
        )
    connector_panel = add_snap_tabs(connector_panel, minus_x_tab_x, floor_inner_z, panel_z_center)

    extra_audio_jack_center_x = OUTER_LENGTH / 2 - EXTRA_AUDIO_JACK_CENTER_FROM_LEFT
    extra_jack_hole = (
        cq.Workplane("XZ")
        .center(extra_audio_jack_center_x, jack_center_z)
        .circle(AUDIO_JACK_DIA / 2)
        .extrude(OUTER_WIDTH + 2 * WALL_THICKNESS, both=True)
    )
    base = base.cut(extra_jack_hole)

    din_hole_x = DIN_CLAMP_HOLE_SPACING / 2
    for x_sign in [-1, 1]:
        din_slot = (
            cq.Workplane("XY")
            .workplane(offset=-OUTER_HEIGHT / 2)
            .center(x_sign * din_hole_x, 0)
            .slot2D(DIN_CLAMP_HOLE_DIA + DIN_CLAMP_SLOT_ELONGATION, DIN_CLAMP_HOLE_DIA, angle=0)
            .extrude(WALL_THICKNESS + 1.0)
        )
        base = base.cut(din_slot)

    for y_sign in [-1, 1]:
        pry_slot = (
            cq.Workplane("XZ")
            .workplane(offset=y_sign * OUTER_WIDTH / 2)
            .center(0, base_top_z - PRY_CHAMFER_DEPTH / 2)
            .rect(PRY_CHAMFER_SPAN, PRY_CHAMFER_DEPTH)
            .extrude(-y_sign * WALL_THICKNESS)
        )
        base = base.cut(pry_slot)

    return base, audio_panel, connector_panel


def build_side_walls():
    _, audio_panel, connector_panel = build_base()
    return audio_panel, connector_panel


def build_lid():
    lid_clearance = 0.2
    skirt_outer_l = BOX_LENGTH - 2 * lid_clearance
    skirt_outer_w = BOX_WIDTH - 2 * lid_clearance
    skirt_height = LID_HEIGHT - LID_THICKNESS

    top_plate = (
        cq.Workplane("XY")
        .workplane(offset=LID_HEIGHT / 2 - LID_THICKNESS)
        .rect(OUTER_LENGTH, OUTER_WIDTH)
        .extrude(LID_THICKNESS)
    )
    top_plate = top_plate.edges("|Z").fillet(EXT_FILLET_R)

    skirt_solid = (
        cq.Workplane("XY")
        .workplane(offset=-LID_HEIGHT / 2)
        .rect(skirt_outer_l, skirt_outer_w)
        .extrude(skirt_height)
    )
    skirt_void = (
        cq.Workplane("XY")
        .workplane(offset=-LID_HEIGHT / 2)
        .rect(skirt_outer_l - 2 * WALL_THICKNESS, skirt_outer_w - 2 * WALL_THICKNESS)
        .extrude(skirt_height)
    )
    box_lid = top_plate.union(skirt_solid.cut(skirt_void))

    bump_center_z = -LID_HEIGHT / 2 + 1.0 + CLIP_BUMP_HEIGHT / 2
    clip_chamfer_height = 0.8

    for x_sign in [-1, 1]:
        skirt_face_x = x_sign * skirt_outer_l / 2
        for y_pos in CLIP_Y_POSITIONS:
            bump = (
                cq.Workplane("YZ")
                .workplane(offset=skirt_face_x)
                .center(y_pos, bump_center_z)
                .rect(CLIP_BUMP_WIDTH, CLIP_BUMP_HEIGHT)
                .extrude(x_sign * CLIP_BUMP_DEPTH)
            )
            chamfer_cut = (
                cq.Workplane("YZ")
                .workplane(offset=skirt_face_x)
                .center(y_pos - CLIP_BUMP_WIDTH / 2, bump_center_z + CLIP_BUMP_HEIGHT / 2 - clip_chamfer_height)
                .lineTo(CLIP_BUMP_WIDTH, 0)
                .lineTo(CLIP_BUMP_WIDTH, clip_chamfer_height)
                .close()
                .extrude(x_sign * CLIP_BUMP_DEPTH)
            )
            box_lid = box_lid.union(bump).cut(chamfer_cut)

    for y_sign in [-1, 1]:
        skirt_face_y = y_sign * skirt_outer_w / 2
        for x_pos in CLIP_X_POSITIONS:
            bump = (
                cq.Workplane("XZ")
                .workplane(offset=skirt_face_y)
                .center(x_pos, bump_center_z)
                .rect(CLIP_BUMP_WIDTH, CLIP_BUMP_HEIGHT)
                .extrude(y_sign * CLIP_BUMP_DEPTH)
            )
            chamfer_cut = (
                cq.Workplane("XZ")
                .workplane(offset=skirt_face_y)
                .center(x_pos - CLIP_BUMP_WIDTH / 2, bump_center_z + CLIP_BUMP_HEIGHT / 2 - clip_chamfer_height)
                .lineTo(CLIP_BUMP_WIDTH, 0)
                .lineTo(CLIP_BUMP_WIDTH, clip_chamfer_height)
                .close()
                .extrude(y_sign * CLIP_BUMP_DEPTH)
            )
            box_lid = box_lid.union(bump).cut(chamfer_cut)

    box_lid = (
        box_lid.faces(">Z")
        .workplane()
        .center(
            LCD_OFFSET[0] + LCD_CUTOUT[0] / 2 - BOX_LENGTH / 2,
            LCD_OFFSET[1] + LCD_CUTOUT[1] / 2 - BOX_WIDTH / 2,
        )
        .rect(LCD_CUTOUT[0], LCD_CUTOUT[1])
        .cutThruAll()
    )
    box_lid = box_lid.edges(">Z").fillet(LID_FILLET_R * 0.6)

    lcd_center_x = LCD_OFFSET[0] + LCD_CUTOUT[0] / 2 - BOX_LENGTH / 2
    lcd_center_y = LCD_OFFSET[1] + LCD_CUTOUT[1] / 2 - BOX_WIDTH / 2
    lcd_right_x = lcd_center_x + LCD_CUTOUT[0] / 2

    hinge_left_x = lcd_right_x + TAB_GAP_FROM_LCD
    hinge_center_x = hinge_left_x + LIVING_HINGE_WIDTH / 2
    tab_left_x = hinge_left_x + LIVING_HINGE_WIDTH + SLOT_CLEARANCE
    tab_right_x = tab_left_x + TAB_LENGTH
    tab_center_x = (tab_left_x + tab_right_x) / 2
    tab_center_y = lcd_center_y

    hinge_cut_depth = LID_THICKNESS - LIVING_HINGE_THICKNESS
    slot_span_y = TAB_WIDTH + 2 * SLOT_CLEARANCE
    top_plate_top_z = LID_HEIGHT / 2

    hinge_thin = (
        cq.Workplane("XY")
        .workplane(offset=top_plate_top_z)
        .center(hinge_center_x, tab_center_y)
        .rect(LIVING_HINGE_WIDTH, slot_span_y)
        .extrude(-hinge_cut_depth)
    )
    box_lid = box_lid.cut(hinge_thin)

    right_slot = (
        cq.Workplane("XY")
        .workplane(offset=top_plate_top_z)
        .center(tab_right_x + SLOT_CLEARANCE / 2, tab_center_y)
        .rect(SLOT_CLEARANCE, slot_span_y)
        .extrude(-(LID_THICKNESS + 0.1))
    )
    box_lid = box_lid.cut(right_slot)

    top_slot = (
        cq.Workplane("XY")
        .workplane(offset=top_plate_top_z)
        .center(tab_center_x, tab_center_y + TAB_WIDTH / 2 + SLOT_CLEARANCE / 2)
        .rect(TAB_LENGTH + SLOT_CLEARANCE, SLOT_CLEARANCE)
        .extrude(-(LID_THICKNESS + 0.1))
    )
    box_lid = box_lid.cut(top_slot)

    bottom_slot = (
        cq.Workplane("XY")
        .workplane(offset=top_plate_top_z)
        .center(tab_center_x, tab_center_y - TAB_WIDTH / 2 - SLOT_CLEARANCE / 2)
        .rect(TAB_LENGTH + SLOT_CLEARANCE, SLOT_CLEARANCE)
        .extrude(-(LID_THICKNESS + 0.1))
    )
    box_lid = box_lid.cut(bottom_slot)

    inner_face_z = LID_HEIGHT / 2 - LID_THICKNESS
    switch_cavity_size = SWITCH_BODY_W + 2 * SWITCH_CLEARANCE
    switch_holder_outer = switch_cavity_size + 2 * SWITCH_HOLDER_WALL
    switch_top_z = inner_face_z - SWITCH_PLUNGER_GAP
    switch_bottom_z = switch_top_z - SWITCH_BODY_H
    switch_floor_z = switch_bottom_z - SWITCH_SUPPORT_FLOOR

    switch_bridge = (
        cq.Workplane("XY")
        .workplane(offset=switch_floor_z)
        .center(tab_center_x, 0)
        .rect(switch_holder_outer + 2, skirt_outer_w - 2 * WALL_THICKNESS)
        .extrude(SWITCH_SUPPORT_FLOOR)
    )
    box_lid = box_lid.union(switch_bridge)

    switch_wall_base_z = switch_floor_z + SWITCH_SUPPORT_FLOOR
    for dx, dy, wall_w, wall_h in [
        (0, switch_cavity_size / 2 + SWITCH_HOLDER_WALL / 2, switch_holder_outer, SWITCH_HOLDER_WALL),
        (0, -(switch_cavity_size / 2 + SWITCH_HOLDER_WALL / 2), switch_holder_outer, SWITCH_HOLDER_WALL),
        (switch_cavity_size / 2 + SWITCH_HOLDER_WALL / 2, 0, SWITCH_HOLDER_WALL, switch_cavity_size + 2 * SWITCH_HOLDER_WALL),
        (-(switch_cavity_size / 2 + SWITCH_HOLDER_WALL / 2), 0, SWITCH_HOLDER_WALL, switch_cavity_size + 2 * SWITCH_HOLDER_WALL),
    ]:
        wall = (
            cq.Workplane("XY")
            .workplane(offset=switch_wall_base_z)
            .center(tab_center_x + dx, tab_center_y + dy)
            .rect(wall_w, wall_h)
            .extrude(SWITCH_BODY_H)
        )
        box_lid = box_lid.union(wall)

    switch_cavity = (
        cq.Workplane("XY")
        .workplane(offset=switch_top_z)
        .center(tab_center_x, tab_center_y)
        .rect(switch_cavity_size, switch_cavity_size)
        .extrude(-(SWITCH_BODY_H + 0.1))
    )
    box_lid = box_lid.cut(switch_cavity)

    switch_lip_span = switch_cavity_size - 0.8
    switch_lip_z = switch_wall_base_z + SWITCH_HOLDER_LIP_HEIGHT
    cavity_half = switch_cavity_size / 2

    for x_sign in [-1, 1]:
        inward_face_x = tab_center_x + x_sign * cavity_half
        lip = (
            cq.Workplane("YZ")
            .workplane(offset=inward_face_x)
            .center(tab_center_y, switch_lip_z)
            .rect(switch_lip_span, SWITCH_HOLDER_LIP_HEIGHT)
            .extrude(-x_sign * SWITCH_HOLDER_LIP)
        )
        box_lid = box_lid.union(lip)

    for y_sign in [-1, 1]:
        inward_face_y = tab_center_y + y_sign * cavity_half
        lip = (
            cq.Workplane("XZ")
            .workplane(offset=inward_face_y)
            .center(tab_center_x, switch_lip_z)
            .rect(switch_lip_span, SWITCH_HOLDER_LIP_HEIGHT)
            .extrude(-y_sign * SWITCH_HOLDER_LIP)
        )
        box_lid = box_lid.union(lip)

    y_clip_center = LCD_MODULE_OUTER_H / 2 - LCD_CLIP_EDGE_INSET
    x_clip_center = LCD_MODULE_OUTER_W / 2 - LCD_CLIP_EDGE_INSET
    for x_sign in [-1, 1]:
        clip = (
            cq.Workplane("XY")
            .workplane(offset=inner_face_z)
            .center(x_sign * x_clip_center, 0)
            .rect(LCD_CLIP_THICKNESS, LCD_CLIP_SPAN)
            .extrude(-LCD_CLIP_DEPTH)
        )
        box_lid = box_lid.union(clip)

    for y_sign in [-1, 1]:
        clip = (
            cq.Workplane("XY")
            .workplane(offset=inner_face_z)
            .center(0, y_sign * y_clip_center)
            .rect(LCD_CLIP_SPAN, LCD_CLIP_THICKNESS)
            .extrude(-LCD_CLIP_DEPTH)
        )
        box_lid = box_lid.union(clip)

    lip_span = (LCD_CLIP_SPAN - 2 * LCD_CLIP_GROOVE_MARGIN) - 1.0
    lip_center_z = inner_face_z - LCD_CLIP_DEPTH + LCD_CLIP_SNAP_LIP_Z_OFFSET

    for x_sign in [-1, 1]:
        inward_face_x = x_sign * (x_clip_center - LCD_CLIP_THICKNESS / 2)
        lip = (
            cq.Workplane("YZ")
            .workplane(offset=inward_face_x)
            .center(0, lip_center_z)
            .rect(lip_span, LCD_CLIP_SNAP_LIP_HEIGHT)
            .extrude(-x_sign * LCD_CLIP_SNAP_LIP)
        )
        box_lid = box_lid.union(lip)

    for y_sign in [-1, 1]:
        inward_face_y = y_sign * (y_clip_center - LCD_CLIP_THICKNESS / 2)
        lip = (
            cq.Workplane("XZ")
            .workplane(offset=inward_face_y)
            .center(0, lip_center_z)
            .rect(lip_span, LCD_CLIP_SNAP_LIP_HEIGHT)
            .extrude(-y_sign * LCD_CLIP_SNAP_LIP)
        )
        box_lid = box_lid.union(lip)

    return box_lid
