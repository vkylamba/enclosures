# Arduino Mega LCD Enclosure - Design Document

## Purpose

This document describes the complete design of a 3D-printable enclosure for an Arduino Mega with an LCD display. It is intended as a reference for future AI agents or humans modifying the design. The enclosure is generated programmatically using CadQuery (Python) and exported as STEP, STL, and SVG files.

## Source File

- **`case.py`** - Single-file parametric design. All dimensions are defined as named variables at the top. Running the script regenerates all output files.
- **Environment**: Python 3.11 venv at `.venv/`. Run with `.venv/bin/python case.py`.
- **Output directory**: `output/` containing STEP, STL, SVG for both base and lid.

## What the Enclosure Houses

| Component | Notes |
|---|---|
| Arduino Mega 2560 | Mounted to floor via 6 M3 through-holes matching official board drawing |
| 16x2 or similar character LCD | Visible through lid cutout (66x16mm) |
| Panel-mount push button | 7mm diameter hole on lid, right of LCD |
| USB connector | Accessible through left wall cutout |
| RJ45 jack | Accessible through left wall cutout, above USB |
| DC barrel power jack | 9mm hole on left wall |
| 6x 3.5mm audio jacks | 4 on right wall, 1 on front wall, 1 on back wall |

## Two-Part Assembly

The enclosure is a two-part snap-fit design: **base** (open-top box) and **lid** (inset plate with skirt).

### Base

- Open-top box with rounded vertical corners and bottom edges (2mm fillet radius)
- Floor has 6 through-holes for Arduino Mega M3 standoffs
- Four walls with various connector cutouts
- Alignment ledge at top of inner cavity (0.75mm step inward, 2mm tall) for positive lid registration
- 4 snap-fit clip grooves in inner X-walls (2 per wall) for tool-less lid retention
- 8 pry slots (2 per wall) on all 4 walls for screwdriver-assisted lid removal
- DIN rail channel on the underside for panel mounting

### Lid

- Top plate that sits on the base walls, with a hollow skirt that drops inside the cavity
- LCD rectangular cutout centered on top face
- Push button circular cutout to the right of the LCD
- 4 snap-fit clip bumps on skirt X-faces (0.5mm protrusion) that engage base grooves
- Top edges rounded (0.75mm fillet radius) for comfortable handling
- 0.75mm clearance per side between skirt and inner cavity (increased for clip bumps)

## Dimensions

### Inner Cavity
- Length: 103mm
- Width: 54mm
- Height: 50mm

### Outer Shell
- Length: 108mm (103 + 2 x 2.5)
- Width: 59mm (54 + 2 x 2.5)
- Height: 55mm (50 + 2 x 2.5), split into base and lid
- Wall thickness: 2.5mm

### Lid
- Total lid height: 10mm (box_height / 5)
- Top plate thickness: 2.5mm (same as wall_thickness)
- Skirt height: 7.5mm (lid_height - lid_thickness)
- Skirt clearance: 0.75mm per side (increased for clip bumps)

## Wall Cutout Layout

### Left Wall (-X face)

From bottom to top:
1. **DC barrel jack**: 9mm diameter circle, 3mm above bottom edge, 5mm from front edge
2. **USB**: 10x5mm rectangle, 3mm above bottom edge, 13.5mm from back edge
3. **RJ45**: 16x14mm rectangle, 10mm gap above USB cutout, horizontally aligned with USB

### Right Wall (+X face)

4 audio jacks in a row:
- 6mm diameter each
- First center 7.5mm from front edge
- 12.8mm center-to-center spacing
- All at 14mm height from inner bottom

### Front and Back Walls (+/-Y faces)

- 1 audio jack each (6mm diameter)
- Center 24.5mm from the right edge (measured from +X side)
- Same 14mm height as right-wall jacks

## DIN Rail Mount

The enclosure mounts onto a standard TS35 (35mm) DIN rail via a channel on the underside of the base.

### Design

Two parallel walls extend downward from the enclosure bottom, each with an inward-facing L-shaped hook at the bottom. The rail slides into the channel from the side, or snaps on vertically.

### Parameters

