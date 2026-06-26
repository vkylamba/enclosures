import unittest
from pathlib import Path

import cadquery as cq

from enclosure_parts import (
    BOX_LENGTH,
    BOX_WIDTH,
    LCD_CUTOUT,
    LCD_MODULE_HEIGHT,
    LCD_MODULE_OUTER_H,
    LCD_MODULE_OUTER_W,
    LID_HEIGHT,
    OUTPUT_DIR,
    SLOT_CLEARANCE,
    SWITCH_BODY_H,
    SWITCH_BODY_W,
    SWITCH_CLEARANCE,
    SWITCH_HOLDER_LIP_HEIGHT,
    SWITCH_HOLDER_WALL,
    SWITCH_PLUNGER_GAP,
    SWITCH_SUPPORT_FLOOR,
    TAB_GAP_FROM_LCD,
    TAB_LENGTH,
    TAB_WIDTH,
    LIVING_HINGE_WIDTH,
    WALL_THICKNESS,
)


LID_STEP_PATH = OUTPUT_DIR / "lcd_arduino_enclosure_lid.step"
BASE_STEP_PATH = OUTPUT_DIR / "lcd_arduino_enclosure_base.step"

switch_cavity_size = SWITCH_BODY_W + 2 * SWITCH_CLEARANCE
switch_holder_outer = switch_cavity_size + 2 * SWITCH_HOLDER_WALL
cavity_half = switch_cavity_size / 2
wall_half = cavity_half + SWITCH_HOLDER_WALL / 2

