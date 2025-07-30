# SPDX-FileCopyrightText: 2023 CELESTIFYX Team
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Custom exceptions for the Necika library.
"""

from typing import Any

class ColorError(Exception):
    """Base exception class for all color-related errors."""
    pass

class InvalidColorError(ColorError):
    """Raised when an invalid color value is provided."""
    def __init__(self, color_value: Any, message: str | None = None) -> None:
        self.color_value: Any = color_value

        if message is None:
            message = "Invalid color value: " + str(color_value)

        super().__init__(message)

class ColorConversionError(ColorError):
    """Raised when color conversion fails."""
    def __init__(self, from_format: str, to_format: str, value: Any, message: str | None = None) -> None:
        self.from_format: str = from_format
        self.to_format: str = to_format
        self.value: Any = value

        if message is None:
            message = "Failed to convert " + str(value) + " from " + from_format + " to " + to_format

        super().__init__(message)

class ColorRangeError(ColorError):
    """Raised when color values are out of valid range."""
    def __init__(self, component: str, value: Any, valid_range: tuple[int, int], message: str | None = None) -> None:
        self.component: str = component
        self.value: Any = value
        self.valid_range: tuple[int, int] = valid_range

        if message is None:
            message = component + " value " + str(value) + " is out of range " + str(valid_range)

        super().__init__(message)
