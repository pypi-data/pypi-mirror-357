"""
Mouse automation functionality for simulating mouse operations.
"""

import time
from typing import Tuple, Optional, Dict, Any
import pyautogui


class MouseController:
    """Handles mouse automation operations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize mouse controller.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.action_delay = self.config.get('action_delay', 0.5)
        
        # Disable pyautogui failsafe for automation
        pyautogui.FAILSAFE = False
        
        # Set mouse movement duration
        pyautogui.PAUSE = 0.1
    
    def click(self, x: int, y: int, button: str = 'left', clicks: int = 1, interval: float = 0.0) -> bool:
        """
        Click at specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate  
            button: Mouse button ('left', 'right', 'middle')
            clicks: Number of clicks
            interval: Interval between clicks
            
        Returns:
            True if successful, False otherwise
        """
        try:
            pyautogui.click(x, y, clicks=clicks, interval=interval, button=button)
            time.sleep(self.action_delay)
            return True
        except Exception as e:
            print(f"Failed to click at ({x}, {y}): {e}")
            return False
    
    def double_click(self, x: int, y: int, button: str = 'left') -> bool:
        """
        Double click at specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button
            
        Returns:
            True if successful, False otherwise
        """
        return self.click(x, y, button=button, clicks=2, interval=0.1)
    
    def right_click(self, x: int, y: int) -> bool:
        """
        Right click at specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if successful, False otherwise
        """
        return self.click(x, y, button='right')
    
    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, 
             duration: float = 1.0, button: str = 'left') -> bool:
        """
        Drag from start coordinates to end coordinates.
        
        Args:
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            end_x: Ending X coordinate
            end_y: Ending Y coordinate
            duration: Duration of drag operation in seconds
            button: Mouse button to use for dragging
            
        Returns:
            True if successful, False otherwise
        """
        try:
            pyautogui.drag(start_x, start_y, end_x - start_x, end_y - start_y, 
                          duration=duration, button=button)
            time.sleep(self.action_delay)
            return True
        except Exception as e:
            print(f"Failed to drag from ({start_x}, {start_y}) to ({end_x}, {end_y}): {e}")
            return False
    
    def move_to(self, x: int, y: int, duration: float = 0.5) -> bool:
        """
        Move mouse to specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Duration of movement in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            pyautogui.moveTo(x, y, duration=duration)
            return True
        except Exception as e:
            print(f"Failed to move to ({x}, {y}): {e}")
            return False
    
    def scroll(self, x: int, y: int, clicks: int, direction: str = 'vertical') -> bool:
        """
        Scroll at specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            clicks: Number of scroll clicks (positive for up/right, negative for down/left)
            direction: Scroll direction ('vertical' or 'horizontal')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Move to position first
            pyautogui.moveTo(x, y)
            
            if direction == 'vertical':
                pyautogui.scroll(clicks, x=x, y=y)
            elif direction == 'horizontal':
                pyautogui.hscroll(clicks, x=x, y=y)
            else:
                raise ValueError(f"Invalid scroll direction: {direction}")
            
            time.sleep(self.action_delay)
            return True
        except Exception as e:
            print(f"Failed to scroll at ({x}, {y}): {e}")
            return False
    
    def get_position(self) -> Tuple[int, int]:
        """
        Get current mouse position.
        
        Returns:
            Tuple of (x, y) coordinates
        """
        return pyautogui.position()
    
    def press_and_hold(self, x: int, y: int, button: str = 'left') -> bool:
        """
        Press and hold mouse button at specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button to press
            
        Returns:
            True if successful, False otherwise
        """
        try:
            pyautogui.moveTo(x, y)
            pyautogui.mouseDown(button=button)
            return True
        except Exception as e:
            print(f"Failed to press and hold at ({x}, {y}): {e}")
            return False
    
    def release(self, button: str = 'left') -> bool:
        """
        Release mouse button.
        
        Args:
            button: Mouse button to release
            
        Returns:
            True if successful, False otherwise
        """
        try:
            pyautogui.mouseUp(button=button)
            time.sleep(self.action_delay)
            return True
        except Exception as e:
            print(f"Failed to release {button} button: {e}")
            return False
    
    def drag_and_drop(self, start_x: int, start_y: int, end_x: int, end_y: int,
                      duration: float = 1.0) -> bool:
        """
        Perform drag and drop operation.
        
        Args:
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            end_x: Ending X coordinate
            end_y: Ending Y coordinate
            duration: Duration of drag operation
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Move to start position
            pyautogui.moveTo(start_x, start_y)
            time.sleep(0.1)
            
            # Press and hold
            pyautogui.mouseDown()
            time.sleep(0.1)
            
            # Drag to end position
            pyautogui.moveTo(end_x, end_y, duration=duration)
            time.sleep(0.1)
            
            # Release
            pyautogui.mouseUp()
            time.sleep(self.action_delay)
            
            return True
        except Exception as e:
            print(f"Failed to drag and drop from ({start_x}, {start_y}) to ({end_x}, {end_y}): {e}")
            return False
