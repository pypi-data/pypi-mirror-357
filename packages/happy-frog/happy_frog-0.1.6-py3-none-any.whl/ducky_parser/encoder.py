"""
Happy Frog - CircuitPython Encoder

This module converts parsed Happy Frog Script commands into CircuitPython code that can
be executed on microcontrollers like the Seeed Xiao RP2040.

Educational Purpose: This demonstrates code generation, microcontroller programming,
and how to translate high-level commands into low-level hardware operations.

Author: Happy Frog Team
License: MIT
"""

from typing import List, Dict, Any, Optional
from .parser import HappyFrogScript, HappyFrogCommand, CommandType


class EncoderError(Exception):
    """Custom exception for encoding errors."""
    pass


class CircuitPythonEncoder:
    """
    Encoder that converts parsed Happy Frog Script commands into CircuitPython code.
    
    This encoder generates human-readable CircuitPython code that can be directly
    uploaded to compatible microcontrollers. It includes educational comments
    to help users understand how each command works.
    """
    
    def __init__(self):
        """Initialize the encoder with key mappings and templates."""
        # USB HID key codes for CircuitPython
        self.key_codes = {
            # Basic keys
            CommandType.ENTER: "Keycode.ENTER",
            CommandType.SPACE: "Keycode.SPACE",
            CommandType.TAB: "Keycode.TAB",
            CommandType.BACKSPACE: "Keycode.BACKSPACE",
            CommandType.DELETE: "Keycode.DELETE",
            
            # Arrow keys
            CommandType.UP: "Keycode.UP_ARROW",
            CommandType.DOWN: "Keycode.DOWN_ARROW",
            CommandType.LEFT: "Keycode.LEFT_ARROW",
            CommandType.RIGHT: "Keycode.RIGHT_ARROW",
            
            # Navigation keys
            CommandType.HOME: "Keycode.HOME",
            CommandType.END: "Keycode.END",
            CommandType.INSERT: "Keycode.INSERT",
            CommandType.PAGE_UP: "Keycode.PAGE_UP",
            CommandType.PAGE_DOWN: "Keycode.PAGE_DOWN",
            CommandType.ESCAPE: "Keycode.ESCAPE",
            
            # Function keys
            CommandType.F1: "Keycode.F1",
            CommandType.F2: "Keycode.F2",
            CommandType.F3: "Keycode.F3",
            CommandType.F4: "Keycode.F4",
            CommandType.F5: "Keycode.F5",
            CommandType.F6: "Keycode.F6",
            CommandType.F7: "Keycode.F7",
            CommandType.F8: "Keycode.F8",
            CommandType.F9: "Keycode.F9",
            CommandType.F10: "Keycode.F10",
            CommandType.F11: "Keycode.F11",
            CommandType.F12: "Keycode.F12",
            
            # Modifier keys
            CommandType.CTRL: "Keycode.CONTROL",
            CommandType.SHIFT: "Keycode.SHIFT",
            CommandType.ALT: "Keycode.ALT",
            CommandType.MOD: "Keycode.GUI",  # MOD maps to GUI (Windows/Command key)
        }
        
        # CircuitPython code templates
        self.templates = {
            'header': self._get_header_template(),
            'footer': self._get_footer_template(),
            'delay': self._get_delay_template(),
            'string': self._get_string_template(),
            'key_press': self._get_key_press_template(),
            'comment': self._get_comment_template(),
        }
    
    def encode(self, script: HappyFrogScript, output_file: Optional[str] = None) -> str:
        """
        Encode a parsed Happy Frog Script into CircuitPython code.
        
        Args:
            script: Parsed HappyFrogScript object
            output_file: Optional output file path
            
        Returns:
            Generated CircuitPython code as string
            
        Raises:
            EncoderError: If encoding fails
        """
        try:
            # Generate the main code
            code_lines = []
            
            # Add header with educational comments
            code_lines.extend(self._generate_header(script))
            
            # Add main execution code
            code_lines.extend(self._generate_main_code(script))
            
            # Add footer
            code_lines.extend(self._generate_footer())
            
            # Join all lines
            code = '\n'.join(code_lines)
            
            # Write to file if specified
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(code)
            
            return code
            
        except Exception as e:
            raise EncoderError(f"Failed to encode script: {str(e)}")
    
    def _generate_header(self, script: HappyFrogScript) -> List[str]:
        """Generate the header section of the CircuitPython code."""
        lines = []
        
        # Add template header
        lines.extend(self.templates['header'].split('\n'))
        
        # Add script metadata as comments
        lines.append("")
        lines.append("# Script Information:")
        lines.append(f"# Source: {script.metadata.get('source', 'Unknown')}")
        lines.append(f"# Total Commands: {script.metadata.get('total_commands', 0)}")
        lines.append(f"# Total Lines: {script.metadata.get('total_lines', 0)}")
        lines.append("")
        
        return lines
    
    def _generate_main_code(self, script: HappyFrogScript) -> List[str]:
        """Generate the main execution code from script commands."""
        lines = []
        
        lines.append("# Main execution loop")
        lines.append("def main():")
        lines.append("    # Wait for system to recognize the device")
        lines.append("    time.sleep(2)")
        lines.append("")
        
        # Process each command
        for i, command in enumerate(script.commands):
            lines.extend(self._encode_command(command, i + 1))
        
        lines.append("")
        lines.append("# Run the main function")
        lines.append("if __name__ == '__main__':")
        lines.append("    main()")
        lines.append("")
        
        return lines
    
    def _encode_command(self, command: HappyFrogCommand, command_index: int) -> List[str]:
        """Encode a single command into CircuitPython code."""
        lines = []
        
        # Add comment with original command
        comment = f"    # Command {command_index}: {command.raw_text}"
        lines.append(comment)
        
        # Encode based on command type
        if command.command_type == CommandType.DELAY:
            lines.extend(self._encode_delay(command))
        elif command.command_type == CommandType.STRING:
            lines.extend(self._encode_string(command))
        elif command.command_type == CommandType.MODIFIER_COMBO:
            lines.extend(self._encode_modifier_combo(command))
        elif command.command_type in self.key_codes:
            lines.extend(self._encode_key_press(command))
        elif command.command_type in [CommandType.COMMENT, CommandType.REM]:
            lines.extend(self._encode_comment(command))
        else:
            # Unknown command - add warning comment
            lines.append(f"    # WARNING: Unknown command '{command.command_type}'")
            lines.append("    pass")
        
        lines.append("")  # Add blank line for readability
        return lines
    
    def _encode_delay(self, command: HappyFrogCommand) -> List[str]:
        """Encode a DELAY command."""
        try:
            delay_ms = int(command.parameters[0])
            if delay_ms < 0:
                raise EncoderError("Delay value must be non-negative")
            return [
                f"    time.sleep({delay_ms / 1000.0})  # Delay for {delay_ms}ms"
            ]
        except (ValueError, IndexError):
            raise EncoderError(f"Invalid delay value '{command.parameters[0] if command.parameters else 'None'}' in command: {command.raw_text}")
    
    def _encode_string(self, command: HappyFrogCommand) -> List[str]:
        """Encode a STRING command."""
        if not command.parameters:
            raise EncoderError(f"STRING command missing text: {command.raw_text}")
        
        text = command.parameters[0]
        # Escape quotes and special characters
        escaped_text = text.replace('\\', '\\\\').replace('"', '\\"')
        
        return [
            f'    keyboard_layout.write("{escaped_text}")  # Type: {text}'
        ]
    
    def _encode_modifier_combo(self, command: HappyFrogCommand) -> List[str]:
        """Encode a MODIFIER_COMBO command (e.g., MOD r, CTRL ALT DEL)."""
        if not command.parameters:
            raise EncoderError(f"MODIFIER_COMBO command missing parameters: {command.raw_text}")
        
        lines = []
        
        # Press all keys in the combo
        for param in command.parameters:
            if param.upper() in ['MOD', 'CTRL', 'SHIFT', 'ALT']:
                # It's a modifier key
                key_code = self.key_codes.get(CommandType(param.upper()))
                if key_code:
                    lines.append(f"    keyboard.press({key_code})  # Press {param}")
            else:
                # It's a regular key - map it to the appropriate keycode
                key_code = self._map_key_to_keycode(param)
                if key_code:
                    lines.append(f"    keyboard.press({key_code})  # Press {param}")
        
        # Release all keys in reverse order
        for param in reversed(command.parameters):
            if param.upper() in ['MOD', 'CTRL', 'SHIFT', 'ALT']:
                key_code = self.key_codes.get(CommandType(param.upper()))
                if key_code:
                    lines.append(f"    keyboard.release({key_code})  # Release {param}")
            else:
                key_code = self._map_key_to_keycode(param)
                if key_code:
                    lines.append(f"    keyboard.release({key_code})  # Release {param}")
        
        return lines
    
    def _map_key_to_keycode(self, key: str) -> str:
        """Map a key string to its CircuitPython keycode."""
        key = key.upper()
        
        # Single letter keys
        if len(key) == 1 and key.isalpha():
            return f"Keycode.{key}"
        
        # Number keys
        if key.isdigit():
            return f"Keycode.{key}"
        
        # Special mappings
        key_mappings = {
            'R': 'Keycode.R',
            'DEL': 'Keycode.DELETE',
            'BACKSPACE': 'Keycode.BACKSPACE',
            'ENTER': 'Keycode.ENTER',
            'SPACE': 'Keycode.SPACE',
            'TAB': 'Keycode.TAB',
            'ESC': 'Keycode.ESCAPE',
            'ESCAPE': 'Keycode.ESCAPE',
        }
        
        return key_mappings.get(key, f"Keycode.{key}")
    
    def _encode_key_press(self, command: HappyFrogCommand) -> List[str]:
        """Encode a key press command."""
        key_code = self.key_codes.get(command.command_type)
        if not key_code:
            raise EncoderError(f"Unsupported key: {command.command_type}")
        
        return [
            f"    keyboard.press({key_code})  # Press {command.command_type.value}",
            f"    keyboard.release({key_code})  # Release {command.command_type.value}"
        ]
    
    def _encode_comment(self, command: HappyFrogCommand) -> List[str]:
        """Encode a comment command."""
        comment_text = command.parameters[0] if command.parameters else ""
        return [
            f"    # {comment_text}"
        ]
    
    def _generate_footer(self) -> List[str]:
        """Generate the footer section of the CircuitPython code."""
        return self.templates['footer'].split('\n')
    
    def _get_header_template(self) -> str:
        """Get the header template for CircuitPython code."""
        return '''"""
Happy Frog - Generated CircuitPython Code
Educational HID Emulation Script

This code was automatically generated from a Happy Frog Script.
It demonstrates how to use CircuitPython for HID emulation.

⚠️ IMPORTANT: Use only for educational purposes and authorized testing!
"""

import time
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

# Initialize HID devices
keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)

# Educational note: This creates a virtual keyboard that the computer
# will recognize as a USB HID device. The keyboard can send keystrokes
# just like a physical keyboard would.'''
    
    def _get_footer_template(self) -> str:
        """Get the footer template for CircuitPython code."""
        return '''"""
End of Happy Frog Generated Code

Educational Notes:
- This script demonstrates basic HID emulation techniques
- Always test in controlled environments
- Use responsibly and ethically
- Consider the security implications of automated input

For more information, visit: https://github.com/ZeroDumb/happy-frog
"""'''
    
    def _get_delay_template(self) -> str:
        """Get the delay command template."""
        return "time.sleep({delay})  # Delay for {delay_ms}ms"
    
    def _get_string_template(self) -> str:
        """Get the string command template."""
        return 'keyboard_layout.write("{text}")  # Type: {original_text}'
    
    def _get_key_press_template(self) -> str:
        """Get the key press template."""
        return [
            "keyboard.press({key_code})  # Press {key_name}",
            "keyboard.release({key_code})  # Release {key_name}"
        ]
    
    def _get_comment_template(self) -> str:
        """Get the comment template."""
        return "# {comment_text}"
    
    def validate_script(self, script: HappyFrogScript) -> List[str]:
        """
        Validate a script for encoding compatibility.
        
        Args:
            script: Parsed HappyFrogScript object
            
        Returns:
            List of warning messages (empty if no issues)
        """
        warnings = []
        
        for command in script.commands:
            # Check for unsupported commands
            if command.command_type not in self.key_codes and \
               command.command_type not in [CommandType.DELAY, CommandType.STRING, 
                                           CommandType.COMMENT, CommandType.REM,
                                           CommandType.MODIFIER_COMBO]:
                warnings.append(
                    f"Line {command.line_number}: Command '{command.command_type.value}' "
                    "may not be fully supported"
                )
            
            # Check for very long strings that might cause issues
            if command.command_type == CommandType.STRING and command.parameters:
                text = command.parameters[0]
                if len(text) > 1000:
                    warnings.append(
                        f"Line {command.line_number}: Very long string ({len(text)} chars) "
                        "may cause timing issues"
                    )
        
        return warnings 