| Parameter | Value | Rationale |
|---|---|---|
| Channel inner width | 35.6mm | 35mm rail + 0.3mm clearance per side |
| Guide wall height | 10mm | Sufficient grip depth |
| Channel length | outer_length - 10mm | 5mm shorter on each end to clear corners |
| Fixed wall thickness (+Y) | 3.0mm | Rigid hook side |
| Spring wall thickness (-Y) | 2.0mm | Thinner for flex/snap-on |
| Hook reach (inward) | 2.5mm | Catches rail lip |
| Hook thickness | 1.5mm | Shelf strength |
| Spring interference | 0.3mm | Extra reach on spring side for snap retention |

### How It Works

1. The fixed hook (+Y side) has a rigid 3mm wall with 2.5mm inward hook
2. The spring clip (-Y side) has a thinner 2mm wall that flexes outward when the rail is pressed in
3. The spring side has 0.3mm extra hook reach (interference fit) so it snaps back and locks
4. To remove: flex the spring wall outward and tilt the enclosure off the rail

### Orientation

The DIN rail is on the **bottom** of the enclosure. The lid (with LCD and button) faces **upward** for visibility. This means the enclosure hangs below the DIN rail.

## Fillets and Edge Treatment

Fillets improve structural integrity, print quality, and handling comfort. Applied in a specific order to avoid CadQuery/OCCT kernel failures on complex geometry.

### Applied Fillets

| Location | Radius | Applied To | Purpose |
|---|---|---|---|
| Base vertical corners | 2.0mm | 4 vertical edges of outer box | Comfortable grip, no sharp corners |
| Base bottom edges | 2.0mm | Bottom perimeter of outer box | Smooth base, better print adhesion |
| DIN channel top edges | 0.75mm | Top edges where channel walls meet enclosure bottom | Structural - prevents cracking at junction under load |
| Lid top edges | 0.75mm | Top perimeter of lid | Comfortable handling |

### Fillet Application Order (Critical)

1. **Outer box fillets** are applied BEFORE the inner cavity is cut. This ensures `edges("|Z")` and `edges("<Z")` select exactly the intended edges on a simple box.
2. **DIN channel fillets** are applied AFTER unioning the 4 channel parts but BEFORE unioning with the base. This isolates the fillet to channel geometry.
3. **Lid fillets** are applied AFTER all cutouts (LCD, button, screw holes). The `edges(">Z")` selector picks all top-face edges including around cutouts.

### CadQuery Fillet Limitations

The OCCT kernel used by CadQuery can fail on fillets applied to complex boolean geometry. The following fallback strategy was used during development:

- **Original target**: `din_fillet_r = 1.5mm`, `lid_fillet_r = 1.5mm`
- **Actual applied**: Half-radius (0.75mm) for both DIN channel and lid, because full radius caused `BRep_API: command not done` errors
- **Outer box fillets**: Full 2.0mm worked because they are applied to simple box geometry before any boolean operations
- **Fallback chain**: Try full radius -> try half radius -> try chamfer instead -> skip

## Lid Retention System

The lid uses a hybrid snap-fit + optional screw design for tool-less daily access while retaining vibration security when needed.

### Snap-Fit Clips (Primary Retention)

4 clip bumps on the lid skirt (2 per X-wall) engage matching grooves in the base inner walls. Press the lid down and it clicks into place; use the pry slots on the front wall to lever the lid off.

| Parameter | Value | Rationale |
|---|---|---|
| Bump width | 5.0mm | Along wall, sufficient engagement area |
| Bump height | 2.0mm | Vertical engagement |
| Bump depth (protrusion) | 0.5mm | Gentle snap force, easy release |
| Y positions | -12mm, +12mm from center | Spread for even retention |
| Groove extra clearance | 0.4mm | 0.2mm per side for easy snap |
| Groove depth | 0.7mm | Pocket into base wall |

### Alignment Ledge

A rectangular ring at the top of the base inner cavity that narrows the opening by 0.75mm per side. The skirt registers against this step for positive lateral alignment (no rattling).

| Parameter | Value |
|---|---|
| Ledge depth | 0.75mm inward from cavity wall |
| Ledge height | 2.0mm tall |

### Pry Slots (Lid Removal Aid)

8 rectangular notches (2 per wall) cut into the top edge of all 4 base walls from the outside face. When the lid is seated, a flat-head screwdriver tip fits into the slot between the base wall and the lid's overhanging top plate, then twists to lever the lid up.

