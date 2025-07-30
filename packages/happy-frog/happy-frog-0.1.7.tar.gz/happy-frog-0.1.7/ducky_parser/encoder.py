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
            
            # Execution control
            CommandType.PAUSE: "PAUSE",  # Special handling for PAUSE command
        }
        
        # CircuitPython code templates
        self.templates = {
            'header': self._get_header_template(),
            'footer': self._get_footer_template(),
            'delay': self._get_delay_template(),
            'string': self._get_string_template(),
            'key_press': self._get_key_press_template(),
            'comment': self._get_comment_template(),
            'repeat': self._get_repeat_template(),
            'conditional': self._get_conditional_template(),
            'loop': self._get_loop_template(),
            'log': self._get_log_template(),
        }
        
        # State for advanced features
        self.default_delay = 0  # Default delay between commands
        self.last_command = None  # For REPEAT functionality
        self.safe_mode = True  # Safe mode enabled by default
    
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
        
        # Add template header (conditional based on safe mode)
        if self.safe_mode:
            lines.extend(self.templates['header'].split('\n'))
        else:
            # Minimal header for production code
            lines.extend([
                '"""',
                'Happy Frog - Generated CircuitPython Code',
                '"""',
                '',
                'import time',
                'import usb_hid',
                'from adafruit_hid.keyboard import Keyboard',
                'from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS',
                'from adafruit_hid.keycode import Keycode',
                '',
                '# Initialize HID devices',
                'keyboard = Keyboard(usb_hid.devices)',
                'keyboard_layout = KeyboardLayoutUS(keyboard)',
                ''
            ])
        
        # Add script metadata as comments (only in safe mode)
        if self.safe_mode:
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
        
        if self.safe_mode:
            lines.append("# Main execution loop")
        lines.append("def main():")
        if self.safe_mode:
            lines.append("    # Wait for system to recognize the device")
        lines.append("    time.sleep(2)")
        lines.append("")
        
        # Process each command
        for i, command in enumerate(script.commands):
            lines.extend(self._encode_command(command, i + 1))
        
        lines.append("")
        if self.safe_mode:
            lines.append("# Run the main function")
        lines.append("if __name__ == '__main__':")
        lines.append("    main()")
        lines.append("")
        
        return lines
    
    def _encode_command(self, command: HappyFrogCommand, command_index: int) -> List[str]:
        """Encode a single command into CircuitPython code."""
        lines = []
        
        # Add comment with original command (only in safe mode)
        if self.safe_mode:
            comment = f"    # Command {command_index}: {command.raw_text}"
            lines.append(comment)
        
        # Encode based on command type
        if command.command_type == CommandType.DELAY:
            lines.extend(self._encode_delay(command))
        elif command.command_type == CommandType.STRING:
            lines.extend(self._encode_string(command))
        elif command.command_type == CommandType.MODIFIER_COMBO:
            lines.extend(self._encode_modifier_combo(command))
        elif command.command_type == CommandType.PAUSE:
            lines.extend(self._encode_pause(command))
        elif command.command_type == CommandType.SAFE_MODE:
            lines.extend(self._encode_safe_mode(command))
        elif command.command_type == CommandType.ATTACKMODE:
            lines.extend(self._encode_attackmode(command))
        elif command.command_type in self.key_codes:
            lines.extend(self._encode_key_press(command))
        elif command.command_type in [CommandType.COMMENT, CommandType.REM]:
            lines.extend(self._encode_comment(command))
        else:
            # Unknown command - add warning comment (only in safe mode)
            if self.safe_mode:
                lines.append(f"    # WARNING: Unknown command '{command.command_type}'")
            lines.append("    pass")
        
        if self.safe_mode:
            lines.append("")  # Add blank line for readability
        return lines
    
    def _encode_delay(self, command: HappyFrogCommand) -> List[str]:
        """Encode a DELAY command."""
        try:
            delay_ms = int(command.parameters[0])
            if delay_ms < 0:
                raise EncoderError("Delay value must be non-negative")
            
            if self.safe_mode:
                return [
                    f"    # DELAY: Wait {delay_ms} milliseconds",
                    f"    time.sleep({delay_ms / 1000.0})"
                ]
            else:
                return [f"    time.sleep({delay_ms / 1000.0})"]
        except (ValueError, IndexError):
            raise EncoderError(f"Invalid DELAY command: {command.raw_text}")
    
    def _encode_string(self, command: HappyFrogCommand) -> List[str]:
        """Encode a STRING command."""
        try:
            text = command.parameters[0]
            if self.safe_mode:
                return [
                    f"    # STRING: Type '{text}'",
                    f"    keyboard_layout.write('{text}')"
                ]
            else:
                return [f"    keyboard_layout.write('{text}')"]
        except IndexError:
            raise EncoderError(f"Invalid STRING command: {command.raw_text}")
    
    def _encode_pause(self, command: HappyFrogCommand) -> List[str]:
        """Encode a PAUSE command."""
        if self.safe_mode:
            return [
                "    # PAUSE: Wait for user input (not implemented in CircuitPython)",
                "    # This would normally wait for a button press or other trigger",
                "    time.sleep(1)  # Default pause duration"
            ]
        else:
            return ["    time.sleep(1)"]
    
    def _encode_modifier_combo(self, command: HappyFrogCommand) -> List[str]:
        """Encode a MODIFIER_COMBO command (e.g., MOD r)."""
        try:
            modifier = command.parameters[0]
            key = command.parameters[1]
            
            # Map modifier to keycode
            modifier_code = self.key_codes.get(CommandType(modifier), f"Keycode.{modifier.upper()}")
            key_code = self._map_key_to_keycode(key)
            
            if self.safe_mode:
                return [
                    f"    # MODIFIER_COMBO: Press {modifier}+{key}",
                    f"    keyboard.press({modifier_code})",
                    f"    keyboard.press({key_code})",
                    f"    keyboard.release_all()",
                    "    time.sleep(0.1)"
                ]
            else:
                return [
                    f"    keyboard.press({modifier_code})",
                    f"    keyboard.press({key_code})",
                    f"    keyboard.release_all()",
                    "    time.sleep(0.1)"
                ]
        except (IndexError, ValueError) as e:
            raise EncoderError(f"Invalid MODIFIER_COMBO command: {command.raw_text}")
    
    def _map_key_to_keycode(self, key: str) -> str:
        """Map a key string to its CircuitPython keycode."""
        key_mappings = {
            'a': 'Keycode.A', 'b': 'Keycode.B', 'c': 'Keycode.C', 'd': 'Keycode.D',
            'e': 'Keycode.E', 'f': 'Keycode.F', 'g': 'Keycode.G', 'h': 'Keycode.H',
            'i': 'Keycode.I', 'j': 'Keycode.J', 'k': 'Keycode.K', 'l': 'Keycode.L',
            'm': 'Keycode.M', 'n': 'Keycode.N', 'o': 'Keycode.O', 'p': 'Keycode.P',
            'q': 'Keycode.Q', 'r': 'Keycode.R', 's': 'Keycode.S', 't': 'Keycode.T',
            'u': 'Keycode.U', 'v': 'Keycode.V', 'w': 'Keycode.W', 'x': 'Keycode.X',
            'y': 'Keycode.Y', 'z': 'Keycode.Z',
            '0': 'Keycode.ZERO', '1': 'Keycode.ONE', '2': 'Keycode.TWO', '3': 'Keycode.THREE',
            '4': 'Keycode.FOUR', '5': 'Keycode.FIVE', '6': 'Keycode.SIX', '7': 'Keycode.SEVEN',
            '8': 'Keycode.EIGHT', '9': 'Keycode.NINE',
            'enter': 'Keycode.ENTER', 'space': 'Keycode.SPACE', 'tab': 'Keycode.TAB',
            'backspace': 'Keycode.BACKSPACE', 'delete': 'Keycode.DELETE',
            'up': 'Keycode.UP_ARROW', 'down': 'Keycode.DOWN_ARROW',
            'left': 'Keycode.LEFT_ARROW', 'right': 'Keycode.RIGHT_ARROW',
            'home': 'Keycode.HOME', 'end': 'Keycode.END', 'insert': 'Keycode.INSERT',
            'page_up': 'Keycode.PAGE_UP', 'page_down': 'Keycode.PAGE_DOWN',
            'escape': 'Keycode.ESCAPE', 'esc': 'Keycode.ESCAPE',
            'f1': 'Keycode.F1', 'f2': 'Keycode.F2', 'f3': 'Keycode.F3', 'f4': 'Keycode.F4',
            'f5': 'Keycode.F5', 'f6': 'Keycode.F6', 'f7': 'Keycode.F7', 'f8': 'Keycode.F8',
            'f9': 'Keycode.F9', 'f10': 'Keycode.F10', 'f11': 'Keycode.F11', 'f12': 'Keycode.F12',
        }
        
        key_lower = key.lower()
        if key_lower in key_mappings:
            return key_mappings[key_lower]
        else:
            # Try to construct the keycode directly
            return f"Keycode.{key.upper()}"
    
    def _encode_key_press(self, command: HappyFrogCommand) -> List[str]:
        """Encode a single key press command."""
        try:
            key_code = self.key_codes[command.command_type]
            if self.safe_mode:
                return [
                    f"    # {command.command_type.value}: Press {command.command_type.value} key",
                    f"    keyboard.press({key_code})",
                    f"    keyboard.release_all()",
                    "    time.sleep(0.1)"
                ]
            else:
                return [
                    f"    keyboard.press({key_code})",
                    f"    keyboard.release_all()",
                    "    time.sleep(0.1)"
                ]
        except KeyError:
            raise EncoderError(f"Unknown key command: {command.command_type}")
    
    def _encode_comment(self, command: HappyFrogCommand) -> List[str]:
        """Encode a comment command."""
        if self.safe_mode:
            return [f"    # {command.parameters[0] if command.parameters else 'Comment'}" ]
        else:
            return []  # Skip comments in production mode
    
    def _encode_safe_mode(self, command: HappyFrogCommand) -> List[str]:
        """Encode a SAFE_MODE command - enable/disable safe mode restrictions."""
        if not command.parameters:
            raise EncoderError(f"SAFE_MODE command missing ON/OFF value: {command.raw_text}")
        
        mode = command.parameters[0].upper()
        if mode not in ['ON', 'OFF']:
            raise EncoderError("SAFE_MODE must be ON or OFF")
        
        self.safe_mode = (mode == 'ON')
        
        return [
            f"    # SAFE_MODE: {'Enabled' if self.safe_mode else 'Disabled'} safe mode restrictions",
            f"    safe_mode = {str(self.safe_mode).lower()}"
        ]
    
    def _encode_attackmode(self, command: HappyFrogCommand) -> List[str]:
        """Encode an ATTACKMODE command (BadUSB syntax)."""
        if not command.parameters:
            raise EncoderError(f"ATTACKMODE command missing parameters: {command.raw_text}")
        
        mode_config = command.parameters[0].upper()
        if mode_config == 'HID':
            self.safe_mode = False  # Attack mode disables safe mode
            return [
                "    # ATTACKMODE: Enabled HID attack mode (BadUSB)",
                "    # This mode allows direct HID emulation without restrictions",
                "    safe_mode = false"
            ]
        else:
            self.safe_mode = (mode_config == 'ON')
            return [
                f"    # ATTACKMODE: {'Enabled' if self.safe_mode else 'Disabled'} attack mode",
                f"    safe_mode = {str(self.safe_mode).lower()}"
            ]
    
    def _generate_footer(self) -> List[str]:
        """Generate the footer section of the CircuitPython code."""
        if self.safe_mode:
            return self.templates['footer'].split('\n')
        else:
            return []  # No footer in production mode
    
    def _get_header_template(self) -> str:
        """Get the header template with educational comments."""
        return '''"""
Happy Frog - Educational HID Emulation Framework
Generated CircuitPython Code for Microcontroller

Educational Purpose: This code demonstrates how to:
- Emulate USB HID devices (keyboard/mouse)
- Execute automated sequences safely
- Understand microcontroller programming
- Learn about USB protocols and automation

⚠️  IMPORTANT: Use only for EDUCATIONAL PURPOSES and AUTHORIZED TESTING!

Author: Generated by Happy Frog Framework
License: GNU GPLv3
"""

import time
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

# Initialize HID devices
keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)

# Educational Note: This code will execute automatically when the device
# is connected to a computer. Always test in a safe environment first!'''
    
    def _get_footer_template(self) -> str:
        """Get the footer template with educational warnings."""
        return '''
# Educational Footer:
# This script demonstrates automated HID emulation techniques.
# Remember to use these skills responsibly and ethically!
# 
# Key Learning Points:
# - USB HID protocols and device emulation
# - Microcontroller programming with CircuitPython
# - Automation and scripting concepts
# - Security implications of HID devices
# 
# For more educational content, visit: https://github.com/ZeroDumb/happy-frog'''
    
    def _get_delay_template(self) -> str:
        """Get the delay template."""
        return "time.sleep({delay})"
    
    def _get_string_template(self) -> str:
        """Get the string template."""
        return "keyboard_layout.write('{text}')"
    
    def _get_key_press_template(self) -> str:
        """Get the key press template."""
        return "keyboard.press({keycode})\nkeyboard.release_all()"
    
    def _get_comment_template(self) -> str:
        """Get the comment template."""
        return "# {comment}"
    
    def _get_repeat_template(self) -> str:
        """Get the repeat template."""
        return "# REPEAT: {count} times"
    
    def _get_conditional_template(self) -> str:
        """Get the conditional template."""
        return "# IF: {condition}"
    
    def _get_loop_template(self) -> str:
        """Get the loop template."""
        return "# WHILE: {condition}"
    
    def _get_log_template(self) -> str:
        """Get the log template."""
        return "# LOG: {message}"
    
    def validate_script(self, script: HappyFrogScript) -> List[str]:
        """
        Validate a parsed script for potential issues.
        
        Args:
            script: Parsed HappyFrogScript object
            
        Returns:
            List of warning messages
        """
        warnings = []
        
        # Check for potentially dangerous commands
        dangerous_commands = []
        for command in script.commands:
            if command.command_type in [CommandType.STRING]:
                # Check string content for potentially dangerous patterns
                if command.parameters:
                    text = command.parameters[0].lower()
                    dangerous_patterns = [
                        'cmd', 'powershell', 'run', 'exec', 'system',
                        'reg', 'rundll32', 'wscript', 'cscript'
                    ]
                    for pattern in dangerous_patterns:
                        if pattern in text:
                            dangerous_commands.append(f"{command.command_type.value}: {command.raw_text}")
                            break
        
        if dangerous_commands:
            warnings.append("Potentially dangerous commands detected:")
            for cmd in dangerous_commands:
                warnings.append(f"  - {cmd}")
            warnings.append("Review these commands carefully before execution.")
        
        # Check for missing delays
        if len(script.commands) > 10:
            delay_commands = [cmd for cmd in script.commands if cmd.command_type == CommandType.DELAY]
            if len(delay_commands) < len(script.commands) * 0.1:  # Less than 10% delays
                warnings.append("Consider adding more DELAY commands for reliable execution.")
        
        return warnings 