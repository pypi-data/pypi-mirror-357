# SPDX-FileCopyrightText: 2023 CELESTIFYX Team
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Utility functions for color conversions and manipulations.

This module provides low-level color conversion functions and utilities that
power the Color class. It includes conversions between different color spaces,
color analysis functions, and blending operations.

Color Space Conversions:
- RGB ↔ Hex
- RGB ↔ HSL (Hue, Saturation, Lightness)
- RGB ↔ HSV (Hue, Saturation, Value)
- RGB ↔ CMYK (Cyan, Magenta, Yellow, Black)

Color Analysis:
- Luminance calculation (WCAG standard)
- Contrast ratio calculation
- Light/dark color detection

Color Operations:
- Color blending/mixing
- Color validation

Examples:
    Basic conversions:
    >>> from necika.utils import hex_to_rgb, rgb_to_hex

    >>> rgb: tuple[int, int, int] = hex_to_rgb('#FF0000') # (255, 0, 0)
    >>> hex_color: str = rgb_to_hex(255, 0, 0) # '#FF0000'

    Color space conversions:
    >>> from necika.utils import rgb_to_hsl, hsl_to_rgb

    >>> hsl: tuple[float, float, float] = rgb_to_hsl(255, 0, 0) # (0.0, 100.0, 50.0)
    >>> rgb: tuple[int, int, int] = hsl_to_rgb(0, 100, 50) # (255, 0, 0)

    Color analysis:
    >>> from necika.utils import calculate_luminance, calculate_contrast_ratio

    >>> luminance: float = calculate_luminance(255, 255, 255) # 1.0 (white)
    >>> contrast:  float = calculate_contrast_ratio((0, 0, 0), (255, 255, 255)) # 21.0