lcd_right_x = LCD_CUTOUT[0] / 2
hinge_left_x = lcd_right_x + TAB_GAP_FROM_LCD
tab_left_x = hinge_left_x + LIVING_HINGE_WIDTH + SLOT_CLEARANCE
tab_right_x = tab_left_x + TAB_LENGTH
TAB_CENTER_X = (tab_left_x + tab_right_x) / 2
TAB_CENTER_Y = 0.0


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
        self.assertGreaterEqual(lid_bbox.xlen, base_bbox.xlen - 0.3)
        self.assertGreaterEqual(lid_bbox.ylen, base_bbox.ylen - 0.3)

    def test_lid_has_lcd_cutout(self):
        """Lid top face must have a rectangular LCD cutout."""
        self.assertTrue(LID_STEP_PATH.exists(), f"Missing STEP file: {LID_STEP_PATH}")

        shape = _load_shape()
        bbox = shape.BoundingBox()

        # Top plate is at the top of the lid; sample its mid-thickness
        plate_z = bbox.zmax - WALL_THICKNESS / 2

        # Centre of LCD cutout should be air (cutThruAll)
        lcd_pt = cq.Vector(0.0, 0.0, plate_z)
        self.assertFalse(
            shape.isInside(lcd_pt),
            f"LCD centre {lcd_pt.toTuple()} should be cut out, not solid",
        )

        # Sample points within the LCD rectangle should also be air
        for dx, dy in [
            (LCD_CUTOUT[0] / 2 - 2, 0),
            (-LCD_CUTOUT[0] / 2 + 2, 0),
            (0, LCD_CUTOUT[1] / 2 - 2),
            (0, -LCD_CUTOUT[1] / 2 + 2),
        ]:
            pt = cq.Vector(dx, dy, plate_z)
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
                cq.Vector(dx, dy, probe_z)
                for dx, dy in side_offsets
            ]
            solid_count = sum(1 for pt in clip_probe_points if shape.isInside(pt))
            self.assertGreaterEqual(
                solid_count,
                4,
                "Expected 4 inner LCD clip-holder contacts around "
                f"80.0 x 35.7 mm module ({label}), found {solid_count}",
            )

    def test_lid_has_living_hinge_push_tab(self):
        """Lid must have a living-hinge press tab to the right of the LCD."""
        self.assertTrue(LID_STEP_PATH.exists(), f"Missing STEP file: {LID_STEP_PATH}")

        shape = _load_shape()
        bbox = shape.BoundingBox()

        plate_z = bbox.zmax - WALL_THICKNESS / 2
        inner_face_z = bbox.zmax - WALL_THICKNESS

        # Press tab centre should remain solid material
        tab_pt = cq.Vector(TAB_CENTER_X, TAB_CENTER_Y, plate_z)
        self.assertTrue(
            shape.isInside(tab_pt),
            f"Living hinge tab centre {tab_pt.toTuple()} should be solid",
        )

        # Tab must be to the right of the LCD cutout
        lcd_right_edge = LCD_CUTOUT[0] / 2
        self.assertGreater(
            TAB_CENTER_X, lcd_right_edge,
            "Living hinge tab must be to the right of the LCD cutout",
        )

        # U-slot beside the tab should be cut through the top plate
        slot_pt = cq.Vector(tab_right_x + SLOT_CLEARANCE / 2, TAB_CENTER_Y, plate_z)
        self.assertFalse(
            shape.isInside(slot_pt),
            f"Slot beside tab {slot_pt.toTuple()} should be cut out",
        )

        # Air gap between flex tab underside and stationary switch plunger
        gap_pt = cq.Vector(TAB_CENTER_X, TAB_CENTER_Y, inner_face_z - SWITCH_PLUNGER_GAP / 2)
        self.assertFalse(
            shape.isInside(gap_pt),
            f"Plunger gap {gap_pt.toTuple()} should be open air, not solid",
        )

        # Switch cavity on fixed bridge should be hollow
        switch_top_z = inner_face_z - SWITCH_PLUNGER_GAP
        pocket_pt = cq.Vector(TAB_CENTER_X, TAB_CENTER_Y, switch_top_z - SWITCH_BODY_H / 2)
        self.assertFalse(
            shape.isInside(pocket_pt),
            f"Switch cavity {pocket_pt.toTuple()} should be cut out",
        )

        # Fixed bridge tying into skirt walls should be solid (probe at wall, not cavity)
        switch_floor_z = switch_top_z - SWITCH_BODY_H - SWITCH_SUPPORT_FLOOR
        skirt_inner_half_w = (BOX_WIDTH - 2 * 0.2 - 2 * WALL_THICKNESS) / 2  # matches lid skirt inner
        bridge_pt = cq.Vector(TAB_CENTER_X, skirt_inner_half_w - 1.0, switch_floor_z + SWITCH_SUPPORT_FLOOR / 2)
        self.assertTrue(
            shape.isInside(bridge_pt),
            f"Fixed switch bridge {bridge_pt.toTuple()} should be solid",
        )

        # Holder walls around the cavity should be solid
        holder_mid_z = switch_floor_z + SWITCH_SUPPORT_FLOOR + SWITCH_BODY_H / 2
        for dx, dy in [(wall_half, 0), (0, wall_half)]:
            wall_pt = cq.Vector(TAB_CENTER_X + dx, TAB_CENTER_Y + dy, holder_mid_z)
            self.assertTrue(
                shape.isInside(wall_pt),
                f"Switch holder wall {wall_pt.toTuple()} should be solid",
            )

        # Snap lips at cavity floor should be solid on each side
        lip_z = switch_floor_z + SWITCH_SUPPORT_FLOOR + SWITCH_HOLDER_LIP_HEIGHT / 2
        lip_probe_points = [
            cq.Vector(TAB_CENTER_X + cavity_half - 0.2, TAB_CENTER_Y, lip_z),
            cq.Vector(TAB_CENTER_X, TAB_CENTER_Y + cavity_half - 0.2, lip_z),
        ]
        lip_solid_count = sum(1 for pt in lip_probe_points if shape.isInside(pt))
        self.assertGreaterEqual(
            lip_solid_count,
            2,
            f"Expected snap lips at switch cavity floor, found {lip_solid_count}",
        )


if __name__ == "__main__":
    unittest.main()
