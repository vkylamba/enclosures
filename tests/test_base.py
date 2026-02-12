import unittest
from pathlib import Path

import cadquery as cq


OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"
BASE_STEP_PATH = OUTPUT_DIR / "lcd_arduino_enclosure_base.step"

# Approx Arduino Mega footprint based on mounting-hole span with small margins.
MEGA_MOUNT_SPAN_X = 97 - 5
MEGA_MOUNT_SPAN_Y = 48 - 5
BOARD_MARGIN = 2  # mm per side
BOARD_LENGTH = MEGA_MOUNT_SPAN_X + 2 * BOARD_MARGIN
BOARD_WIDTH = MEGA_MOUNT_SPAN_Y + 2 * BOARD_MARGIN
HAT_HEIGHT = 20  # mm
WALL_THICKNESS_GUESS = 2.5

# Arduino Mega mounting hole positions (from case.py) and diameter
MEGA_MOUNTS = [(5, 5), (5, 48), (97, 5), (97, 48), (5, 26), (97, 26)]
MOUNT_DIA = 3
BOX_LENGTH = 103
BOX_WIDTH = 54


def _load_shape():
    shape = cq.importers.importStep(str(BASE_STEP_PATH))
    if hasattr(shape, "val"):
        return shape.val()
    return shape


class TestBaseEnclosure(unittest.TestCase):
    def test_base_is_hollow(self):
        """Verify the base is a hollow shell, not a solid block."""
        self.assertTrue(BASE_STEP_PATH.exists(), f"Missing STEP file: {BASE_STEP_PATH}")

        shape = _load_shape()
        bbox = shape.BoundingBox()

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
        cavity_point = cq.Vector(0, 0, bbox.zmin + WALL_THICKNESS_GUESS + 5)
        self.assertFalse(
            shape.isInside(cavity_point),
            f"Point {cavity_point.toTuple()} should be hollow cavity, not solid",
        )

        # Point inside a side wall must be solid.
        wall_point = cq.Vector(
            bbox.xmax - WALL_THICKNESS_GUESS / 2, 0,
            bbox.zmin + WALL_THICKNESS_GUESS / 2,
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

        inner_length = bbox.xlen - 2 * WALL_THICKNESS_GUESS
        inner_width = bbox.ylen - 2 * WALL_THICKNESS_GUESS
        inner_height = bbox.zlen - WALL_THICKNESS_GUESS  # floor only, open top

        self.assertGreaterEqual(
            inner_length, BOARD_LENGTH,
            f"Inner length {inner_length:.1f} mm < board {BOARD_LENGTH} mm",
        )
        self.assertGreaterEqual(
            inner_width, BOARD_WIDTH,
            f"Inner width {inner_width:.1f} mm < board {BOARD_WIDTH} mm",
        )
        self.assertGreaterEqual(
            inner_height, HAT_HEIGHT,
            f"Inner height {inner_height:.1f} mm < hat {HAT_HEIGHT} mm",
        )

        # Verify the board footprint fits by checking that corner points
        # inside the cavity (at board level) are NOT solid.
        board_z = bbox.zmin + WALL_THICKNESS_GUESS + 1  # just above floor
        half_l = BOARD_LENGTH / 2
        half_w = BOARD_WIDTH / 2
        for x, y in [(half_l, half_w), (-half_l, half_w),
                      (half_l, -half_w), (-half_l, -half_w)]:
            pt = cq.Vector(x, y, board_z)
            self.assertFalse(
                shape.isInside(pt),
                f"Board corner {pt.toTuple()} should be inside cavity, not wall",
            )

    def test_base_has_mounting_holes(self):
        """Base floor must have through-holes at each Arduino Mega mount position."""
        self.assertTrue(BASE_STEP_PATH.exists(), f"Missing STEP file: {BASE_STEP_PATH}")

        shape = _load_shape()
        bbox = shape.BoundingBox()

        floor_mid_z = bbox.zmin + WALL_THICKNESS_GUESS / 2  # mid-floor height

        for mx, my in MEGA_MOUNTS:
            # Convert from board-origin coords to centred CadQuery coords
            cx = mx - BOX_LENGTH / 2
            cy = my - BOX_WIDTH / 2

            # Centre of mounting hole should be air (drilled through)
            hole_pt = cq.Vector(cx, cy, floor_mid_z)
            self.assertFalse(
                shape.isInside(hole_pt),
                f"Mount hole centre ({mx},{my}) at {hole_pt.toTuple()} "
                "should be drilled through, but is solid",
            )

            # A point offset from the hole by more than its radius should be
            # solid floor (confirms material exists around the hole).
            offset = MOUNT_DIA / 2 + 1.5  # 1.5 mm outside hole edge
            floor_pt = cq.Vector(cx + offset, cy + offset, floor_mid_z)
            self.assertTrue(
                shape.isInside(floor_pt),
                f"Floor near mount ({mx},{my}) at {floor_pt.toTuple()} "
                "should be solid material",
            )


if __name__ == "__main__":
    unittest.main()
