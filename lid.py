#!/usr/bin/env python3
from enclosure_parts import build_lid, export_shape


def main() -> int:
    lid = build_lid()
    export_shape(lid, "lcd_arduino_enclosure_lid.step", "lcd_arduino_enclosure_lid.stl")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
