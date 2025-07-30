"""
Keyboard automation functionality for simulating keyboard operations.
"""

import time
from typing import List, Optional, Dict, Any, Union
import pyautogui


class KeyboardController:
    """Handles keyboard automation operations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize keyboard controller.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.action_delay = self.config.get('action_delay', 0.5)
        
        # Disable pyautogui failsafe for automation
        pyautogui.FAILSAFE = False
    
    def type_text(self, text: str, interval: float = 0.0) -> bool:
        """
        Type text string.
        
        Args:
            text: Text to type
            interval: Interval between keystrokes
            
        Returns:
            True if successful, False otherwise
        """
        try:
            pyautogui.typewrite(text, interval=interval)
            time.sleep(self.action_delay)
            return True
        except Exception as e:
            print(f"Failed to type text '{text}': {e}")
            return False
    
    def press_key(self, key: str, presses: int = 1, interval: float = 0.0) -> bool:
        """
        Press a key or key combination.
        
        Args:
            key: Key to press (e.g., 'enter', 'space', 'ctrl+c')
            presses: Number of times to press the key
            interval: Interval between presses
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if '+' in key:
                # Handle key combinations
                keys = key.split('+')
                pyautogui.hotkey(*keys)
            else:
                # Handle single key
                pyautogui.press(key, presses=presses, interval=interval)
            
            time.sleep(self.action_delay)
            return True
        except Exception as e:
            print(f"Failed to press key '{key}': {e}")
            return False
    
    def press_keys(self, keys: List[str], interval: float = 0.0) -> bool:
        """
        Press multiple keys in sequence.
        
        Args:
            keys: List of keys to press
            interval: Interval between key presses
            
        Returns:
            True if successful, False otherwise
        """
        try:
            for key in keys:
                self.press_key(key)
                if interval > 0:
                    time.sleep(interval)
            return True
        except Exception as e:
            print(f"Failed to press keys {keys}: {e}")
            return False
    
    def hold_key(self, key: str) -> bool:
        """
        Hold down a key.
        
        Args:
            key: Key to hold down
            
        Returns:
            True if successful, False otherwise
        """
        try:
            pyautogui.keyDown(key)
            return True
        except Exception as e:
            print(f"Failed to hold key '{key}': {e}")
            return False
    
    def release_key(self, key: str) -> bool:
        """
        Release a held key.
        
        Args:
            key: Key to release
            
        Returns:
            True if successful, False otherwise
        """
        try:
            pyautogui.keyUp(key)
            time.sleep(self.action_delay)
            return True
        except Exception as e:
            print(f"Failed to release key '{key}': {e}")
            return False
    
    def key_combination(self, keys: List[str]) -> bool:
        """
        Press a combination of keys simultaneously.
        
        Args:
            keys: List of keys to press together
            
        Returns:
            True if successful, False otherwise
        """
        try:
            pyautogui.hotkey(*keys)
            time.sleep(self.action_delay)
            return True
        except Exception as e:
            print(f"Failed to press key combination {keys}: {e}")
            return False
    
    def clear_text(self, method: str = 'ctrl+a') -> bool:
        """
        Clear text in current input field.
        
        Args:
            method: Method to clear text ('ctrl+a', 'backspace', 'delete')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if method == 'ctrl+a':
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(0.1)
                pyautogui.press('delete')
            elif method == 'backspace':
                # Clear by pressing backspace multiple times
                for _ in range(100):  # Arbitrary large number
                    pyautogui.press('backspace')
            elif method == 'delete':
                # Select all and delete
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(0.1)
                pyautogui.press('delete')
            else:
                raise ValueError(f"Invalid clear method: {method}")
            
            time.sleep(self.action_delay)
            return True
        except Exception as e:
            print(f"Failed to clear text using method '{method}': {e}")
            return False
    
    def paste_text(self, text: str) -> bool:
        """
        Paste text using clipboard.
        
        Args:
            text: Text to paste
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import pyperclip
            
            # Save current clipboard content
            original_clipboard = pyperclip.paste()
            
            # Set text to clipboard and paste
            pyperclip.copy(text)
            pyautogui.hotkey('ctrl', 'v')
            
            # Restore original clipboard content
            time.sleep(0.1)
            pyperclip.copy(original_clipboard)
            
            time.sleep(self.action_delay)
            return True
        except Exception as e:
            print(f"Failed to paste text '{text}': {e}")
            # Fallback to typing
            return self.type_text(text)
    
    def copy_text(self) -> Optional[str]:
        """
        Copy selected text to clipboard and return it.
        
        Returns:
            Copied text or None if failed
        """
        try:
            import pyperclip
            
            # Save current clipboard content
            original_clipboard = pyperclip.paste()
            
            # Clear clipboard and copy
            pyperclip.copy('')
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.2)
            
            # Get copied text
            copied_text = pyperclip.paste()
            
            # Restore original clipboard if nothing was copied
            if not copied_text:
                pyperclip.copy(original_clipboard)
                return None
            
            return copied_text
        except Exception as e:
            print(f"Failed to copy text: {e}")
            return None
    
    def send_special_key(self, key: str) -> bool:
        """
        Send special keys like function keys, arrow keys, etc.
        
        Args:
            key: Special key name (e.g., 'f1', 'up', 'down', 'left', 'right', 'home', 'end')
            
        Returns:
            True if successful, False otherwise
        """
        special_keys = {
            'up': 'up', 'down': 'down', 'left': 'left', 'right': 'right',
            'home': 'home', 'end': 'end', 'pageup': 'pageup', 'pagedown': 'pagedown',
            'insert': 'insert', 'delete': 'delete', 'backspace': 'backspace',
            'tab': 'tab', 'enter': 'enter', 'space': 'space', 'escape': 'esc',
            'f1': 'f1', 'f2': 'f2', 'f3': 'f3', 'f4': 'f4', 'f5': 'f5',
            'f6': 'f6', 'f7': 'f7', 'f8': 'f8', 'f9': 'f9', 'f10': 'f10',
            'f11': 'f11', 'f12': 'f12'
        }
        
        key_lower = key.lower()
        if key_lower in special_keys:
            return self.press_key(special_keys[key_lower])
        else:
            print(f"Unknown special key: {key}")
            return False
