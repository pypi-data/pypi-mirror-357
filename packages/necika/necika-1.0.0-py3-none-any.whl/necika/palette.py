# SPDX-FileCopyrightText: 2023 CELESTIFYX Team
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Color palette generation and management.
"""

import random

from cffi.model import UnionType

from necika.color import Color

ColorType: UnionType = str | tuple[int, int, int] | Color

class ColorPalette:
    """
    A collection of colors with palette generation capabilities.
    """
    def __init__(self, colors: list[str | tuple[int, int, int] | Color] | None = None) -> None:
        """
        Initialize a color palette.

        Args:
            colors: List of colors to include in palette
        """
        self._colors: list[Color] = [c if isinstance(c, Color) else Color(c) for c in colors] if colors else []

    @property
    def colors(self) -> list[Color]:
        """Get a list of colors in the palette."""
        return self._colors.copy()

    @property
    def size(self) -> int:
        """Get number of colors in palette."""
        return len(self._colors)

    def add_color(self, color: ColorType) -> None:
        """
        Add a color to the palette.

        Args:
            color: Color to add
        """
        if not isinstance(color, Color):
            color: Color = Color(color)

        self._colors.append(color)

    def remove_color(self, index: int) -> Color:
        """
        Remove a color from the palette by index.

        Args:
            index: Index of color to remove

        Returns:
            Removed Color object

        Raises:
            IndexError: If index is out of range
        """
        if not 0 <= index < len(self._colors):
            raise IndexError("Color index " + str(index) + " out of range")

        return self._colors.pop(index)

    def clear(self) -> None:
        """Remove all colors from palette."""
        self._colors.clear()

    def get_dominant_color(self) -> Color | None:
        """
        Get the most dominant color (first color if available).

        Returns:
            Dominant Color object or None if palette is empty
        """
        return self._colors[0] if self._colors else None

    def get_lightest(self) -> Color | None:
        """
        Get the lightest color in the palette.

        Returns:
            Lightest Color object or None if palette is empty
        """
        return None if not self._colors else max(self._colors, key=lambda c: c.luminance)

    def get_darkest(self) -> Color | None:
        """
        Get the darkest color in the palette.

        Returns:
            Darkest Color object or None if palette is empty
        """
        return None if not self._colors else min(self._colors, key=lambda c: c.luminance)

    def get_most_saturated(self) -> Color | None:
        """
        Get the most saturated color in the palette.

        Returns:
            Most saturated Color object or None if palette is empty
        """
        return None if not self._colors else max(self._colors, key=lambda c: c.hsl[1])

    def sort_by_hue(self) -> None:
        """Sort colors by hue."""
        self._colors.sort(key=lambda c: c.hsl[0])

    def sort_by_lightness(self) -> None:
        """Sort colors by lightness."""
        self._colors.sort(key=lambda c: c.hsl[2])

    def sort_by_saturation(self) -> None:
        """Sort colors by saturation."""
        self._colors.sort(key=lambda c: c.hsl[1])

    def sort_by_luminance(self) -> None:
        """Sort colors by luminance."""
        self._colors.sort(key=lambda c: c.luminance)

    def to_hex_list(self) -> list[str]:
        """
        Get a list of hex color strings.

        Returns:
            list of hex color strings
        """
        return [color.hex for color in self._colors]

    def to_rgb_list(self) -> list[tuple[int, int, int]]:
        """
        Get a list of RGB tuples.

        Returns:
            list of RGB tuples
        """
        return [color.rgb for color in self._colors]

    @classmethod
    def monochromatic(cls, base_color: ColorType, count: int = 5) -> 'ColorPalette':
        """
        Generate a monochromatic color palette.

        Args:
            base_color: Base color for the palette
            count: Number of colors to generate

        Returns:
            New ColorPalette object
        """
        if not isinstance(base_color, Color):
            base_color: Color = Color(base_color)

        palette: ColorPalette = cls()
        (h, s, l) = base_color.hsl

        # Generate colors with varying lightness
        for i in range(count):
            lightness: float = 20 + (60 * i / (count - 1)) if count > 1 else l
            palette.add_color(Color.from_hsl(h, s, lightness))

        return palette

    @classmethod
    def analogous(cls, base_color: ColorType, count: int = 5, angle: float = 30) -> 'ColorPalette':
        """
        Generate an analogous color palette.

        Args:
            base_color: Base color for the palette
            count: Number of colors to generate
            angle: Angle range for analogous colors

        Returns:
            New ColorPalette object
        """
        if not isinstance(base_color, Color):
            base_color = Color(base_color)

        palette: ColorPalette = cls()
        (h, s, l) = base_color.hsl

        # Generate colors with varying hues around the base
        for i in range(count):
            hue_offset: float | int = 0 if count == 1 else (-angle + (2 * angle * i / (count - 1)))
            new_hue: float = (h + hue_offset) % 360

            palette.add_color(Color.from_hsl(new_hue, s, l))

        return palette

    @classmethod
    def complementary(cls, base_color: ColorType) -> 'ColorPalette':
        """
        Generate a complementary color palette.

        Args:
            base_color: Base color for the palette

        Returns:
            New ColorPalette object with base and complementary colors
        """
        if not isinstance(base_color, Color):
            base_color: Color = Color(base_color)

        palette: ColorPalette = cls()
        palette.add_color(base_color)
        palette.add_color(base_color.complement())

        return palette

    @classmethod
    def triadic(cls, base_color: ColorType) -> 'ColorPalette':
        """
        Generate a triadic color palette.

        Args:
            base_color: Base color for the palette

        Returns:
            New ColorPalette object with triadic colors
        """
        if not isinstance(base_color, Color):
            base_color: Color = Color(base_color)

        palette: ColorPalette = cls()
        palette.add_color(base_color)

        triadic_colors: tuple[Color, Color] = base_color.triadic()
        palette.add_color(triadic_colors[0])
        palette.add_color(triadic_colors[1])

        return palette

    @classmethod
    def tetradic(cls, base_color: ColorType) -> 'ColorPalette':
        """
        Generate a tetradic color palette.

        Args:
            base_color: Base color for the palette

        Returns:
            New ColorPalette object with tetradic colors
        """
        if not isinstance(base_color, Color):
            base_color: Color = Color(base_color)

        palette: ColorPalette = cls()
        palette.add_color(base_color)

        tetradic_colors: tuple[Color, Color, Color] = base_color.tetradic()

        for color in tetradic_colors:
            palette.add_color(color)

        return palette

    @classmethod
    def split_complementary(cls, base_color: ColorType) -> 'ColorPalette':
        """
        Generate a split complementary color palette.

        Args:
            base_color: Base color for the palette

        Returns:
            New ColorPalette object with split complementary colors
        """
        if not isinstance(base_color, Color):
            base_color: Color = Color(base_color)

        palette: ColorPalette = cls()
        palette.add_color(base_color)

        split_colors: tuple[Color, Color] = base_color.split_complementary()
        palette.add_color(split_colors[0])
        palette.add_color(split_colors[1])

        return palette

    @classmethod
    def random(cls, count: int = 5, saturation_range: tuple[float, float] = (30, 90), lightness_range: tuple[float, float] = (30, 70)) -> 'ColorPalette':
        """
        Generate a random color palette.

        Args:
            count: Number of colors to generate
            saturation_range: Range for saturation values (0-100)
            lightness_range: Range for lightness values (0-100)

        Returns:
            New ColorPalette object with random colors
        """
        palette: ColorPalette = cls()

        for _ in range(count):
            h: float = random.uniform(a=0, b=360)
            s: float = random.uniform(*saturation_range)
            l: float = random.uniform(*lightness_range)

            palette.add_color(Color.from_hsl(h, s, l))

        return palette

    @classmethod
    def gradient(cls, start_color: ColorType, end_color: ColorType, steps: int = 5) -> 'ColorPalette':
        """
        Generate a gradient color palette between two colors.

        Args:
            start_color: Starting color
            end_color: Ending color
            steps: Number of steps in gradient

        Returns:
            New ColorPalette object with gradient colors
        """
        if not isinstance(start_color, Color):
            start_color: Color = Color(start_color)

        if not isinstance(end_color, Color):
            end_color: Color = Color(end_color)

        palette: ColorPalette = cls()

        for i in range(steps):
            ratio: float | int = i / (steps - 1) if steps > 1 else 0
            blended: Color = start_color.blend(end_color, ratio)

            palette.add_color(blended)

        return palette
    
    @classmethod
    def material_design(cls, base_color: ColorType) -> 'ColorPalette':
        """
        Generate a Material Design inspired color palette.

        Args:
            base_color: Base color for the palette

        Returns:
            New ColorPalette object with Material Design colors
        """
        if not isinstance(base_color, Color):
            base_color: Color = Color(base_color)

        palette: ColorPalette = cls()
        (h, s, l) = base_color.hsl

        # Material Design color weights
        lightness_values: list[int] = [95, 90, 80, 70, 60, 50, 40, 30, 20, 10]

        for lightness in lightness_values:
            # Adjust saturation based on lightness for better visual balance
            adjusted_s: float = s * (0.7 if lightness > 80 else 1.0)
            palette.add_color(Color.from_hsl(h, adjusted_s, lightness))

        return palette

    def __len__(self) -> int:
        """Get number of colors in palette."""
        return len(self._colors)

    def __getitem__(self, index: int) -> Color:
        """Get color by index."""
        return self._colors[index]

    def __iter__(self):
        """Iterate over colors in palette."""
        return iter(self._colors)

    def __str__(self) -> str:
        """String representation."""
        return "ColorPalette(" + str(len(self._colors)) + " colors)"

    def __repr__(self) -> str:
        """Detailed string representation."""
        colors_repr: list[str] = [color.hex for color in self._colors[:3]]

        if len(self._colors) > 3:
            colors_repr.append("... +" + str(len(self._colors) - 3) + " more")

        return "ColorPalette([" + ', '.join(colors_repr) + "])"
