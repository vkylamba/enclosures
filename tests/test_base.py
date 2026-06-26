import unittest
from pathlib import Path

import cadquery as cq

from enclosure_parts import (
    AUDIO_JACK_CENTER_HEIGHT_FROM_BOTTOM,
    AUDIO_JACK_DIA,
    AUDIO_JACK_SPACING_1_TO_2,
    AUDIO_JACK_SPACING_2_TO_3,
    AUDIO_JACK_SPACING_3_TO_4,
    BOX_HEIGHT,
    BOX_LENGTH,
    BOX_WIDTH,
    BOARD_RAW_LENGTH,
    BOARD_RAW_WIDTH,
    BOTTOM_OFFSET,
    DIN_CLAMP_HOLE_DIA,
    DIN_CLAMP_HOLE_SPACING,
    EXTRA_AUDIO_JACK_CENTER_FROM_LEFT,
    FIRST_AUDIO_JACK_CENTER_FROM_LEFT,
    JACKS_DISTANCES_FROM_WALL,
    MEGA_MOUNTS,
    MOUNT_BOSS_DIA,
    MOUNT_BOSS_HEIGHT,
    MOUNT_BOSS_PILOT_DIA,
    NUMBER_OF_AUDIO_JACKS,
    OUTPUT_DIR,
    POWER_FROM_LEFT,
    POWER_JACK_H,
    POWER_JACK_W,
    PLUG_PANEL_THICKNESS,
    PLUG_SNAP_TAB_SPAN,
    PLUG_SNAP_TAB_THICK,
    RJ45_CUT_H,
    RJ45_CUT_W,
    RJ45_GAP,
    USB_CUT_H,
    USB_CUT_W,
    USB_FROM_RIGHT,
    WALL_THICKNESS,
)


BASE_STEP_PATH = OUTPUT_DIR / "lcd_arduino_enclosure_base.step"
AUDIO_PANEL_STEP_PATH = OUTPUT_DIR / "lcd_arduino_enclosure_audio_panel.step"
CONNECTOR_PANEL_STEP_PATH = OUTPUT_DIR / "lcd_arduino_enclosure_connector_panel.step"


def _load_shape():
    shape = cq.importers.importStep(str(BASE_STEP_PATH))
    if hasattr(shape, "val"):
        return shape.val()
    return shape


def _shell_floor_bottom_z(bbox):
    # Enclosure shell height: cavity + floor thickness
    return bbox.zmax - (BOX_HEIGHT + WALL_THICKNESS)


