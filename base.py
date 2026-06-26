#!/usr/bin/env python3
from enclosure_parts import build_base, export_shape


def main() -> int:
    base, _, _ = build_base()
    export_shape(base, "lcd_arduino_enclosure_base.step", "lcd_arduino_enclosure_base.stl")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
