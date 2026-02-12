import unittest
from pathlib import Path

import cadquery as cq


OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"
LID_STEP_PATH = OUTPUT_DIR / "lcd_arduino_enclosure_lid.step"

# Lid dimensions (from case.py)
BOX_LENGTH = 103
BOX_WIDTH = 54
WALL_THICKNESS = 2.5
LID_HEIGHT = 50 / 5  # box_height / 5

# LCD cutout (from case.py)
LCD_CUTOUT_W = 66
LCD_CUTOUT_H = 16
LCD_CENTER_X = 0.0   # centred on lid
LCD_CENTER_Y = 0.0   # centred on lid

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
        outside_pt = cq.Vector(0, -(BOX_WIDTH / 2 - WALL_THICKNESS - 3), plate_z)
        self.assertTrue(
            shape.isInside(outside_pt),
            f"Lid surface {outside_pt.toTuple()} outside LCD should be solid",
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
            if (abs(surround_pt.x) < BOX_LENGTH / 2
                    and abs(surround_pt.y) < BOX_WIDTH / 2):
                self.assertTrue(
                    shape.isInside(surround_pt),
                    f"Lid material around button {surround_pt.toTuple()} should be solid",
                )


if __name__ == "__main__":
    unittest.main()
