import unittest
from pathlib import Path

import cadquery as cq


OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"
LID_STEP_PATH = OUTPUT_DIR / "lcd_arduino_enclosure_lid.step"
BASE_STEP_PATH = OUTPUT_DIR / "lcd_arduino_enclosure_base.step"

# Lid dimensions references
INNER_LENGTH_REF = 106.5
INNER_WIDTH_REF = 57
WALL_THICKNESS = 2.5
LID_HEIGHT = 50 / 5  # box_height / 5

# LCD cutout (from case.py)
LCD_CUTOUT_W = 66
LCD_CUTOUT_H = 16
LCD_CENTER_X = 0.0   # centred on lid
LCD_CENTER_Y = 0.0   # centred on lid

# LCD module outer size from Issues.md (clip holder target)
LCD_MODULE_OUTER_W = 80.0
LCD_MODULE_OUTER_H = 35.7
LCD_MODULE_HEIGHT = 8.5

# Push button (from case.py)
PUSH_BUTTON_DIA = 7
# Button is 3mm gap to the right of LCD right edge, centred vertically with LCD
PUSH_BTN_X = LCD_CENTER_X + LCD_CUTOUT_W / 2 + PUSH_BUTTON_DIA / 2 + 3
PUSH_BTN_Y = LCD_CENTER_Y


def _load_shape():
    shape = cq.importers.importStep(str(LID_STEP_PATH))
    if hasattr(shape, "val"):
        return shape.val()
    return shape