| Parameter | Value | Rationale |
|---|---|---|
| Slot width | 6.0mm | Along wall, fits standard screwdriver tip |
| Slot depth | 2.0mm | Inward from outer wall face |
| Slot height | 2.5mm | Down from base wall top (= wall_thickness) |
| Y-wall X positions | -15mm, +15mm from center | Spread along length |
| X-wall Y positions | -10mm, +10mm from center | Spread along width (shorter walls) |

### Why This Design

Snap-fit clips provide tool-less lid closure but need a way to release. Pry slots at the parting line are the standard approach on commercial DIN-rail enclosures — insert a screwdriver and twist to pop the lid off.

## Coordinate System

CadQuery centers the box at origin (0,0,0). All positions are relative to center:

- **X axis**: Length direction. -X is "left" wall (USB/RJ45/power). +X is "right" wall (4 audio jacks).
- **Y axis**: Width direction. +/-Y are front/back walls (1 extra audio jack each). +Y is the DIN rail fixed hook side.
- **Z axis**: Height direction. -Z is bottom (DIN rail). +Z is top (lid).

## 3D Printing Considerations

### Print Orientation
- **Base**: Print upright (open side up). The filleted bottom edges improve first-layer adhesion.
- **Lid**: Print upside down (top plate on build surface). The flat top plate gives best surface finish for the LCD viewing area.

### Material
- PLA or PETG recommended. The DIN rail spring clip requires some material flex - PETG handles this better for long-term use.

### Tolerances
- 0.75mm lid clearance per side accounts for clip bumps and FDM tolerance at 0.2mm layer height
- DIN rail 0.3mm clearance per side accounts for typical FDM dimensional accuracy
- Clip groove has 0.4mm total extra clearance (0.2mm/side) vs bump for reliable snap engagement
- Screw holes may need drilling out depending on printer calibration

## Known Limitations and Future Improvement Areas

1. **No ventilation**: The enclosure is sealed except for connector cutouts. Consider adding ventilation slots if heat dissipation is needed.
2. **No cable strain relief**: Connectors are just holes. Adding strain relief features (cable clips, grommet grooves) would improve durability.
3. **No internal cable routing**: Wires from connectors to Arduino are unmanaged. Consider adding internal wire channels or tie-down points.
4. **Snap-fit clip tuning**: Clip bump depth (0.5mm) and groove clearance (0.4mm) may need adjustment based on printer accuracy. If clips are too tight, increase `clip_groove_extra`; if too loose, increase `clip_bump_depth`.
5. **DIN rail hook chamfers**: The plan called for 0.5mm lead-in chamfers on hook tips for easier rail mounting. Not yet implemented due to complexity of selecting specific edges on the hook geometry. Future work should add these.
6. **Fillet radii are reduced**: DIN channel and lid fillets are at 0.75mm instead of the ideal 1.5mm. Future CadQuery versions or alternative modeling approaches (building fillets into the sketch profile rather than applying them post-boolean) may allow larger radii.
7. **LCD cutout has no bezel/recess**: A stepped recess around the LCD cutout would allow the display to sit flush and be protected.
8. **No labeling**: Consider adding embossed or debossed text for connector labels, product name, or version info.
9. **Mounting holes are through-holes**: Currently just holes through the floor. Adding raised standoff bosses would properly space the Arduino board above the floor.
10. **Single enclosure size**: The design is parametric but not yet modular. Could be extended to support different board sizes (Uno, Nano, ESP32) by swapping dimension sets.

## File Inventory

| File | Format | Description |
|---|---|---|
| `case.py` | Python | Parametric source - regenerates everything |
| `output/lcd_arduino_enclosure_base.step` | STEP | Base part for CAD import |
| `output/lcd_arduino_enclosure_base.stl` | STL | Base part for slicing/printing |
| `output/lcd_arduino_enclosure_base.svg` | SVG | Base 2D projection for documentation |
| `output/lcd_arduino_enclosure_lid.step` | STEP | Lid part for CAD import |
| `output/lcd_arduino_enclosure_lid.stl` | STL | Lid part for slicing/printing |
| `output/lcd_arduino_enclosure_lid.svg` | SVG | Lid 2D projection for documentation |
| `requirements.txt` | Text | Python dependencies (cadquery) |
| `DESIGN.md` | Markdown | This document |