"""

import re

from necika.exceptions import (InvalidColorError, ColorConversionError)

def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """
    Convert hexadecimal color to RGB tuple.

    Supports various hex formats:
    - Full hex with hash: '#FF0000'
    - Full hex without hash: 'FF0000'
    - Short hex with hash: '#F00'
    - Short hex without hash: 'F00'
    - Case insensitive: '#ff0000' or '#FF0000'

    Args:
        hex_color: Hex color string in supported formats

    Returns:
        RGB tuple (r, g, b) with values 0-255

    Raises:
        InvalidColorError: If a hex color format is invalid

    Examples:
        >>> hex_to_rgb('#FF0000')
        (255, 0, 0)
        >>> hex_to_rgb('F00')
        (255, 0, 0)
        >>> hex_to_rgb('#00FF00')
        (0, 255, 0)
    """
    # Remove '#' if present and convert to uppercase
    hex_color: str = hex_color.lstrip('#').upper()

    # Handle 3-digit hex (e.g., 'F00' -> 'FF0000')
    if len(hex_color) == 3:
        hex_color: str = ''.join([c * 2 for c in hex_color])

    # Validate hex format
    if not re.match(pattern=r'^[0-9A-F]{6}$', string=hex_color):
        raise InvalidColorError(hex_color, message="Invalid hex color format")

    try:
        r: int = int(hex_color[0:2], 16)
        g: int = int(hex_color[2:4], 16)
        b: int = int(hex_color[4:6], 16)

        return r, g, b
    except ValueError as e:
        raise ColorConversionError(from_format="hex", to_format="rgb", value=hex_color) from e

def rgb_to_hex(r: int, g: int, b: int) -> str:
    """
    Convert RGB values to hexadecimal color string.

    Args:
        r: Red component (0-255)
        g: Green component (0-255)
        b: Blue component (0-255)

    Returns:
        Hex color string with '#' prefix (e.g., '#FF0000')

    Raises:
        InvalidColorError: If RGB values are out of valid range

    Examples:
        >>> rgb_to_hex(255, 0, 0)
        '#FF0000'
        >>> rgb_to_hex(0, 255, 0)
        '#00FF00'
        >>> rgb_to_hex(128, 128, 128)
        '#808080'
    """
    # Validate RGB values
    for (component, value) in [('r', r), ('g', g), ('b', b)]:
        if not isinstance(value, int) or not 0 <= value <= 255:
            raise InvalidColorError("RGB(" + str(r) + ", " + str(g) + ", " + str(b) + ")", component + " value " + str(value) + " must be 0-255")

    return "#{r:02X}{g:02X}{b:02X}".format(r=r, g=g, b=b)

def rgb_to_hsl(r: int, g: int, b: int) -> tuple[float, float, float]:
    """
    Convert RGB to HSL color space.

    HSL (Hue, Saturation, Lightness) is a cylindrical color space that's more
    intuitive for color manipulation than RGB. Hue represents the color type,
    saturation represents the intensity, and lightness represents brightness.

    Args:
        r: Red component (0-255)
        g: Green component (0-255)
        b: Blue component (0-255)

    Returns:
        HSL tuple where:
        - h (hue): 0-360 degrees
        - s (saturation): 0-100 percent
        - l (lightness): 0-100 percent

    Examples:
        >>> rgb_to_hsl(255, 0, 0) # Pure red
        (0.0, 100.0, 50.0)
        >>> rgb_to_hsl(0, 255, 0) # Pure green
        (120.0, 100.0, 50.0)
        >>> rgb_to_hsl(128, 128, 128) # Gray
        (0.0, 0.0, 50.2)
    """
    # Normalize RGB values to 0-1
    (r_norm, g_norm, b_norm) = (r / 255.0, g / 255.0, b / 255.0)

    max_val: float = max(r_norm, g_norm, b_norm)
    min_val: float = min(r_norm, g_norm, b_norm)
    diff:    float = max_val - min_val

    # Lightness calculation
    l: float = (max_val + min_val) / 2

    # Handle an achromatic case (no color)
    if diff == 0:
        return 0.0, 0.0, l * 100

    # Saturation calculation
    s: float = (diff / (2 - max_val - min_val)) if l > 0.5 else (diff / (max_val + min_val))

    # Hue calculation using color-specific formulas
    hue_calculators: dict[float, ...] = {
        r_norm: lambda: (g_norm - b_norm) / diff + (6 if g_norm < b_norm else 0),
        g_norm: lambda: (b_norm - r_norm) / diff + 2,
        b_norm: lambda: (r_norm - g_norm) / diff + 4
    }

    h: float = hue_calculators[max_val]() / 6
    return h * 360, s * 100, l * 100

def hsl_to_rgb(h: float, s: float, l: float) -> tuple[int, int, int]:
    """
    Convert HSL to RGB color space.

    Converts from HSL (Hue, Saturation, Lightness) back to RGB values.
    This is the inverse operation of rgb_to_hsl().

    Args:
        h: Hue (0-360 degrees)
        s: Saturation (0-100 percent)
        l: Lightness (0-100 percent)

    Returns:
        RGB tuple (r, g, b) with values 0-255

    Examples:
        >>> hsl_to_rgb(0, 100, 50) # Pure red
        (255, 0, 0)
        >>> hsl_to_rgb(120, 100, 50) # Pure green
        (0, 255, 0)
        >>> hsl_to_rgb(0, 0, 50) # Gray
        (128, 128, 128)
    """
    # Normalize values to 0-1 range
    h_norm: float = h / 360.0
    s_norm: float = s / 100.0
    l_norm: float = l / 100.0

    def hue_to_rgb(p_value: float, q_value: float, t_val: float) -> float:
        """Convert hue to an RGB component using HSL algorithm."""
        # Normalize hue to 0-1 range
        t_val: float = (t_val + 1) % 1 if t_val < 0 else (t_val % 1 if t_val > 1 else t_val)

        # Apply HSL to RGB conversion formula
        hue_ranges: list[tuple[..., ...]] = [
            (1 / 6, lambda: p_value + (q_value - p_value) * 6 * t_val),
            (1 / 2, lambda: q_value),
            (2 / 3, lambda: p_value + (q_value - p_value) * (2 / 3 - t_val) * 6)
        ]

        for (threshold, calculator) in hue_ranges:
            if t_val < threshold:
                return calculator()

        return p_value

    # Handle an achromatic case (no saturation)
    if s_norm == 0:
        return round(l_norm * 255), round(l_norm * 255), round(l_norm * 255)

    # Calculate intermediate values for chromatic colors
    q_val: float = l_norm * (1 + s_norm) if l_norm < 0.5 else l_norm + s_norm - l_norm * s_norm
    p_val: float = 2 * l_norm - q_val

    # Calculate RGB components
    r: float = hue_to_rgb(p_val, q_val, h_norm + 1 / 3)
    g: float = hue_to_rgb(p_val, q_val, h_norm)
    b: float = hue_to_rgb(p_val, q_val, h_norm - 1 / 3)

    return round(r * 255), round(g * 255), round(b * 255)

def rgb_to_hsv(r: int, g: int, b: int) -> tuple[float, float, float]:
    """
    Convert RGB to HSV color space.

    HSV (Hue, Saturation, Value) is another cylindrical color space similar to HSL
    but with different saturation and brightness calculations. Value represents
    the brightness of the color.

    Args:
        r: Red component (0-255)
        g: Green component (0-255)
        b: Blue component (0-255)

    Returns:
        HSV tuple where:
        - h (hue): 0-360 degrees
        - s (saturation): 0-100 percent
        - v (value): 0-100 percent

    Examples:
        >>> rgb_to_hsv(255, 0, 0) # Pure red
        (0.0, 100.0, 100.0)
        >>> rgb_to_hsv(255, 128, 0) # Orange
        (30.1, 100.0, 100.0)
    """
    (r_norm, g_norm, b_norm) = (r / 255.0, g / 255.0, b / 255.0)

    max_val: float = max(r_norm, g_norm, b_norm)
    min_val: float = min(r_norm, g_norm, b_norm)
    diff:    float = max_val - min_val

    # Saturation calculation
    s: float | int = 0 if max_val == 0 else diff / max_val

    # Hue calculation using component-specific formulas
    h: float | int = 0 if diff == 0 else [
        lambda: (60 * ((g_norm - b_norm) / diff) + 360) % 360,
        lambda: (60 * ((b_norm - r_norm) / diff) + 120) % 360,
        lambda: (60 * ((r_norm - g_norm) / diff) + 240) % 360
    ][[r_norm, g_norm, b_norm].index(max_val)]()

    return h, s * 100, max_val * 100

def hsv_to_rgb(h: float, s: float, v: float) -> tuple[int, int, int]:
    """
    Convert HSV to RGB color space.

    Converts from HSV (Hue, Saturation, Value) back to RGB values.
    This is the inverse operation of rgb_to_hsv().

    Args:
        h: Hue (0-360 degrees)
        s: Saturation (0-100 percent)
        v: Value/Brightness (0-100 percent)

    Returns:
        RGB tuple (r, g, b) with values 0-255

    Examples:
        >>> hsv_to_rgb(0, 100, 100) # Pure red
        (255, 0, 0)
        >>> hsv_to_rgb(60, 100, 100) # Yellow
        (255, 255, 0)
    """
    h_norm: float = h / 60.0
    s_norm: float = s / 100.0
    v_norm: float = v / 100.0

    c: float = v_norm * s_norm  # Chroma
    x: float = c * (1 - abs((h_norm % 2) - 1))  # Intermediate value
    m: float = v_norm - c  # Match value

    # RGB values based on hue sector (0-5)
    rgb_sectors: list[tuple[float, float, float]] = [
        (c, x, 0),  # 0-60°: Red to Yellow
        (x, c, 0),  # 60-120°: Yellow to Green
        (0, c, x),  # 120-180°: Green to Cyan
        (0, x, c),  # 180-240°: Cyan to Blue
        (x, 0, c),  # 240-300°: Blue to Magenta
        (c, 0, x)   # 300-360°: Magenta to Red
    ]

    sector_index: int = int(h_norm) % 6
    (r_prime, g_prime, b_prime) = rgb_sectors[sector_index]

    # Add match value and convert to 0-255 range
    r_final: int = round((r_prime + m) * 255)
    g_final: int = round((g_prime + m) * 255)
    b_final: int = round((b_prime + m) * 255)

    return r_final, g_final, b_final

def rgb_to_cmyk(r: int, g: int, b: int) -> tuple[float, float, float, float]:
    """
    Convert RGB to CMYK color space.

    CMYK (Cyan, Magenta, Yellow, Black) is a subtractive color model used
    primarily in printing. This conversion is approximate since RGB (additive)
    and CMYK (subtractive) have different color gamuts.

    Args:
        r: Red component (0-255)
        g: Green component (0-255)
        b: Blue component (0-255)

    Returns:
        CMYK tuple (c, m, y, k) with values 0-100 percent

    Examples:
        >>> rgb_to_cmyk(255, 0, 0) # Pure red
        (0.0, 100.0, 100.0, 0.0)
        >>> rgb_to_cmyk(0, 0, 0) # Black
        (0.0, 0.0, 0.0, 100.0)
    """
    # Normalize RGB values to 0-1
    (r_norm, g_norm, b_norm) = (r / 255.0, g / 255.0, b / 255.0)

    # Calculate K (black) component
    k: float = 1 - max(r_norm, g_norm, b_norm)

    # Handle a pure black case
    if k == 1:
        return 0.0, 0.0, 0.0, 100.0

    # Calculate CMY components
    c: float = (1 - r_norm - k) / (1 - k)
    m: float = (1 - g_norm - k) / (1 - k)
    y: float = (1 - b_norm - k) / (1 - k)

    return c * 100, m * 100, y * 100, k * 100

def cmyk_to_rgb(c: float, m: float, y: float, k: float) -> tuple[int, int, int]:
    """
    Convert CMYK to RGB color space.

    Converts from CMYK (Cyan, Magenta, Yellow, Black) back to RGB values.
    This conversion is approximate due to different color gamuts.

    Args:
        c: Cyan component (0-100 percent)
        m: Magenta component (0-100 percent)
        y: Yellow component (0-100 percent)
        k: Black component (0-100 percent)

    Returns:
        RGB tuple (r, g, b) with values 0-255

    Examples:
        >>> cmyk_to_rgb(0, 100, 100, 0) # Should be red
        (255, 0, 0)
        >>> cmyk_to_rgb(0, 0, 0, 100) # Black
        (0, 0, 0)
    """
    # Normalize CMYK values to 0-1
    (c_norm, m_norm, y_norm, k_norm) = (c / 100.0, m / 100.0, y / 100.0, k / 100.0)

    # Convert to RGB using CMYK formula
    r: float = 255 * (1 - c_norm) * (1 - k_norm)
    g: float = 255 * (1 - m_norm) * (1 - k_norm)
    b: float = 255 * (1 - y_norm) * (1 - k_norm)

    return round(r), round(g), round(b)

def calculate_luminance(r: int, g: int, b: int) -> float:
    """
    Calculate the relative luminance of a color according to WCAG 2.1 guidelines.

    Relative luminance is the relative brightness of any point in a colorspace,
    normalized to 0 for the darkest black and 1 for the lightest white. This calculation
    follows the WCAG 2.1 specification for accessibility compliance.

    Args:
        r: Red component (0-255)
        g: Green component (0-255)
        b: Blue component (0-255)

    Returns:
        Relative luminance (0.0 = darkest black, 1.0 = lightest white)

    Note:
        This function is used for calculating contrast ratios and determining
        if colors meet accessibility standards.

    Examples:
        >>> calculate_luminance(255, 255, 255) # White
        1.0
        >>> calculate_luminance(0, 0, 0) # Black
        0.0
        >>> calculate_luminance(255, 0, 0) # Red
        0.2126
    """
    def linearize(component: float) -> float:
        """Convert sRGB component to linear RGB."""
        return (component / 12.92) if component <= 0.03928 else pow((component + 0.055) / 1.055, 2.4)

    # Normalize and linearize RGB components
    r_lin: float = linearize(r / 255.0)
    g_lin: float = linearize(g / 255.0)
    b_lin: float = linearize(b / 255.0)

    # Apply WCAG luminance formula with standard coefficients
    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin

def calculate_contrast_ratio(color1: tuple[int, int, int], color2: tuple[int, int, int]) -> float:
    """
    Calculate the contrast ratio between two colors according to WCAG guidelines.

    The contrast ratio is used to determine if color combinations provide
    sufficient contrast for accessibility. WCAG defines minimum contrast ratios
    for different compliance levels.

    Args:
        color1: First color as RGB tuple (r, g, b)
        color2: Second color as RGB tuple (r, g, b)

    Returns:
        Contrast ratio (1.0 = no contrast, 21.0 = maximum contrast)

    Note:
        - WCAG AA requires a contrast ratio of at least 4.5:1
        - WCAG AAA requires a contrast ratio of at least 7:1
        - The ratio is always >= 1.0 and is symmetric (order doesn't matter)

    Examples:
        >>> calculate_contrast_ratio((0, 0, 0), (255, 255, 255)) # Black vs. White
        21.0
        >>> calculate_contrast_ratio((128, 128, 128), (128, 128, 128)) # Same color
        1.0
    """
    lum1: float = calculate_luminance(*color1)
    lum2: float = calculate_luminance(*color2)

    # Ensure lighter color is in numerator for consistent results
    (lighter, darker) = (lum1, lum2) if lum1 > lum2 else (lum2, lum1)
    return (lighter + 0.05) / (darker + 0.05)

def is_light_color(r: int, g: int, b: int, threshold: float = 0.5) -> bool:
    """
    Determine if a color is light or dark based on its luminance.

    This function is useful for automatically choosing appropriate text colors
    (dark text on light backgrounds, light text on dark backgrounds).

    Args:
        r: Red component (0-255)
        g: Green component (0-255)
        b: Blue component (0-255)
        threshold: Luminance threshold (0.0-1.0, default 0.5)

    Returns:
        True if color is considered light, False if dark

    Examples:
        >>> is_light_color(255, 255, 255) # White
        True
        >>> is_light_color(0, 0, 0) # Black
        False
        >>> is_light_color(128, 128, 128) # Gray
        True # Depends on a threshold
    """
    luminance: float = calculate_luminance(r, g, b)
    return luminance > threshold

def blend_colors(color1: tuple[int, int, int], color2: tuple[int, int, int], ratio: float = 0.5) -> tuple[int, int, int]:
    """
    Blend two colors using linear interpolation in RGB space.

    This function creates a smooth transition between two colors by mixing
    their RGB components according to the specified ratio.

    Args:
        color1: First color as RGB tuple (r, g, b)
        color2: Second color as RGB tuple (r, g, b)
        ratio: Blend ratio (0.0 = color1, 1.0 = color2, 0.5 = 50/50 mix)

    Returns:
        Blended RGB tuple (r, g, b)

    Raises:
        InvalidColorError: If a ratio is not between 0.0 and 1.0

    Examples:
        >>> blend_colors((255, 0, 0), (0, 0, 255), 0.5)  # Red + Blue = Purple
        (128, 0, 128)
        >>> blend_colors((255, 0, 0), (0, 255, 0), 0.25)  # 75% Red, 25% Green
        (191, 64, 0)
    """
    if not 0 <= ratio <= 1:
        raise InvalidColorError(ratio, message="Blend ratio must be between 0 and 1")

    (r1, g1, b1) = color1
    (r2, g2, b2) = color2

    # Linear interpolation for each component
    r: int = round(r1 * (1 - ratio) + r2 * ratio)
    g: int = round(g1 * (1 - ratio) + g2 * ratio)
    b: int = round(b1 * (1 - ratio) + b2 * ratio)

    return r, g, b
