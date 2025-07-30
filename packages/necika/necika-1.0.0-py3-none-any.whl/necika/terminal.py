# SPDX-FileCopyrightText: 2023 CELESTIFYX Team
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Terminal color output with ANSI escape codes.

This module provides comprehensive terminal color functionality including:
- Basic and bright ANSI colors
- Custom RGB colors (24-bit color support)
- Text styling (bold, italic, underline, etc.)
- Background colors
- Special effects (rainbow, gradient)
- Message type formatting (success, warning, error, info)
- Automatic color support detection

Examples:
    Basic usage:
        >>> from necika import TerminalColor
        >>> terminal_color: TerminalColor = TerminalColor()

        >>> print(terminal_color.red("This is red text"))
        >>> print(terminal_color.success("✓ Operation completed"))

    Advanced usage:
        >>> from necika import Color
        >>> custom_color: Color = Color('#FF6B35')

        >>> print(terminal_color.colored("Custom color", custom_color))
        >>> print(terminal_color.gradient_text("Gradient", '#FF0000', '#0000FF'))
"""

import sys

from typing import (Any, TextIO)

from necika.color import Color
from necika.constants import (ANSI_COLORS, ANSI_BG_COLORS, ANSI_STYLES)

ColorType = str | Color

class TerminalColor:
    """
    Terminal color output using ANSI escape codes.

    Provides methods for colored text output, background colors, text styling,
    and special effects in terminal environments. Automatically detects terminal
    color support and gracefully degrades when colors are not supported.

    Features:
    - Basic ANSI colors (red, green, blue, etc.)
    - Custom RGB colors (24-bit color support)
    - Background colors
    - Text styles (bold, italic, underline, strikethrough)
    - Message types (success, warning, error, info)
    - Special effects (rainbow, gradient)
    - Automatic color support detection

    Examples:
        Basic colors:
            >>> terminal_color: TerminalColor = TerminalColor()
            >>> print(terminal_color.red("Red text"))
            >>> print(terminal_color.green("Green text"))

        Custom colors:
            >>> custom: Color = Color('#FF6B35')
            >>> print(terminal_color.colored("Orange text", custom))

        With backgrounds and styles:
            >>> print(terminal_color.colored("Styled", "white", background="red", style="bold"))

        Message types:
            >>> print(terminal_color.success("✓ Success"))
            >>> print(terminal_color.error("✗ Error"))

        Special effects:
            >>> print(terminal_color.rainbow("Rainbow text"))
            >>> print(terminal_color.gradient_text("Gradient", '#FF0000', '#0000FF'))
    """
    def __init__(self, auto_detect: bool = True) -> None:
        """
        Initialize TerminalColor with optional color support detection.

        Args:
            auto_detect: Automatically detect terminal color support (default True)
                        If False, assumes color support is available
        """
        self.color_support: bool = self._detect_color_support() if auto_detect else True

    def _detect_color_support(self) -> bool:
        """
        Detect if the terminal supports color output.

        Checks various indicators to determine if the terminal can display colors:
        - Platform-specific checks (Windows ANSI support)
        - Environment variables (ANSICON, WT_SESSION)
        - TTY detection

        Returns:
            True if color is supported, False otherwise
        """
        # Platform-specific color support detection
        color_detection_strategies: dict[str, ...] = {
            'win32':   self._detect_windows_color_support,
            'default': self._detect_unix_color_support
        }

        strategy: Any = color_detection_strategies.get(sys.platform, color_detection_strategies['default'])
        return strategy()

    @staticmethod
    def _detect_windows_color_support() -> bool:
        """Detect color support on Windows systems."""
        import os

        # Windows 10+ supports ANSI colors, check for common indicators
        return any(key in os.environ for key in {'ANSICON', 'WT_SESSION', 'TERM'})

    @staticmethod
    def _detect_unix_color_support() -> bool:
        """Detect color support on Unix-like systems."""
        # Unix-like systems usually support colors if connected to a TTY
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

    def _format_ansi(self, text: str, *codes: int) -> str:
        """
        Format text with ANSI escape codes.

        Args:
            text: Text to format
            *codes: ANSI codes to apply

        Returns:
            Formatted text string with ANSI codes, or plain text if colors disabled
        """
        if not self.color_support or not codes:
            return text

        start_code: str = "\033[" + ';'.join(map(str, codes)) + "m"
        end_code:   str = "\033[0m"

        return start_code + text + end_code

    def colored(self, text: str, color: ColorType, background: ColorType | None = None, style: str | None = None) -> str:
        """
        Apply color, background, and style to text.

        This is the main method for applying colors and styles to text. It supports
        various color formats and can combine foreground colors, background colors,
        and text styles.

        Args:
            text: Text to colorize
            color: Foreground color (ANSI color name, hex string, or Color object)
            background: Background color (optional, same formats as color)
            style: Text style ('bold', 'italic', 'underline', 'strikethrough')

        Returns:
            Colored and styled text string

        Examples:
            >>> terminal.colored("Hello", "red")
            >>> terminal.colored("World", "#FF0000")
            >>> terminal.colored("Styled", Color('#00FF00'), background="black", style="bold")
        """
        codes: list[int] = []

        # Style code application
        style_code: int | None = ANSI_STYLES.get(style) if style else None

        if style_code is not None:
            codes.append(style_code)

        # Foreground color application strategies
        fg_codes: list[int] = self._get_color_codes(color, is_background=False)
        codes.extend(fg_codes)

        # Background color application strategies
        if background is not None:
            bg_codes: list[int] = self._get_color_codes(background, is_background=True)
            codes.extend(bg_codes)

        return self._format_ansi(text, *codes)

    def _get_color_codes(self, color: ColorType, is_background: bool = False) -> list[int]:
        """
        Get ANSI codes for a color using a strategy pattern.

        Args:
            color: Color in various formats
            is_background: Whether this is for background color

        Returns:
            List of ANSI codes for the color
        """
        color_strategies: list[...] = [
            self._try_ansi_color,
            self._try_color_object,
            self._try_string_color
        ]

        for strategy in color_strategies:
            codes: list[int] = strategy(color, is_background)

            if codes:
                return codes

        return []

    @staticmethod
    def _try_ansi_color(color: ColorType, is_background: bool) -> list[int]:
        """Try to get codes for ANSI color names."""
        if not isinstance(color, str):
            return []

        color_name: str = color.lower()
        color_map: dict[str, int] = ANSI_BG_COLORS if is_background else ANSI_COLORS

        ansi_code: int | None = color_map.get(color_name)
        return [ansi_code] if ansi_code is not None else []

    @staticmethod
    def _try_color_object(color: ColorType, is_background: bool) -> list[int]:
        """Try to get codes for Color objects."""
        if not isinstance(color, Color):
            return []

        # 24-bit color support (RGB)
        prefix: int = 48 if is_background else 38
        return [prefix, 2] + list(color.rgb)

    @staticmethod
    def _try_string_color(color: ColorType, is_background: bool) -> list[int]:
        """Try to parse string as a Color object."""
        if not isinstance(color, str):
            return []

        # noinspection PyBroadException
        try:
            color_obj: Color = Color(color)
            prefix: int = 48 if is_background else 38

            return [prefix, 2] + list(color_obj.rgb)
        except Exception:
            return []

    def print_colored(self, text: str, color: ColorType, background: ColorType | None = None, style: str | None = None, file: TextIO | None = None, **kwargs: Any) -> None:
        """
        Print-colored text to terminal.

        Convenience method that combines coloring and printing in one call.

        Args:
            text: Text to print
            color: Foreground color
            background: Background color (optional)
            style: Text style (optional)
            file: Output file (default: sys.stdout)
            **kwargs: Additional arguments passed to print()

        Example:
            >>> terminal.print_colored("Hello World", "red", background="yellow")
        """
        colored_text: str = self.colored(text, color, background, style)
        print(colored_text, file=file, **kwargs)

    # Basic color methods with comprehensive documentation
    def red(self, text: str) -> str:
        """Color text red. Equivalent to colored(text, 'red')."""
        return self.colored(text, color='red')

    def green(self, text: str) -> str:
        """Color text green. Equivalent to colored(text, 'green')."""
        return self.colored(text, color='green')

    def blue(self, text: str) -> str:
        """Color text blue. Equivalent to colored(text, 'blue')."""
        return self.colored(text, color='blue')

    def yellow(self, text: str) -> str:
        """Color text yellow. Equivalent to colored(text, 'yellow')."""
        return self.colored(text, color='yellow')

    def magenta(self, text: str) -> str:
        """Color text magenta. Equivalent to colored(text, 'magenta')."""
        return self.colored(text, color='magenta')

    def cyan(self, text: str) -> str:
        """Color text cyan. Equivalent to colored(text, 'cyan')."""
        return self.colored(text, color='cyan')

    def white(self, text: str) -> str:
        """Color text white. Equivalent to colored(text, 'white')."""
        return self.colored(text, color='white')

    def black(self, text: str) -> str:
        """Color text black. Equivalent to colored(text, 'black')."""
        return self.colored(text, color='black')

    # Text style methods
    def bold(self, text: str) -> str:
        """Make text bold. Equivalent to colored(text, 'white', style='bold')."""
        return self.colored(text, color='white', style='bold')

    def italic(self, text: str) -> str:
        """Make text italic. Equivalent to colored(text, 'white', style='italic')."""
        return self.colored(text, color='white', style='italic')

    def underline(self, text: str) -> str:
        """Make text underlined. Equivalent to colored(text, 'white', style='underline')."""
        return self.colored(text, color='white', style='underline')

    def strikethrough(self, text: str) -> str:
        """Make text strikethrough. Equivalent to colored(text, 'white', style='strikethrough')."""
        return self.colored(text, color='white', style='strikethrough')

    # Message type methods with semantic meaning
    def success(self, text: str) -> str:
        """
        Format success message with green color and bold style.

        Args:
            text: Success message text

        Returns:
            Formatted success message

        Example:
            >>> print(terminal.success("✓ Operation completed successfully"))
        """
        return self.colored(text, color='green', style='bold')

    def warning(self, text: str) -> str:
        """
        Format warning message with yellow color and bold style.

        Args:
            text: Warning message text

        Returns:
            Formatted warning message

        Example:
            >>> print(terminal.warning("⚠ This is a warning"))
        """
        return self.colored(text, color='yellow', style='bold')

    def error(self, text: str) -> str:
        """
        Format error message with red color and bold style.

        Args:
            text: Error message text

        Returns:
            Formatted error message

        Example:
            >>> print(terminal.error("✗ An error occurred"))
        """
        return self.colored(text, color='red', style='bold')

    def info(self, text: str) -> str:
        """
        Format info message with blue color and bold style.

        Args:
            text: Info message text

        Returns:
            Formatted info message

        Example:
            >>> print(terminal.info("ℹ This is information"))
        """
        return self.colored(text, color='blue', style='bold')

    def rainbow(self, text: str, colors: list[str] | None = None) -> str:
        """
        Create rainbow-colored text by cycling through colors.

        Each character (excluding spaces) gets a different color from a predefined
        rainbow sequence: red, yellow, green, cyan, blue, magenta.

        Args:
            text: Text to colorize with rainbow effect
            colors: Optional list of color names to use instead of the default rainbow sequence.
                    If None, the default ['red', 'yellow', 'green', 'cyan', 'blue', 'magenta'] is used.

        Returns:
            Rainbow colored text string

        Example:
            >>> print(terminal.rainbow("Hello World!"))
            # Each letter will be a different color
        """
        if not colors:
            colors: list[str] = ['red', 'yellow', 'green', 'cyan', 'blue', 'magenta']

        result: list[str] = []
        color_index: int = 0

        for char in text:
            result.append(char if char.isspace() else self.colored(char, colors[color_index % len(colors)]))
            color_index += not char.isspace()

        return ''.join(result)

    def gradient_text(self, text: str, start_color: ColorType, end_color: ColorType) -> str:
        """
        Create gradient-colored text between two colors.

        Each character transitions smoothly from start_color to end_color using
        linear interpolation in RGB space.

        Args:
            text: Text to apply gradient to
            start_color: Starting color (Color object, hex string, or color name)
            end_color: Ending color (Color object, hex string, or color name)

        Returns:
            Gradient colored text string

        Example:
            >>> gradient: str = terminal.gradient_text("Hello", "#FF0000", "#0000FF")
            >>> print(gradient) # Text transitions from red to blue
        """
        # Convert colors to Color objects
        color_conversion_strategies: list[...] = [
            lambda c: c        if isinstance(c, Color) else None,
            lambda c: Color(c) if isinstance(c, str)   else None
        ]

        start_color_obj: Color | None = None
        end_color_obj:   Color | None = None

        for strategy in color_conversion_strategies:
            # noinspection PyBroadException
            try:
                if start_color_obj is None:
                    start_color_obj = strategy(start_color)

                if end_color_obj is None:
                    end_color_obj = strategy(end_color)

                if start_color_obj and end_color_obj:
                    break

            except Exception:
                continue

        if not (start_color_obj and end_color_obj):
            return text

        result:     list[str] = []
        text_chars: list[str] = [c for c in text if not c.isspace()]

        char_index: int = 0

        for char in text:
            result.append(char if char.isspace() else self.colored(char, start_color_obj.blend(end_color_obj, char_index / (len(text_chars) - 1) if len(text_chars) > 1 else 0)))
            char_index += not char.isspace()

        return ''.join(result)

    def disable_colors(self) -> None:
        """
        Disable color output.

        After calling this method, all color methods will return plain text
        without ANSI escape codes.
        """
        self.color_support = False

    def enable_colors(self) -> None:
        """
        Enable color output.

        Re-enables color output if it was previously disabled.
        """
        self.color_support = True

# Global instance for convenience
terminal: TerminalColor = TerminalColor()
"""
Global TerminalColor instance for convenient access.

This pre-configured instance can be imported and used directly without
creating your own TerminalColor object.

Example:
    >>> from necika.terminal import terminal

    >>> print(terminal.red("Red text"))
    >>> print(terminal.success("Success message"))
"""