class TestLidEnclosure(unittest.TestCase):
    def test_lid_covers_base_walls(self):
        """Cap should cover the base top walls in both X and Y directions."""
        self.assertTrue(LID_STEP_PATH.exists(), f"Missing STEP file: {LID_STEP_PATH}")
        self.assertTrue(BASE_STEP_PATH.exists(), f"Missing STEP file: {BASE_STEP_PATH}")

        lid_shape = _load_shape()
        base_shape = cq.importers.importStep(str(BASE_STEP_PATH))
        if hasattr(base_shape, "val"):
            base_shape = base_shape.val()

        lid_bbox = lid_shape.BoundingBox()
        base_bbox = base_shape.BoundingBox()

        # Cap top should at least span the base outer wall footprint.
        self.assertGreaterEqual(
            lid_bbox.xlen,
            base_bbox.xlen - 0.3,
            f"Lid X coverage too small: lid={lid_bbox.xlen:.2f} mm, "
            f"base={base_bbox.xlen:.2f} mm",
        )
        self.assertGreaterEqual(
            lid_bbox.ylen,
            base_bbox.ylen - 0.3,
            f"Lid Y coverage too small: lid={lid_bbox.ylen:.2f} mm, "
            f"base={base_bbox.ylen:.2f} mm",
        )

    def test_lid_has_lcd_cutout(self):
        """Lid top face must have a rectangular LCD cutout."""
        self.assertTrue(LID_STEP_PATH.exists(), f"Missing STEP file: {LID_STEP_PATH}")

        shape = _load_shape()
        bbox = shape.BoundingBox()

        # Top plate is at the top of the lid; sample its mid-thickness
        plate_z = bbox.zmax - WALL_THICKNESS / 2

        # Centre of LCD cutout should be air (cutThruAll)
        lcd_pt = cq.Vector(LCD_CENTER_X, LCD_CENTER_Y, plate_z)
        self.assertFalse(
            shape.isInside(lcd_pt),
            f"LCD centre {lcd_pt.toTuple()} should be cut out, not solid",
        )

        # Sample points within the LCD rectangle should also be air
        for dx, dy in [
            (LCD_CUTOUT_W / 2 - 2, 0),
            (-LCD_CUTOUT_W / 2 + 2, 0),
            (0, LCD_CUTOUT_H / 2 - 2),
            (0, -LCD_CUTOUT_H / 2 + 2),
        ]:
            pt = cq.Vector(LCD_CENTER_X + dx, LCD_CENTER_Y + dy, plate_z)
            self.assertFalse(
                shape.isInside(pt),
                f"LCD area {pt.toTuple()} should be cut out",
            )

        # A point on the top plate outside the LCD cutout should be solid.
        outside_pt = cq.Vector(0, -(INNER_WIDTH_REF / 2 - WALL_THICKNESS - 3), plate_z)
        self.assertTrue(
            shape.isInside(outside_pt),
            f"Lid surface {outside_pt.toTuple()} outside LCD should be solid",
        )

    def test_lid_has_inner_lcd_clip_holder_for_80x35_7_module(self):
        """Cap inner side should include clip-holder features for 80.0 x 35.7 x 8.5 mm LCD."""
        self.assertTrue(LID_STEP_PATH.exists(), f"Missing STEP file: {LID_STEP_PATH}")

        shape = _load_shape()
        bbox = shape.BoundingBox()

        # Probe just below inner face and also near module bottom to ensure retention depth.
        inner_face_z = bbox.zmax - WALL_THICKNESS
        near_face_z = inner_face_z - 0.8
        retention_overlap = 1.0  # clip should still overlap module near its bottom edge
        hold_depth_z = inner_face_z - (LCD_MODULE_HEIGHT - retention_overlap)

        module_half_w = LCD_MODULE_OUTER_W / 2
        module_half_h = LCD_MODULE_OUTER_H / 2

        # Four expected clip zones around the LCD outer perimeter.
        side_offsets = [
            (-module_half_w + 1.5, 0),
            (module_half_w - 1.5, 0),
            (0, -module_half_h + 1.5),
            (0, module_half_h - 1.5),
        ]

        for probe_z, label in [(near_face_z, "near inner face"), (hold_depth_z, "hold depth")]:
            clip_probe_points = [
                cq.Vector(LCD_CENTER_X + dx, LCD_CENTER_Y + dy, probe_z)
                for dx, dy in side_offsets
            ]
            solid_count = sum(1 for pt in clip_probe_points if shape.isInside(pt))
            self.assertGreaterEqual(
                solid_count,
                4,
                "Expected 4 inner LCD clip-holder contacts around "
                f"80.0 x 35.7 mm module ({label}), found {solid_count}",
            )

    def test_lid_has_push_button_hole(self):
        """Lid must have a circular push button hole to the right of the LCD."""
        self.assertTrue(LID_STEP_PATH.exists(), f"Missing STEP file: {LID_STEP_PATH}")

        shape = _load_shape()
        bbox = shape.BoundingBox()

        # Sample the top plate mid-thickness
        plate_z = bbox.zmax - WALL_THICKNESS / 2

        # Centre of push button hole should be air
        btn_pt = cq.Vector(PUSH_BTN_X, PUSH_BTN_Y, plate_z)
        self.assertFalse(
            shape.isInside(btn_pt),
            f"Push button centre {btn_pt.toTuple()} should be cut out",
        )

        # Button centre must be to the right of the LCD right edge
        lcd_right_edge = LCD_CENTER_X + LCD_CUTOUT_W / 2
        self.assertGreater(
            PUSH_BTN_X, lcd_right_edge,
            "Push button must be to the right of the LCD cutout",
        )

        # Material should exist around the button on the top plate
        surround_offset = PUSH_BUTTON_DIA / 2 + 1.5
        for dx, dy in [(surround_offset, 0), (0, surround_offset)]:
            surround_pt = cq.Vector(
                PUSH_BTN_X + dx, PUSH_BTN_Y + dy, plate_z,
            )
            # Only check if point is within the top plate footprint
            if (abs(surround_pt.x) < INNER_LENGTH_REF / 2
                    and abs(surround_pt.y) < INNER_WIDTH_REF / 2):
                self.assertTrue(
                    shape.isInside(surround_pt),
                    f"Lid material around button {surround_pt.toTuple()} should be solid",
                )


if __name__ == "__main__":
    unittest.main()
