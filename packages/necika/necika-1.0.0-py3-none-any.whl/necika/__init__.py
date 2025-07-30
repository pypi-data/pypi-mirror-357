# SPDX-FileCopyrightText: 2023 CELESTIFYX Team
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Necika - A comprehensive color manipulation library for Python.

This library provides extensive color manipulation capabilities including
- Color space conversions (RGB, HSL, HSV, CMYK, etc.)
- Color palette generation
- Terminal color output with ANSI codes
- Color validation and parsing
- Color mixing and blending
- Accessibility features (contrast ratios, color blindness simulation)
"""

from necika.color import Color
from necika.palette import ColorPalette
from necika.terminal import TerminalColor
from necika.exceptions import (ColorError, InvalidColorError, ColorConversionError)
from necika.constants import (NAMED_COLORS, ANSI_COLORS)
from necika.utils import (hex_to_rgb, rgb_to_hex, rgb_to_hsl, hsl_to_rgb)

__all__: list[str] = [
    "Color",
    "ColorPalette", 
    "TerminalColor",
    "ColorError",
    "InvalidColorError",
    "ColorConversionError",
    "NAMED_COLORS",
    "ANSI_COLORS",
    "hex_to_rgb",
    "rgb_to_hex",
    "rgb_to_hsl",
    "hsl_to_rgb"
]
