"""
Happy Frog - Script Parser Package

This package provides parsing and encoding functionality for Happy Frog Script,
an educational scripting language for HID emulation on microcontrollers.

Educational Purpose: This demonstrates language parsing, code generation,
and microcontroller programming concepts.

Author: Happy Frog Team
License: MIT
"""

from .parser import (
    HappyFrogParser,
    HappyFrogScript,
    HappyFrogCommand,
    CommandType,
    HappyFrogScriptError
)

from .encoder import (
    CircuitPythonEncoder,
    EncoderError
)

__version__ = "1.0.0"
__author__ = "Happy Frog Team"
__license__ = "MIT"

__all__ = [
    # Parser classes
    "HappyFrogParser",
    "HappyFrogScript", 
    "HappyFrogCommand",
    "CommandType",
    "HappyFrogScriptError",
    
    # Encoder classes
    "CircuitPythonEncoder",
    "EncoderError",
] 