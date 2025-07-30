# SPDX-FileCopyrightText: 2023 CELESTIFYX Team
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations
from typing import Any

import re

from necika.exceptions import (InvalidColorError, ColorRangeError)
from necika.constants import NAMED_COLORS
from necika.utils import (hex_to_rgb, rgb_to_hex, rgb_to_hsl, hsl_to_rgb, rgb_to_hsv, hsv_to_rgb, rgb_to_cmyk, cmyk_to_rgb, calculate_luminance, calculate_contrast_ratio, is_light_color, blend_colors)

class Color:
    """
    A comprehensive color class supporting multiple color spaces and operations.

    The Color class is the core component of Necika, providing extensive color
    manipulation capabilities across RGB, HSL, HSV, and CMYK color spaces.

    Features:
    - Multiple input formats (hex, RGB tuples, named colors, color strings)
    - Color space conversions (RGB ↔ HSL ↔ HSV ↔ CMYK)
    - Color manipulation (lighten, darken, saturate, desaturate)
    - Color theory operations (complement, triadic, analogous, etc.)
    - Accessibility features (contrast ratios, WCAG compliance)
    - Color blending and mixing

    Examples:
        Basic color creation:
            >>> red: Color = Color('#FF0000')
            >>> blue: Color = Color('blue')
            >>> green: Color = Color((0, 255, 0))

        Color manipulation:
            >>> lighter_red: Color = red.lighten(0.2)
            >>> complement: Color = red.complement()
            >>> blended: Color = red.blend(blue, 0.5)

        Color analysis:
            >>> print(red.luminance) # 0.2126
            >>> print(red.is_light) # False
            >>> print(red.contrast_ratio(Color('white'))) # 3.998

        Color space conversions:
            >>> print(red.hsl) # (0.0, 100.0, 50.0)
            >>> print(red.hsv) # (0.0, 100.0, 100.0)
            >>> print(red.cmyk) # (0.0, 100.0, 100.0, 0.0)
    """
    def __init__(self, color: str | tuple[int, int, int] | 'Color') -> None:
        """
        Initialize a Color object from various input formats.

        Args:
            color: Color specification in one of the following formats:
                - Hex string: '#FF0000', 'FF0000', '#F00'
                - RGB tuple: (255, 0, 0)
                - Named color: 'red', 'blue', 'forestgreen'
                - RGB string: 'rgb(255, 0, 0)'
                - HSL string: 'hsl(0, 100%, 50%)'
                - Color object: existing Color instance

        Raises:
            InvalidColorError: If a color format is not recognized
            ColorRangeError: If RGB values are out of valid range (0-255)

        Examples:
            >>> Color('#FF0000')           # Hex with hash
            >>> Color('FF0000')            # Hex without hash
            >>> Color('#F00')              # Short hex
            >>> Color('red')               # Named color
            >>> Color((255, 0, 0))         # RGB tuple
            >>> Color('rgb(255, 0, 0)')    # RGB string
            >>> Color('hsl(0, 100%, 50%)') # HSL string
        """
        self._r: int = 0
        self._g: int = 0
        self._b: int = 0

        # Color input type mapping
        color_handlers: dict[..., ...] = {
            Color: self._from_color_object,
            str:   self._parse_string_color,
            tuple: self._from_rgb_tuple,
            list:  self._from_rgb_tuple
        }

        handler: Any | None = color_handlers.get(type(color))

        if handler is None:
            raise InvalidColorError(color, message="Color must be hex string, RGB tuple, named color, or Color object")

        handler(color)

    def _from_color_object(self, color: 'Color') -> None:
        """Initialize from another Color object."""
        (self._r, self._g, self._b) = color.rgb

    def _from_rgb_tuple(self, color: tuple[int, int, int] | list[int]) -> None:
        """Initialize from RGB tuple or list."""
        if len(color) != 3:
            raise InvalidColorError(color, message="RGB tuple must have exactly 3 values")

        self._set_rgb(*color)

    def _parse_string_color(self, color_str: str) -> None:
        """
        Parse string color representation using a strategy pattern.

        Supports multiple string formats:
        - Named colors: 'red', 'blue', 'forestgreen'
        - Hex colors: '#FF0000', 'FF0000', '#F00'
        - RGB format: 'rgb(255, 0, 0)'
        - HSL format: 'hsl(0, 100%, 50%)'
        """
        color_str: str = color_str.strip().lower()

        # String parsing strategies
        parsing_strategies: list[...] = [
            self._try_named_color,
            self._try_hex_color,
            self._try_rgb_string,
            self._try_hsl_string,
        ]

        for strategy in parsing_strategies:
            if strategy(color_str):
                return

        raise InvalidColorError(color_str, message="Unrecognized color format")

    def _try_named_color(self, color_str: str) -> bool:
        """Try to parse as named color."""
        if color_str in NAMED_COLORS:
            (self._r, self._g, self._b) = NAMED_COLORS[color_str]
            return True

        return False

    def _try_hex_color(self, color_str: str) -> bool:
        """Try to parse as hex color."""
        if color_str.startswith('#') or re.match(pattern=r'^[0-9a-f]{3,6}$', string=color_str):
            try:
                (self._r, self._g, self._b) = hex_to_rgb(color_str)
                return True
            except InvalidColorError:
                return False

        return False

    def _try_rgb_string(self, color_str: str) -> bool:
        """Try to parse as RGB string format."""
        rgb_match: re.Match[str] | None = re.match(pattern=r'rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', string=color_str)

        if rgb_match:
            (r, g, b) = map(int, rgb_match.groups())
            self._set_rgb(r, g, b)

            return True

        return False

    def _try_hsl_string(self, color_str: str) -> bool:
        """Try to parse as HSL string format."""
        hsl_match: re.Match[str] | None = re.match(pattern=r'hsl\s*\(\s*(\d+)\s*,\s*(\d+)%\s*,\s*(\d+)%\s*\)', string=color_str)

        if hsl_match:
            (h, s, l) = map(int, hsl_match.groups())
            (self._r, self._g, self._b) = hsl_to_rgb(h, s, l)

            return True

        return False

    def _set_rgb(self, r: int, g: int, b: int) -> None:
        """
        Set RGB values with validation.

        Args:
            r: RGB values (must be 0-255)
            g: RGB values (must be 0-255)
            b: RGB values (must be 0-255)

        Raises:
            ColorRangeError: If any RGB value is out of range
        """
        for (component, value) in [('r', r), ('g', g), ('b', b)]:
            if not isinstance(value, int) or not 0 <= value <= 255:
                raise ColorRangeError(component, value, (0, 255))

        (self._r, self._g, self._b) = (r, g, b)

    @property
    def rgb(self) -> tuple[int, int, int]:
        """
        Get RGB tuple.

        Returns:
            Tuple of (red, green, blue) values (0-255)

        Example:
            >>> color: Color = Color('#FF8040')
            >>> print(color.rgb)
            (255, 128, 64)
        """
        return self._r, self._g, self._b

    @property
    def r(self) -> int:
        """Get red component (0-255)."""
        return self._r

    @property
    def g(self) -> int:
        """Get green component (0-255)."""
        return self._g

    @property
    def b(self) -> int:
        """Get blue component (0-255)."""
        return self._b

    @property
    def hex(self) -> str:
        """
        Get hexadecimal representation.

        Returns:
            Hex color string with '#' prefix (e.g., '#FF0000')

        Example:
            >>> Color((255, 0, 0)).hex
            '#FF0000'
        """
        return rgb_to_hex(self._r, self._g, self._b)

    @property
    def hsl(self) -> tuple[float, float, float]:
        """
        Get HSL (Hue, Saturation, Lightness) representation.

        Returns:
            Tuple of (hue, saturation, lightness) where:
            - hue: 0-360 degrees
            - saturation: 0-100 percent
            - lightness: 0-100 percent

        Example:
            >>> Color('#FF0000').hsl
            (0.0, 100.0, 50.0)
        """
        return rgb_to_hsl(self._r, self._g, self._b)

    @property
    def hsv(self) -> tuple[float, float, float]:
        """
        Get HSV (Hue, Saturation, Value) representation.

        Returns:
            Tuple of (hue, saturation, value) where:
            - hue: 0-360 degrees
            - saturation: 0-100 percent
            - value: 0-100 percent

        Example:
            >>> Color('#FF0000').hsv
            (0.0, 100.0, 100.0)
        """
        return rgb_to_hsv(self._r, self._g, self._b)

    @property
    def cmyk(self) -> tuple[float, float, float, float]:
        """
        Get CMYK (Cyan, Magenta, Yellow, Black) representation.

        Returns:
            Tuple of (cyan, magenta, yellow, black) values (0-100 percent)

        Example:
            >>> Color('#FF0000').cmyk
            (0.0, 100.0, 100.0, 0.0)
        """
        return rgb_to_cmyk(self._r, self._g, self._b)

    @property
    def luminance(self) -> float:
        """
        Get relative luminance according to WCAG guidelines.

        Returns:
            Relative luminance value (0.0 = black, 1.0 = white)

        Note:
            Used for calculating contrast ratios and accessibility compliance.

        Example:
            >>> Color('#FFFFFF').luminance # White
            1.0
            >>> Color('#000000').luminance # Black
            0.0
        """
        return calculate_luminance(self._r, self._g, self._b)

    @property
    def is_light(self) -> bool:
        """
        Check if color is considered light (luminance > 0.5).

        Returns:
            True if color is light, False if dark

        Example:
            >>> Color('#FFFFFF').is_light
            True
            >>> Color('#000000').is_light
            False
        """
        return is_light_color(self._r, self._g, self._b)

    @property
    def is_dark(self) -> bool:
        """
        Check if color is considered dark (luminance <= 0.5).

        Returns:
            True if color is dark, False if light
        """
        return not self.is_light

    def lighten(self, amount: float = 0.1) -> 'Color':
        """
        Create a lighter version of the color by increasing lightness in HSL space.

        Args:
            amount: Amount to lighten (0.0-1.0, default 0.1)

        Returns:
            New Color object with increased lightness

        Example:
            >>> red:         Color = Color('#FF0000')
            >>> lighter_red: Color = red.lighten(0.2)

            >>> print(lighter_red.hex)
            '#FF6666'
        """
        (h, s, l) = self.hsl
        l: float = min(100.0, l + amount * 100)

        return Color.from_hsl(h, s, l)

    def darken(self, amount: float = 0.1) -> 'Color':
        """
        Create a darker version of the color by decreasing lightness in HSL space.

        Args:
            amount: Amount to darken (0.0-1.0, default 0.1)

        Returns:
            New Color object with decreased lightness

        Example:
            >>> red:        Color = Color('#FF0000')
            >>> darker_red: Color = red.darken(0.2)

            >>> print(darker_red.hex)
            '#990000'
        """
        (h, s, l) = self.hsl
        l: float = max(0.0, l - amount * 100)

        return Color.from_hsl(h, s, l)

    def saturate(self, amount: float = 0.1) -> 'Color':
        """
        Create a more saturated version of the color.

        Args:
            amount: Amount to increase saturation (0.0-1.0, default 0.1)

        Returns:
            New Color object with increased saturation
        """
        (h, s, l) = self.hsl
        s: float = min(100.0, s + amount * 100)

        return Color.from_hsl(h, s, l)

    def desaturate(self, amount: float = 0.1) -> 'Color':
        """
        Create a less saturated version of the color.

        Args:
            amount: Amount to decrease saturation (0.0-1.0, default 0.1)

        Returns:
            New Color object with decreased saturation
        """
        (h, s, l) = self.hsl
        s: float = max(0.0, s - amount * 100)

        return Color.from_hsl(h, s, l)

    def rotate_hue(self, degrees: float) -> 'Color':
        """
        Rotate the hue by specified degrees on the color wheel.

        Args:
            degrees: Degrees to rotate (-360 to 360)

        Returns:
            New Color object with rotated hue

        Example:
            >>> red:   Color = Color('#FF0000')
            >>> green: Color = red.rotate_hue(120) # 120° rotation

            >>> print(green.hex)
            '#00FF00'
        """
        (h, s, l) = self.hsl
        h: float = (h + degrees) % 360
        return Color.from_hsl(h, s, l)

    def complement(self) -> 'Color':
        """
        Get the complementary color (opposite on color wheel, 180° rotation).

        Returns:
            New Color object representing the complement

        Example:
            >>> red:  Color = Color('#FF0000')
            >>> cyan: Color = red.complement()

            >>> print(cyan.hex)
            '#00FFFF'
        """
        return self.rotate_hue(180)

    def triadic(self) -> tuple['Color', 'Color']:
        """
        Get triadic colors (120° and 240° apart on color wheel).

        Returns:
            Tuple of two Color objects forming a triadic color scheme

        Example:
            >>> red: Color = Color('#FF0000')
            >>> (green, blue) = red.triadic()

            >>> print(green.hex, blue.hex)
            '#00FF00' '#0000FF'
        """
        return self.rotate_hue(120), self.rotate_hue(240)

    def analogous(self, angle: float = 30) -> tuple['Color', 'Color']:
        """
        Get analogous colors (adjacent on color wheel).

        Args:
            angle: Angle separation in degrees (default 30°)

        Returns:
            Tuple of two Color objects forming an analogous color scheme

        Example:
            >>> red: Color = Color('#FF0000')
            >>> (orange, magenta) = red.analogous()
        """
        return self.rotate_hue(-angle), self.rotate_hue(angle)

    def split_complementary(self) -> tuple['Color', 'Color']:
        """
        Get split complementary colors (150° and 210° from base).

        Returns:
            Tuple of two Color objects forming a split complementary scheme

        Example:
            >>> red: Color = Color('#FF0000')
            >>> (color1, color2) = red.split_complementary()
        """
        return self.rotate_hue(150), self.rotate_hue(210)

    def tetradic(self) -> tuple['Color', 'Color', 'Color']:
        """
        Get tetradic (square) colors (90°, 180°, 270° from base).

        Returns:
            Tuple of three Color objects forming a tetradic color scheme

        Example:
            >>> red: Color = Color('#FF0000')
            >>> colors: tuple[Color, Color, Color] = red.tetradic()

            >>> print([c.hex for c in colors]) # type: ignore
            ['#80FF00', '#00FFFF', '#7F00FF']
        """
        return self.rotate_hue(90), self.rotate_hue(180), self.rotate_hue(270)

    def blend(self, other: 'Color', ratio: float = 0.5) -> 'Color':
        """
        Blend this color with another color using linear interpolation.

        Args:
            other: Color to blend with
            ratio: Blend ratio (0.0 = this color, 1.0 = other color, 0.5 = 50/50 mix)

        Returns:
            New Color object representing the blended result

        Example:
            >>> red:    Color = Color('#FF0000')
            >>> blue:   Color = Color('#0000FF')
            >>> purple: Color = red.blend(blue, 0.5)

            >>> print(purple.hex)
            '#800080'
        """
        blended_rgb: tuple[int, int, int] = blend_colors(self.rgb, other.rgb, ratio)
        return Color(blended_rgb)

    def contrast_ratio(self, other: 'Color') -> float:
        """
        Calculate a contrast ratio with another color according to WCAG guidelines.

        Args:
            other: Color to compare with

        Returns:
            Contrast ratio (1.0 = no contrast, 21.0 = maximum contrast)

        Note:
            Used for accessibility compliance checking.

        Example:
            >>> black: Color = Color('#000000')
            >>> white: Color = Color('#FFFFFF')

            >>> ratio: float = black.contrast_ratio(white)
            >>> print(ratio)
            21.0
        """
        return calculate_contrast_ratio(self.rgb, other.rgb)

    def meets_wcag_aa(self, other: 'Color') -> bool:
        """
        Check if a color combination meets WCAG AA accessibility standards.

        Args:
            other: Color to compare with (typically background color)

        Returns:
            True if a contrast ratio >= 4.5 (meets AA standards)

        Example:
            >>> text_color: Color = Color('#333333')
            >>> bg_color:   Color = Color('#FFFFFF')

            >>> print(text_color.meets_wcag_aa(bg_color))
            True
        """
        return self.contrast_ratio(other) >= 4.5

    def meets_wcag_aaa(self, other: 'Color') -> bool:
        """
        Check if a color combination meets WCAG AAA accessibility standards.

        Args:
            other: Color to compare with (typically background color)

        Returns:
            True if contrast ratio >= 7.0 (meets AAA standards)

        Example:
            >>> text_color: Color = Color('#000000')
            >>> bg_color:   Color = Color('#FFFFFF')

            >>> print(text_color.meets_wcag_aaa(bg_color))
            True
        """
        return self.contrast_ratio(other) >= 7.0

    def grayscale(self) -> 'Color':
        """
        Convert to grayscale using luminance-based conversion.

        Returns:
            New Color object in grayscale with equal RGB components

        Example:
            >>> red:  Color = Color('#FF0000')
            >>> gray: Color = red.grayscale()

            >>> print(gray.hex)
            '#363636'
        """
        gray_value: int = round(self.luminance * 255)
        return Color((gray_value, gray_value, gray_value))

    def invert(self) -> 'Color':
        """
        Get inverted color (255 - each RGB component).

        Returns:
            New Color object with inverted RGB values

        Example:
            >>> red:  Color = Color('#FF0000')
            >>> cyan: Color = red.invert()

            >>> print(cyan.hex)
            '#00FFFF'
        """
        return Color((255 - self._r, 255 - self._g, 255 - self._b))

    def to_dict(self) -> dict[str, Any]:
        """
        Convert color to comprehensive dictionary representation.

        Returns:
            Dictionary containing all color space representations and properties

        Example:
            >>> red: Color = Color('#FF0000')
            >>> data: dict[str, Any] = red.to_dict()

            >>> print(data['hex'])
            '#FF0000'
            >>> print(data['hsl'])
            {'h': 0.0, 's': 100.0, 'l': 50.0}
        """
        (h, s, l)       = self.hsl
        (hue, sat, val) = self.hsv
        (c, m, y, k)    = self.cmyk

        return {
            'rgb': {
                'r': self._r,
                'g': self._g,
                'b': self._b
            },

            'hex': self.hex,

            'hsl': {
                'h': round(h, 1),
                's': round(s, 1),
                'l': round(l, 1)
            },

            'hsv': {
                'h': round(hue, 1),
                's': round(sat, 1),
                'v': round(val, 1)
            },

            'cmyk': {
                'c': round(c, 1),
                'm': round(m, 1),
                'y': round(y, 1),
                'k': round(k, 1)
            },

            'luminance': round(self.luminance, 3),
            'is_light': self.is_light
        }

    @classmethod
    def from_hsl(cls, h: float, s: float, l: float) -> 'Color':
        """
        Create Color from HSL values.

        Args:
            h: Hue (0-360 degrees)
            s: Saturation (0-100 percent)
            l: Lightness (0-100 percent)

        Returns:
            New Color object

        Example:
            >>> red: Color = Color.from_hsl(0, 100, 50)
            >>> print(red.hex)
            '#FF0000'
        """
        rgb: tuple[int, int, int] = hsl_to_rgb(h, s, l)
        return cls(rgb)

    @classmethod
    def from_hsv(cls, h: float, s: float, v: float) -> 'Color':
        """
        Create Color from HSV values.

        Args:
            h: Hue (0-360 degrees)
            s: Saturation (0-100 percent)
            v: Value/Brightness (0-100 percent)

        Returns:
            New Color object

        Example:
            >>> red: Color = Color.from_hsv(0, 100, 100)
            >>> print(red.hex)
            '#FF0000'
        """
        rgb: tuple[int, int, int] = hsv_to_rgb(h, s, v)
        return cls(rgb)

    @classmethod
    def from_cmyk(cls, c: float, m: float, y: float, k: float) -> 'Color':
        """
        Create Color from CMYK values.

        Args:
            c: Cyan (0-100 percent)
            m: Magenta (0-100 percent)
            y: Yellow (0-100 percent)
            k: Black (0-100 percent)

        Returns:
            New Color object

        Example:
            >>> red: Color = Color.from_cmyk(0, 100, 100, 0)
            >>> print(red.hex)
            '#FF0000'
        """
        rgb: tuple[int, int, int] = cmyk_to_rgb(c, m, y, k)
        return cls(rgb)

    @classmethod
    def random(cls) -> 'Color':
        """
        Generate a random color with random RGB values.

        Returns:
            New Color object with random RGB values (0-255 each)

        Example:
            >>> random_color: Color = Color.random()
            >>> print(random_color.hex)
            '#A3B7C9' # Example output will vary
        """
        import random
        return cls((random.randint(a=0, b=255), random.randint(a=0, b=255), random.randint(a=0, b=255)))

    def __str__(self) -> str:
        """String representation showing hex value."""
        return "Color(" + self.hex + ")"

    def __repr__(self) -> str:
        """Detailed string representation showing RGB and hex values."""
        return "Color(rgb=(" + str(self._r) + ", " + str(self._g) + ", " + str(self._b) + "), hex='" + self.hex + "')"

    def __eq__(self, other: object) -> bool:
        """Equality comparison based on RGB values."""
        return isinstance(other, Color) and (self.rgb == other.rgb)

    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries."""
        return hash(self.rgb)
