import unittest
from pathlib import Path

import cadquery as cq


OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"
BASE_STEP_PATH = OUTPUT_DIR / "lcd_arduino_enclosure_base.step"

# Arduino Mega hat footprint dimensions from measurements and reference PNG (mm)
HAT_HEIGHT = 20  # mm
WALL_THICKNESS = 2.5
BOARD_RAW_LENGTH = 102.7
BOARD_RAW_WIDTH = 54.5
DIN_GUIDE_HEIGHT = 10

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

MOUNT_BOSS_DIA = 3.8
MOUNT_BOSS_HEIGHT = 3
MOUNT_BOSS_PILOT_DIA = 2.4

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


def _load_shape():
    shape = cq.importers.importStep(str(BASE_STEP_PATH))
    if hasattr(shape, "val"):
        return shape.val()
    return shape


def _shell_floor_bottom_z(bbox):
    # Enclosure shell height (without DIN rail): cavity + floor thickness
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
        din_extension = floor_bottom_z - bbox.zmin

        self.assertAlmostEqual(inner_length, BOX_LENGTH, delta=0.2)
        self.assertAlmostEqual(inner_width, BOX_WIDTH, delta=0.2)
        self.assertAlmostEqual(inner_height, BOX_HEIGHT, delta=0.2)
        self.assertAlmostEqual(din_extension, DIN_GUIDE_HEIGHT, delta=0.2)

        self.assertLessEqual(BOX_LENGTH, inner_length)
        self.assertLessEqual(BOX_WIDTH, inner_width)

        self.assertLessEqual(USB_FROM_RIGHT + USB_CUT_W / 2, inner_width)
        self.assertLessEqual(POWER_FROM_LEFT + POWER_JACK_DIA / 2, inner_width)
        self.assertLessEqual(
            BOTTOM_OFFSET + USB_CUT_H + RJ45_GAP + RJ45_CUT_H,
            inner_height,
        )

        last_audio_center = (
            FIRST_AUDIO_JACK_CENTER_FROM_LEFT
            + (NUMBER_OF_AUDIO_JACKS - 1) * AUDIO_JACK_SPACING_CENTER_TO_CENTER
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

        # Point inside a side wall must be solid.
        wall_point = cq.Vector(
            bbox.xmax - WALL_THICKNESS / 2, 0,
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
            inner_length, BOX_LENGTH,
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

    def test_side_wall_has_usb_power_and_rj45_holes(self):
        """USB, power, and RJ45 cutouts must all be on the same side wall."""
        self.assertTrue(BASE_STEP_PATH.exists(), f"Missing STEP file: {BASE_STEP_PATH}")

        shape = _load_shape()
        bbox = shape.BoundingBox()
        floor_bottom_z = _shell_floor_bottom_z(bbox)

        wall_x = bbox.xmin + WALL_THICKNESS / 2
        opposite_wall_x = bbox.xmax - WALL_THICKNESS / 2

        usb_center_y = bbox.ymax - USB_FROM_RIGHT - USB_CUT_W / 2
        usb_center_z = floor_bottom_z + BOTTOM_OFFSET + USB_CUT_H / 2

        rj45_center_y = usb_center_y
        rj45_center_z = usb_center_z + USB_CUT_H / 2 + RJ45_GAP + RJ45_CUT_H / 2

        power_center_y = bbox.ymin + POWER_FROM_LEFT + POWER_JACK_DIA / 2
        power_center_z = floor_bottom_z + BOTTOM_OFFSET + POWER_JACK_DIA / 2

        # RJ45 should sit above USB on the same wall.
        self.assertGreater(
            rj45_center_z, usb_center_z,
            "RJ45 should be above the USB cutout (upper-left)",
        )

        connectors = [
            ("USB", usb_center_y, usb_center_z, USB_CUT_W / 2, USB_CUT_H / 2),
            ("RJ45", rj45_center_y, rj45_center_z, RJ45_CUT_W / 2, RJ45_CUT_H / 2),
            ("Power", power_center_y, power_center_z, POWER_JACK_DIA / 2, POWER_JACK_DIA / 2),
        ]

        for name, center_y, center_z, half_w, half_h in connectors:
            centre_pt = cq.Vector(wall_x, center_y, center_z)
            self.assertFalse(
                shape.isInside(centre_pt),
                f"{name} cutout centre {centre_pt.toTuple()} should be open (air)",
            )

            wrong_wall_pt = cq.Vector(opposite_wall_x, center_y, center_z)
            self.assertTrue(
                shape.isInside(wrong_wall_pt),
                f"{name} should NOT be cut on opposite wall at {wrong_wall_pt.toTuple()}",
            )

            probe_points = [
                cq.Vector(wall_x, center_y + half_w + 1.5, center_z),
                cq.Vector(wall_x, center_y - half_w - 1.5, center_z),
                cq.Vector(wall_x, center_y, center_z + half_h + 1.5),
                cq.Vector(wall_x, center_y, center_z - half_h - 1.5),
            ]
            self.assertTrue(
                any(shape.isInside(pt) for pt in probe_points),
                f"No side-wall material found around {name} cutout",
            )

    def test_opposite_side_wall_has_4_audio_jack_holes(self):
        """Wall opposite wall_x must have 4 audio-jack through-holes."""
        self.assertTrue(BASE_STEP_PATH.exists(), f"Missing STEP file: {BASE_STEP_PATH}")

        shape = _load_shape()
        bbox = shape.BoundingBox()
        floor_bottom_z = _shell_floor_bottom_z(bbox)

        opposite_wall_x = bbox.xmax - WALL_THICKNESS / 2

        # Jack centres are specified from the left edge with fixed spacing.
        jack_radius = AUDIO_JACK_DIA / 2
        jack_centres_y = [
            bbox.ymin + FIRST_AUDIO_JACK_CENTER_FROM_LEFT
            + index * AUDIO_JACK_SPACING_CENTER_TO_CENTER
            for index in range(NUMBER_OF_AUDIO_JACKS)
        ]
        jack_center_z = floor_bottom_z + AUDIO_JACK_CENTER_HEIGHT_FROM_BOTTOM + BOTTOM_OFFSET

        for index, center_y in enumerate(jack_centres_y, start=1):
            centre_pt = cq.Vector(opposite_wall_x, center_y, jack_center_z)
            self.assertFalse(
                shape.isInside(centre_pt),
                f"Audio jack {index} centre {centre_pt.toTuple()} should be open",
            )

            surround_pts = [
                cq.Vector(opposite_wall_x, center_y + jack_radius + 1.2, jack_center_z),
                cq.Vector(opposite_wall_x, center_y - jack_radius - 1.2, jack_center_z),
                cq.Vector(opposite_wall_x, center_y, jack_center_z + jack_radius + 1.2),
                cq.Vector(opposite_wall_x, center_y, jack_center_z - jack_radius - 1.2),
            ]
            self.assertTrue(
                any(shape.isInside(pt) for pt in surround_pts),
                f"No wall material around audio jack {index}",
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


if __name__ == "__main__":
    unittest.main()
