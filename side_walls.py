#!/usr/bin/env python3
from enclosure_parts import build_base, export_shape


def main() -> int:
    _, audio_panel, connector_panel = build_base()
    export_shape(audio_panel, "lcd_arduino_enclosure_audio_panel.step", "lcd_arduino_enclosure_audio_panel.stl")
    export_shape(connector_panel, "lcd_arduino_enclosure_connector_panel.step", "lcd_arduino_enclosure_connector_panel.stl")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
