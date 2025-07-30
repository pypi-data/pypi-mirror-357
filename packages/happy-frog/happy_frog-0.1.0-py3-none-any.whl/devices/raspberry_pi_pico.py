"""
Happy Frog - Raspberry Pi Pico Device Template

This module provides CircuitPython code generation specifically for the Raspberry Pi Pico.
The Pico is one of the most popular devices for HID emulation due to its low cost,
excellent CircuitPython support, and powerful RP2040 processor.

Educational Purpose: Demonstrates device-specific code generation and optimization.

Author: ZeroDumb
License: GNU GPLv3
"""

from typing import List, Dict, Any, Optional
from happy_frog_parser import HappyFrogScript, HappyFrogCommand, CommandType


class RaspberryPiPicoEncoder:
    """
    Encoder that generates CircuitPython code specifically for Raspberry Pi Pico.
    
    The Pico uses the RP2040 processor and has excellent CircuitPython support
    for HID emulation. This encoder optimizes code for the Pico's capabilities.
    """
    
    def __init__(self):
        """Initialize the Pico-specific encoder."""
        self.device_name = "Raspberry Pi Pico"
        self.processor = "RP2040"
        self.framework = "CircuitPython"
        
        # Pico-specific optimizations
        self.optimizations = {
            'fast_startup': True,  # Pico boots quickly
            'usb_hid_native': True,  # Native USB HID support
            'dual_core': True,  # Can use both cores if needed
            'flash_storage': True,  # Can store scripts in flash
        }
    
    def generate_header(self, script: HappyFrogScript) -> List[str]:
        """Generate Pico-specific header code."""
        lines = []
        
        lines.append('"""')
        lines.append('Happy Frog - Raspberry Pi Pico Generated Code')
        lines.append('Educational HID Emulation Script')
        lines.append('')
        lines.append(f'Device: {self.device_name}')
        lines.append(f'Processor: {self.processor}')
        lines.append(f'Framework: {self.framework}')
        lines.append('')
        lines.append('This code was automatically generated from a Happy Frog Script.')
        lines.append('Optimized for Raspberry Pi Pico with RP2040 processor.')
        lines.append('')
        lines.append('⚠️ IMPORTANT: Use only for educational purposes and authorized testing!')
        lines.append('"""')
        lines.append('')
        
        # Pico-specific imports
        lines.append('import time')
        lines.append('import usb_hid')
        lines.append('from adafruit_hid.keyboard import Keyboard')
        lines.append('from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS')
        lines.append('from adafruit_hid.keycode import Keycode')
        lines.append('from adafruit_hid.mouse import Mouse')
        lines.append('')
        
        # Pico-specific initialization
        lines.append('# Initialize HID devices for Raspberry Pi Pico')
        lines.append('keyboard = Keyboard(usb_hid.devices)')
        lines.append('keyboard_layout = KeyboardLayoutUS(keyboard)')
        lines.append('mouse = Mouse(usb_hid.devices)')
        lines.append('')
        
        # Pico-specific optimizations
        lines.append('# Pico-specific optimizations')
        lines.append('# Fast startup - Pico boots in ~100ms')
        lines.append('time.sleep(0.1)  # Minimal startup delay')
        lines.append('')
        
        return lines
    
    def generate_footer(self) -> List[str]:
        """Generate Pico-specific footer code."""
        lines = []
        
        lines.append('"""')
        lines.append('End of Happy Frog Generated Code for Raspberry Pi Pico')
        lines.append('')
        lines.append('Educational Notes:')
        lines.append('- Raspberry Pi Pico provides excellent HID emulation capabilities')
        lines.append('- RP2040 processor offers dual-core performance')
        lines.append('- CircuitPython makes development and testing easy')
        lines.append('- Low cost makes it ideal for educational projects')
        lines.append('')
        lines.append('For more information, visit: https://github.com/ZeroDumb/happy-frog')
        lines.append('"""')
        
        return lines
    
    def encode_command(self, command: HappyFrogCommand) -> List[str]:
        """Encode a command specifically for Raspberry Pi Pico."""
        lines = []
        
        # Add Pico-specific comment
        comment = f"    # Pico Command: {command.raw_text}"
        lines.append(comment)
        
        # Encode based on command type with Pico optimizations
        if command.command_type == CommandType.DELAY:
            lines.extend(self._encode_delay_pico(command))
        elif command.command_type == CommandType.STRING:
            lines.extend(self._encode_string_pico(command))
        elif command.command_type == CommandType.MODIFIER_COMBO:
            lines.extend(self._encode_modifier_combo_pico(command))
        elif command.command_type == CommandType.RANDOM_DELAY:
            lines.extend(self._encode_random_delay_pico(command))
        else:
            # Use standard encoding for other commands
            lines.extend(self._encode_standard_command(command))
        
        return lines
    
    def _encode_delay_pico(self, command: HappyFrogCommand) -> List[str]:
        """Encode delay with Pico-specific optimizations."""
        try:
            delay_ms = int(command.parameters[0])
            if delay_ms < 0:
                raise ValueError("Delay value must be non-negative")
            
            # Pico-specific delay optimization
            if delay_ms < 10:
                # Very short delays - use microsecond precision
                return [f"    time.sleep({delay_ms / 1000.0})  # Pico optimized delay: {delay_ms}ms"]
            else:
                # Standard delays
                return [f"    time.sleep({delay_ms / 1000.0})  # Delay: {delay_ms}ms"]
                
        except (ValueError, IndexError):
            return ["    # ERROR: Invalid delay value"]
    
    def _encode_string_pico(self, command: HappyFrogCommand) -> List[str]:
        """Encode string with Pico-specific optimizations."""
        if not command.parameters:
            return ["    # ERROR: STRING command missing text"]
        
        text = command.parameters[0]
        escaped_text = text.replace('\\', '\\\\').replace('"', '\\"')
        
        return [
            f'    keyboard_layout.write("{escaped_text}")  # Pico string input: {text}'
        ]
    
    def _encode_modifier_combo_pico(self, command: HappyFrogCommand) -> List[str]:
        """Encode modifier combo with Pico-specific optimizations."""
        if not command.parameters:
            return ["    # ERROR: MODIFIER_COMBO command missing parameters"]
        
        lines = []
        lines.append("    # Pico optimized modifier combo")
        
        # Press all keys in the combo
        for param in command.parameters:
            if param.upper() in ['MOD', 'CTRL', 'SHIFT', 'ALT']:
                key_code = self._get_keycode(param.upper())
                lines.append(f"    keyboard.press({key_code})  # Press {param}")
            else:
                key_code = self._get_keycode(param)
                lines.append(f"    keyboard.press({key_code})  # Press {param}")
        
        # Release all keys in reverse order
        for param in reversed(command.parameters):
            if param.upper() in ['MOD', 'CTRL', 'SHIFT', 'ALT']:
                key_code = self._get_keycode(param.upper())
                lines.append(f"    keyboard.release({key_code})  # Release {param}")
            else:
                key_code = self._get_keycode(param)
                lines.append(f"    keyboard.release({key_code})  # Release {param}")
        
        return lines
    
    def _encode_random_delay_pico(self, command: HappyFrogCommand) -> List[str]:
        """Encode random delay with Pico-specific optimizations."""
        if len(command.parameters) < 2:
            return ["    # ERROR: RANDOM_DELAY command missing min/max values"]
        
        try:
            min_delay = int(command.parameters[0])
            max_delay = int(command.parameters[1])
            
            return [
                f"    # Pico optimized random delay: {min_delay}ms to {max_delay}ms",
                "    import random",
                f"    random_delay = random.uniform({min_delay / 1000.0}, {max_delay / 1000.0})",
                "    time.sleep(random_delay)"
            ]
            
        except ValueError:
            return ["    # ERROR: Invalid random delay values"]
    
    def _encode_standard_command(self, command: HappyFrogCommand) -> List[str]:
        """Encode standard commands for Pico."""
        key_code = self._get_keycode(command.command_type.value)
        return [
            f"    keyboard.press({key_code})  # Pico key press: {command.command_type.value}",
            f"    keyboard.release({key_code})  # Pico key release: {command.command_type.value}"
        ]
    
    def _get_keycode(self, key: str) -> str:
        """Get CircuitPython keycode for a key."""
        key = key.upper()
        
        # Modifier keys
        if key == 'MOD':
            return "Keycode.GUI"
        elif key == 'CTRL':
            return "Keycode.CONTROL"
        elif key == 'SHIFT':
            return "Keycode.SHIFT"
        elif key == 'ALT':
            return "Keycode.ALT"
        
        # Single letter keys
        if len(key) == 1 and key.isalpha():
            return f"Keycode.{key}"
        
        # Number keys
        if key.isdigit():
            return f"Keycode.{key}"
        
        # Special mappings
        key_mappings = {
            'ENTER': 'Keycode.ENTER',
            'SPACE': 'Keycode.SPACE',
            'TAB': 'Keycode.TAB',
            'BACKSPACE': 'Keycode.BACKSPACE',
            'DELETE': 'Keycode.DELETE',
            'ESCAPE': 'Keycode.ESCAPE',
            'HOME': 'Keycode.HOME',
            'END': 'Keycode.END',
            'INSERT': 'Keycode.INSERT',
            'PAGE_UP': 'Keycode.PAGE_UP',
            'PAGE_DOWN': 'Keycode.PAGE_DOWN',
            'UP': 'Keycode.UP_ARROW',
            'DOWN': 'Keycode.DOWN_ARROW',
            'LEFT': 'Keycode.LEFT_ARROW',
            'RIGHT': 'Keycode.RIGHT_ARROW',
        }
        
        return key_mappings.get(key, f"Keycode.{key}")
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get device information for the Pico."""
        return {
            'name': self.device_name,
            'processor': self.processor,
            'framework': self.framework,
            'price_range': '$4-8',
            'difficulty': 'Beginner',
            'features': [
                'Dual-core ARM Cortex-M0+',
                '264KB SRAM',
                '2MB Flash',
                'Native USB HID support',
                'CircuitPython compatible',
                'Low cost',
                'Fast boot time'
            ],
            'setup_notes': [
                'Install CircuitPython firmware',
                'Install adafruit_hid library',
                'Copy code to device',
                'Test in controlled environment'
            ]
        } 