class TestBaseEnclosure(unittest.TestCase):
    def test_reference_dimensions_are_inner_based(self):
        """Reference dimensions/offsets must be valid against inner dimensions."""
        self.assertTrue(BASE_STEP_PATH.exists(), f"Missing STEP file: {BASE_STEP_PATH}")

        shape = _load_shape()
        bbox = shape.BoundingBox()

        inner_length = bbox.xlen - 2 * WALL_THICKNESS
        inner_width = bbox.ylen - 2 * WALL_THICKNESS
        floor_bottom_z = _shell_floor_bottom_z(bbox)
        floor_top_z = floor_bottom_z + WALL_THICKNESS
        inner_height = bbox.zmax - floor_top_z
        base_bottom_offset = floor_bottom_z - bbox.zmin

        self.assertAlmostEqual(inner_length, BOX_LENGTH, delta=0.5)
        self.assertAlmostEqual(inner_width, BOX_WIDTH, delta=0.2)
        self.assertAlmostEqual(inner_height, BOX_HEIGHT, delta=0.2)
        self.assertAlmostEqual(base_bottom_offset, 0.0, delta=0.2)

        self.assertLessEqual(BOX_LENGTH, inner_length + 0.2)
        self.assertLessEqual(BOX_WIDTH, inner_width)

        self.assertLessEqual(USB_FROM_RIGHT + USB_CUT_W / 2, inner_width)
        self.assertLessEqual(POWER_FROM_LEFT + POWER_JACK_W / 2, inner_width)
        self.assertLessEqual(
            BOTTOM_OFFSET + USB_CUT_H + RJ45_GAP + RJ45_CUT_H,
            inner_height,
        )

        last_audio_center = (
            FIRST_AUDIO_JACK_CENTER_FROM_LEFT
            + JACKS_DISTANCES_FROM_WALL[-1]
        )
        self.assertLessEqual(last_audio_center, inner_width)
        self.assertLessEqual(EXTRA_AUDIO_JACK_CENTER_FROM_LEFT, inner_length)

    def test_base_is_hollow(self):
        """Verify the base is a hollow shell, not a solid block."""
        self.assertTrue(BASE_STEP_PATH.exists(), f"Missing STEP file: {BASE_STEP_PATH}")

        shape = _load_shape()
        bbox = shape.BoundingBox()
        floor_bottom_z = _shell_floor_bottom_z(bbox)

        # Volume of solid material must be well below the bounding-box volume.
        # Walls + screw bosses + mounting posts can reach ~65%, so cap at 75%.
        outer_volume = bbox.xlen * bbox.ylen * bbox.zlen
        solid_volume = shape.Volume()
        self.assertGreater(solid_volume, 0.0, "Solid volume should be positive")
        ratio = solid_volume / outer_volume
        self.assertLess(
            ratio, 0.75,
            f"Material/bbox ratio {ratio:.2f} too high; enclosure may not be hollow",
        )

        # Point inside the cavity (centre, a few mm above the floor) must be air.
        cavity_point = cq.Vector(0, 0, floor_bottom_z + WALL_THICKNESS + 5)
        self.assertFalse(
            shape.isInside(cavity_point),
            f"Point {cavity_point.toTuple()} should be hollow cavity, not solid",
        )

        # Point inside a Y side wall must be solid (both X ends are open for plug-in panels).
        wall_point = cq.Vector(
            0, bbox.ymax - WALL_THICKNESS / 2,
            floor_bottom_z + WALL_THICKNESS / 2,
        )
        self.assertTrue(
            shape.isInside(wall_point),
            f"Point {wall_point.toTuple()} should be inside wall material",
        )

    def test_base_fits_arduino_mega_with_hat(self):
        """Inner cavity must be large enough for a Mega board + shield hat."""
        self.assertTrue(BASE_STEP_PATH.exists(), f"Missing STEP file: {BASE_STEP_PATH}")

        shape = _load_shape()
        bbox = shape.BoundingBox()
        floor_bottom_z = _shell_floor_bottom_z(bbox)

        inner_length = bbox.xlen - 2 * WALL_THICKNESS
        inner_width = bbox.ylen - 2 * WALL_THICKNESS
        inner_height = bbox.zmax - (floor_bottom_z + WALL_THICKNESS)

        self.assertGreaterEqual(
            inner_length, BOX_LENGTH - 0.2,
            f"Inner length {inner_length:.1f} mm < box {BOX_LENGTH} mm",
        )
        self.assertGreaterEqual(
            inner_width, BOX_WIDTH,
            f"Inner width {inner_width:.1f} mm < box {BOX_WIDTH} mm",
        )
        self.assertGreaterEqual(
            inner_height, BOX_HEIGHT,
            f"Inner height {inner_height:.1f} mm < box {BOX_HEIGHT} mm",
        )

        # Verify the board footprint fits by checking that corner points
        # inside the cavity (at board level) are NOT solid.
        board_z = floor_bottom_z + WALL_THICKNESS + 1  # just above floor
        half_l = BOX_LENGTH / 2 - 1.0
        half_w = BOX_WIDTH / 2 - 1.0
        for x, y in [(half_l, half_w), (-half_l, half_w),
                      (half_l, -half_w), (-half_l, -half_w)]:
            pt = cq.Vector(x, y, board_z)
            self.assertFalse(
                shape.isInside(pt),
                f"Board corner {pt.toTuple()} should be inside cavity, not wall",
            )

    def test_base_has_mounting_bosses(self):
        """Base floor must have screwable mounting bosses per the board drawing pattern."""
        self.assertTrue(BASE_STEP_PATH.exists(), f"Missing STEP file: {BASE_STEP_PATH}")

        shape = _load_shape()
        bbox = shape.BoundingBox()
        floor_bottom_z = _shell_floor_bottom_z(bbox)
        boss_mid_z = floor_bottom_z + WALL_THICKNESS + MOUNT_BOSS_HEIGHT / 2

        for mx, my in MEGA_MOUNTS:
            # Convert drawing coords (origin board bottom-left) to centered model XY.
            cx = mx - BOARD_RAW_LENGTH / 2
            cy = my - BOARD_RAW_WIDTH / 2

            # Centre should be pilot-hole air for screw entry.
            boss_pt = cq.Vector(cx, cy, boss_mid_z)
            self.assertFalse(
                shape.isInside(boss_pt),
                f"Mount boss centre ({mx},{my}) at {boss_pt.toTuple()} "
                "should be pilot-hole air, but is solid",
            )

            # Ring between pilot and outer diameter should be solid material.
            ring_offset = (MOUNT_BOSS_PILOT_DIA / 2 + MOUNT_BOSS_DIA / 2) / 2
            ring_pts = [
                cq.Vector(cx + ring_offset, cy, boss_mid_z),
                cq.Vector(cx - ring_offset, cy, boss_mid_z),
                cq.Vector(cx, cy + ring_offset, boss_mid_z),
                cq.Vector(cx, cy - ring_offset, boss_mid_z),
            ]
            self.assertTrue(
                all(shape.isInside(pt) for pt in ring_pts),
                f"No solid boss ring found around mount ({mx},{my}); "
                "boss diameter/pilot may be incorrect",
            )

            # Outside boss radius should be cavity air at boss mid-height.
            outer_offset = MOUNT_BOSS_DIA / 2 + 1.2
            outside_pts = [
                cq.Vector(cx + outer_offset, cy, boss_mid_z),
                cq.Vector(cx - outer_offset, cy, boss_mid_z),
                cq.Vector(cx, cy + outer_offset, boss_mid_z),
                cq.Vector(cx, cy - outer_offset, boss_mid_z),
            ]
            self.assertTrue(
                any(not shape.isInside(pt) for pt in outside_pts),
                f"No cavity clearance found outside boss ({mx},{my}); "
                "boss diameter/placement may be incorrect",
            )

    def test_connector_panel_has_usb_power_and_rj45_holes(self):
        """Pluggable -X panel must carry USB, power, and RJ45 cutouts."""
        self.assertTrue(
            CONNECTOR_PANEL_STEP_PATH.exists(),
            f"Missing STEP file: {CONNECTOR_PANEL_STEP_PATH}",
        )

        shape = cq.importers.importStep(str(CONNECTOR_PANEL_STEP_PATH))
        if hasattr(shape, "val"):
            shape = shape.val()
        bbox = shape.BoundingBox()
        base_bbox = _load_shape().BoundingBox()
        floor_bottom_z = _shell_floor_bottom_z(base_bbox)

        panel_wall_x = bbox.xmin + PLUG_PANEL_THICKNESS / 2

        usb_center_y = base_bbox.ymax - USB_FROM_RIGHT - USB_CUT_W / 2
        usb_center_z = floor_bottom_z + BOTTOM_OFFSET + USB_CUT_H / 2
        rj45_center_y = usb_center_y
        rj45_center_z = usb_center_z + USB_CUT_H / 2 + RJ45_GAP + RJ45_CUT_H / 2
        power_center_y = base_bbox.ymin + POWER_FROM_LEFT + POWER_JACK_W / 2
        power_center_z = floor_bottom_z + BOTTOM_OFFSET + POWER_JACK_H / 2

        connectors = [
            ("USB", usb_center_y, usb_center_z, USB_CUT_W / 2, USB_CUT_H / 2),
            ("RJ45", rj45_center_y, rj45_center_z, RJ45_CUT_W / 2, RJ45_CUT_H / 2),
            ("Power", power_center_y, power_center_z, POWER_JACK_W / 2, POWER_JACK_H / 2),
        ]

        for name, center_y, center_z, half_w, half_h in connectors:
            centre_pt = cq.Vector(panel_wall_x, center_y, center_z)
            self.assertFalse(
                shape.isInside(centre_pt),
                f"{name} cutout centre {centre_pt.toTuple()} should be open on connector panel",
            )

            probe_points = [
                cq.Vector(panel_wall_x, center_y + half_w + 1.5, center_z),
                cq.Vector(panel_wall_x, center_y - half_w - 1.5, center_z),
                cq.Vector(panel_wall_x, center_y, center_z + half_h + 1.5),
                cq.Vector(panel_wall_x, center_y, center_z - half_h - 1.5),
            ]
            self.assertTrue(
                any(shape.isInside(pt) for pt in probe_points),
                f"No connector panel material around {name} cutout",
            )

    def test_minus_x_wall_is_open_for_pluggable_connector_panel(self):
        """-X end wall is removed; USB/power/RJ45 live on the separate plug-in panel."""
        self.assertTrue(BASE_STEP_PATH.exists(), f"Missing STEP file: {BASE_STEP_PATH}")

        shape = _load_shape()
        bbox = shape.BoundingBox()
        floor_bottom_z = _shell_floor_bottom_z(bbox)

        minus_x_opening = bbox.xmin + WALL_THICKNESS + 1.5
        usb_center_z = floor_bottom_z + BOTTOM_OFFSET + USB_CUT_H / 2
        centre_pt = cq.Vector(
            minus_x_opening,
            bbox.ymax - USB_FROM_RIGHT - USB_CUT_W / 2,
            usb_center_z,
        )
        self.assertFalse(
            shape.isInside(centre_pt),
            f"-X opening {centre_pt.toTuple()} should be open in base shell",
        )

    def test_plus_x_wall_is_open_for_pluggable_audio_panel(self):
        """+X end wall is removed; audio jacks live on the separate plug-in panel."""
        self.assertTrue(BASE_STEP_PATH.exists(), f"Missing STEP file: {BASE_STEP_PATH}")

        shape = _load_shape()
        bbox = shape.BoundingBox()
        floor_bottom_z = _shell_floor_bottom_z(bbox)

        opposite_wall_x = bbox.xmax - WALL_THICKNESS - 1.5
        jack_center_z = floor_bottom_z + AUDIO_JACK_CENTER_HEIGHT_FROM_BOTTOM + BOTTOM_OFFSET
        centre_pt = cq.Vector(
            opposite_wall_x,
            0,
            jack_center_z,
        )
        self.assertFalse(
            shape.isInside(centre_pt),
            f"+X opening {centre_pt.toTuple()} should be open in base shell",
        )

    def test_audio_panel_has_4_audio_jack_holes(self):
        """Pluggable +X panel must carry the 4 audio-jack through-holes."""
        self.assertTrue(
            AUDIO_PANEL_STEP_PATH.exists(),
            f"Missing STEP file: {AUDIO_PANEL_STEP_PATH}",
        )

        shape = cq.importers.importStep(str(AUDIO_PANEL_STEP_PATH))
        if hasattr(shape, "val"):
            shape = shape.val()
        bbox = shape.BoundingBox()

        base_bbox = _load_shape().BoundingBox()
        floor_bottom_z = _shell_floor_bottom_z(base_bbox)

        panel_wall_x = bbox.xmax - PLUG_PANEL_THICKNESS / 2
        jack_radius = AUDIO_JACK_DIA / 2
        jack_centres_y = [
            base_bbox.ymin + FIRST_AUDIO_JACK_CENTER_FROM_LEFT
            + JACKS_DISTANCES_FROM_WALL[index]
            for index in range(NUMBER_OF_AUDIO_JACKS)
        ]
        jack_center_z = floor_bottom_z + AUDIO_JACK_CENTER_HEIGHT_FROM_BOTTOM + BOTTOM_OFFSET

        for index, center_y in enumerate(jack_centres_y, start=1):
            centre_pt = cq.Vector(panel_wall_x, center_y, jack_center_z)
            self.assertFalse(
                shape.isInside(centre_pt),
                f"Audio panel jack {index} centre {centre_pt.toTuple()} should be open",
            )

            surround_pts = [
                cq.Vector(panel_wall_x, center_y + jack_radius + 1.2, jack_center_z),
                cq.Vector(panel_wall_x, center_y - jack_radius - 1.2, jack_center_z),
                cq.Vector(panel_wall_x, center_y, jack_center_z + jack_radius + 1.2),
                cq.Vector(panel_wall_x, center_y, jack_center_z - jack_radius - 1.2),
            ]
            self.assertTrue(
                any(shape.isInside(pt) for pt in surround_pts),
                f"No panel material around audio jack {index}",
            )

    def test_audio_panel_has_snap_tabs_on_floor_and_sides(self):
        """Panel has square snap tabs on floor and Y edges for base retention holes."""
        self.assertTrue(
            AUDIO_PANEL_STEP_PATH.exists(),
            f"Missing STEP file: {AUDIO_PANEL_STEP_PATH}",
        )

        shape = cq.importers.importStep(str(AUDIO_PANEL_STEP_PATH))
        if hasattr(shape, "val"):
            shape = shape.val()
        panel_bbox = shape.BoundingBox()
        base_bbox = _load_shape().BoundingBox()
        floor_bottom_z = _shell_floor_bottom_z(base_bbox)
        floor_inner_z = floor_bottom_z + WALL_THICKNESS
        panel_z_center = (floor_inner_z + base_bbox.zmax - WALL_THICKNESS) / 2
        panel_center_x = base_bbox.xmax - WALL_THICKNESS

        floor_tab = cq.Vector(
            panel_center_x,
            0,
            floor_inner_z - WALL_THICKNESS / 2,
        )
        self.assertTrue(
            shape.isInside(floor_tab),
            f"Floor snap tab {floor_tab.toTuple()} should be solid",
        )

        side_tab = cq.Vector(
            panel_center_x,
            panel_bbox.ymax - WALL_THICKNESS / 2,
            panel_z_center,
        )
        self.assertTrue(
            shape.isInside(side_tab),
            f"Side snap tab {side_tab.toTuple()} should be solid",
        )

    def test_connector_panel_has_snap_tabs_on_floor_and_sides(self):
        """Connector panel has square snap tabs on floor and Y edges."""
        self.assertTrue(
            CONNECTOR_PANEL_STEP_PATH.exists(),
            f"Missing STEP file: {CONNECTOR_PANEL_STEP_PATH}",
        )

        shape = cq.importers.importStep(str(CONNECTOR_PANEL_STEP_PATH))
        if hasattr(shape, "val"):
            shape = shape.val()
        panel_bbox = shape.BoundingBox()
        base_bbox = _load_shape().BoundingBox()
        floor_bottom_z = _shell_floor_bottom_z(base_bbox)
        floor_inner_z = floor_bottom_z + WALL_THICKNESS
        panel_z_center = (floor_inner_z + base_bbox.zmax - WALL_THICKNESS) / 2
        panel_center_x = base_bbox.xmin + WALL_THICKNESS

        floor_tab = cq.Vector(
            panel_center_x,
            0,
            floor_inner_z - WALL_THICKNESS / 2,
        )
        self.assertTrue(
            shape.isInside(floor_tab),
            f"Connector floor snap tab {floor_tab.toTuple()} should be solid",
        )

        side_tab = cq.Vector(
            panel_center_x,
            panel_bbox.ymax - WALL_THICKNESS / 2,
            panel_z_center,
        )
        self.assertTrue(
            shape.isInside(side_tab),
            f"Connector side snap tab {side_tab.toTuple()} should be solid",
        )

    def test_base_floor_has_panel_tab_holes_at_both_ends(self):
        """Floor must have snap tab holes at both +X and -X panel ends."""
        self.assertTrue(BASE_STEP_PATH.exists(), f"Missing STEP file: {BASE_STEP_PATH}")

        shape = _load_shape()
        bbox = shape.BoundingBox()
        floor_bottom_z = _shell_floor_bottom_z(bbox)
        floor_inner_z = floor_bottom_z + WALL_THICKNESS
        panel_center_x = bbox.xmax - WALL_THICKNESS

        hole_pt = cq.Vector(panel_center_x, 0, floor_inner_z - 0.5)
        self.assertFalse(
            shape.isInside(hole_pt),
            f"+X floor tab hole {hole_pt.toTuple()} should be open",
        )

        minus_x_hole = cq.Vector(bbox.xmin + WALL_THICKNESS, 0, floor_inner_z - 0.5)
        self.assertFalse(
            shape.isInside(minus_x_hole),
            f"-X floor tab hole {minus_x_hole.toTuple()} should be open",
        )

    def test_base_y_walls_have_panel_tab_holes_at_both_ends(self):
        """Y walls must have snap tab holes at both +X and -X panel ends."""
        self.assertTrue(BASE_STEP_PATH.exists(), f"Missing STEP file: {BASE_STEP_PATH}")

        shape = _load_shape()
        bbox = shape.BoundingBox()
        floor_bottom_z = _shell_floor_bottom_z(bbox)
        floor_inner_z = floor_bottom_z + WALL_THICKNESS
        panel_z_center = (floor_inner_z + bbox.zmax - WALL_THICKNESS) / 2
        panel_center_x = bbox.xmax - WALL_THICKNESS

        for y_sign in [-1, 1]:
            plus_x_hole = cq.Vector(
                panel_center_x,
                y_sign * (BOX_WIDTH / 2 + WALL_THICKNESS / 2),
                panel_z_center,
            )
            self.assertFalse(
                shape.isInside(plus_x_hole),
                f"+X Y-wall through-hole {plus_x_hole.toTuple()} should be open",
            )

            minus_x_hole = cq.Vector(
                bbox.xmin + WALL_THICKNESS,
                y_sign * (BOX_WIDTH / 2 + WALL_THICKNESS / 2),
                panel_z_center,
            )
            self.assertFalse(
                shape.isInside(minus_x_hole),
                f"-X Y-wall through-hole {minus_x_hole.toTuple()} should be open",
            )

            outer_pt = cq.Vector(
                panel_center_x,
                y_sign * (bbox.ymax if y_sign > 0 else bbox.ymin) - y_sign * WALL_THICKNESS / 2,
                panel_z_center,
            )
            self.assertFalse(
                shape.isInside(outer_pt),
                f"Y-wall outer face hole {outer_pt.toTuple()} should be open",
            )

    def test_adjacent_walls_have_extra_audio_jack(self):
        """Both adjacent Y walls from the 4-jack wall have the extra audio jack."""
        self.assertTrue(BASE_STEP_PATH.exists(), f"Missing STEP file: {BASE_STEP_PATH}")

        shape = _load_shape()
        bbox = shape.BoundingBox()
        floor_bottom_z = _shell_floor_bottom_z(bbox)

        wall_y_positions = [
            bbox.ymax - WALL_THICKNESS / 2,
            bbox.ymin + WALL_THICKNESS / 2,
        ]
        jack_radius = AUDIO_JACK_DIA / 2
        extra_jack_center_x = bbox.xmax - EXTRA_AUDIO_JACK_CENTER_FROM_LEFT
        extra_jack_center_z = floor_bottom_z + AUDIO_JACK_CENTER_HEIGHT_FROM_BOTTOM + BOTTOM_OFFSET

        for wall_y in wall_y_positions:
            centre_pt = cq.Vector(extra_jack_center_x, wall_y, extra_jack_center_z)
            self.assertFalse(
                shape.isInside(centre_pt),
                f"Extra audio jack centre {centre_pt.toTuple()} should be open",
            )

            surround_pts = [
                cq.Vector(extra_jack_center_x + jack_radius + 1.2, wall_y, extra_jack_center_z),
                cq.Vector(extra_jack_center_x - jack_radius - 1.2, wall_y, extra_jack_center_z),
                cq.Vector(extra_jack_center_x, wall_y, extra_jack_center_z + jack_radius + 1.2),
                cq.Vector(extra_jack_center_x, wall_y, extra_jack_center_z - jack_radius - 1.2),
            ]
            self.assertTrue(
                any(shape.isInside(pt) for pt in surround_pts),
                f"No wall material around extra audio jack at y={wall_y:.2f}",
            )

    def test_bottom_has_two_din_clamp_mounting_holes(self):
        """Bottom floor must include two screw holes for DIN clamp mounting."""
        self.assertTrue(BASE_STEP_PATH.exists(), f"Missing STEP file: {BASE_STEP_PATH}")

        shape = _load_shape()
        bbox = shape.BoundingBox()

        hole_x = DIN_CLAMP_HOLE_SPACING / 2
        floor_mid_z = bbox.zmin + WALL_THICKNESS / 2

        for x in (-hole_x, hole_x):
            center_pt = cq.Vector(x, 0, floor_mid_z)
            self.assertFalse(
                shape.isInside(center_pt),
                f"Bottom clamp hole centre {center_pt.toTuple()} should be open",
            )

            ring_offset = DIN_CLAMP_HOLE_DIA / 2 + 1.2
            ring_pts = [
                cq.Vector(x + ring_offset, 0, floor_mid_z),
                cq.Vector(x - ring_offset, 0, floor_mid_z),
                cq.Vector(x, ring_offset, floor_mid_z),
                cq.Vector(x, -ring_offset, floor_mid_z),
            ]
            self.assertTrue(
                any(shape.isInside(pt) for pt in ring_pts),
                f"No floor material around bottom clamp hole at x={x:.2f}",
            )

        # Ensure these are two separate holes rather than one merged slot.
        midpoint_pt = cq.Vector(0, 0, floor_mid_z)
        self.assertTrue(
            shape.isInside(midpoint_pt),
            f"Point {midpoint_pt.toTuple()} between clamp holes should remain solid",
        )


if __name__ == "__main__":
    unittest.main()
