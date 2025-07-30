"""
Window control functionality for managing and manipulating application windows.
"""

import platform
import time
from typing import Dict, Any, Optional, Tuple
import pyautogui

if platform.system() == "Windows":
    import win32gui
    import win32con


class WindowController:
    """Controls and manipulates application windows."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize window controller.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.action_delay = self.config.get('action_delay', 0.5)
    
    def focus_window(self, hwnd: int) -> bool:
        """
        Bring a window to the foreground and focus it.
        
        Args:
            hwnd: Window handle
            
        Returns:
            True if successful, False otherwise
        """
        if platform.system() != "Windows":
            return False
        
        try:
            # Restore window if minimized
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.2)
            
            # Bring to foreground
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(self.action_delay)
            
            return True
        except Exception as e:
            print(f"Failed to focus window {hwnd}: {e}")
            return False
    
    def minimize_window(self, hwnd: int) -> bool:
        """
        Minimize a window.
        
        Args:
            hwnd: Window handle
            
        Returns:
            True if successful, False otherwise
        """
        if platform.system() != "Windows":
            return False
        
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            time.sleep(self.action_delay)
            return True
        except Exception as e:
            print(f"Failed to minimize window {hwnd}: {e}")
            return False
    
    def maximize_window(self, hwnd: int) -> bool:
        """
        Maximize a window.
        
        Args:
            hwnd: Window handle
            
        Returns:
            True if successful, False otherwise
        """
        if platform.system() != "Windows":
            return False
        
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            time.sleep(self.action_delay)
            return True
        except Exception as e:
            print(f"Failed to maximize window {hwnd}: {e}")
            return False
    
    def restore_window(self, hwnd: int) -> bool:
        """
        Restore a window to normal size.
        
        Args:
            hwnd: Window handle
            
        Returns:
            True if successful, False otherwise
        """
        if platform.system() != "Windows":
            return False
        
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(self.action_delay)
            return True
        except Exception as e:
            print(f"Failed to restore window {hwnd}: {e}")
            return False
    
    def close_window(self, hwnd: int) -> bool:
        """
        Close a window.
        
        Args:
            hwnd: Window handle
            
        Returns:
            True if successful, False otherwise
        """
        if platform.system() != "Windows":
            return False
        
        try:
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            time.sleep(self.action_delay)
            return True
        except Exception as e:
            print(f"Failed to close window {hwnd}: {e}")
            return False
    
    def move_window(self, hwnd: int, x: int, y: int) -> bool:
        """
        Move a window to specified coordinates.
        
        Args:
            hwnd: Window handle
            x: New X coordinate
            y: New Y coordinate
            
        Returns:
            True if successful, False otherwise
        """
        if platform.system() != "Windows":
            return False
        
        try:
            # Get current window size
            rect = win32gui.GetWindowRect(hwnd)
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]
            
            # Move window
            win32gui.SetWindowPos(hwnd, 0, x, y, width, height, 
                                win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE)
            time.sleep(self.action_delay)
            return True
        except Exception as e:
            print(f"Failed to move window {hwnd} to ({x}, {y}): {e}")
            return False
    
    def resize_window(self, hwnd: int, width: int, height: int) -> bool:
        """
        Resize a window to specified dimensions.
        
        Args:
            hwnd: Window handle
            width: New width
            height: New height
            
        Returns:
            True if successful, False otherwise
        """
        if platform.system() != "Windows":
            return False
        
        try:
            # Get current window position
            rect = win32gui.GetWindowRect(hwnd)
            x = rect[0]
            y = rect[1]
            
            # Resize window
            win32gui.SetWindowPos(hwnd, 0, x, y, width, height, 
                                win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE)
            time.sleep(self.action_delay)
            return True
        except Exception as e:
            print(f"Failed to resize window {hwnd} to {width}x{height}: {e}")
            return False
    
    def move_and_resize_window(self, hwnd: int, x: int, y: int, width: int, height: int) -> bool:
        """
        Move and resize a window in one operation.
        
        Args:
            hwnd: Window handle
            x: New X coordinate
            y: New Y coordinate
            width: New width
            height: New height
            
        Returns:
            True if successful, False otherwise
        """
        if platform.system() != "Windows":
            return False
        
        try:
            win32gui.SetWindowPos(hwnd, 0, x, y, width, height, 
                                win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE)
            time.sleep(self.action_delay)
            return True
        except Exception as e:
            print(f"Failed to move and resize window {hwnd}: {e}")
            return False
    
    def get_window_rect(self, hwnd: int) -> Optional[Tuple[int, int, int, int]]:
        """
        Get window rectangle coordinates.
        
        Args:
            hwnd: Window handle
            
        Returns:
            Tuple of (left, top, right, bottom) or None if failed
        """
        if platform.system() != "Windows":
            return None
        
        try:
            return win32gui.GetWindowRect(hwnd)
        except Exception as e:
            print(f"Failed to get window rect for {hwnd}: {e}")
            return None
    
    def set_window_topmost(self, hwnd: int, topmost: bool = True) -> bool:
        """
        Set window to be always on top or remove topmost status.
        
        Args:
            hwnd: Window handle
            topmost: True to set topmost, False to remove topmost
            
        Returns:
            True if successful, False otherwise
        """
        if platform.system() != "Windows":
            return False
        
        try:
            flag = win32con.HWND_TOPMOST if topmost else win32con.HWND_NOTOPMOST
            win32gui.SetWindowPos(hwnd, flag, 0, 0, 0, 0, 
                                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            time.sleep(self.action_delay)
            return True
        except Exception as e:
            print(f"Failed to set topmost for window {hwnd}: {e}")
            return False
    
    def click_window_center(self, hwnd: int) -> bool:
        """
        Click the center of a window.
        
        Args:
            hwnd: Window handle
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Focus window first
            if not self.focus_window(hwnd):
                return False
            
            # Get window rectangle
            rect = self.get_window_rect(hwnd)
            if not rect:
                return False
            
            # Calculate center
            center_x = (rect[0] + rect[2]) // 2
            center_y = (rect[1] + rect[3]) // 2
            
            # Click center
            pyautogui.click(center_x, center_y)
            time.sleep(self.action_delay)
            
            return True
        except Exception as e:
            print(f"Failed to click center of window {hwnd}: {e}")
            return False
    
    def send_keys_to_window(self, hwnd: int, keys: str) -> bool:
        """
        Send keystrokes to a specific window.
        
        Args:
            hwnd: Window handle
            keys: Keys to send
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Focus window first
            if not self.focus_window(hwnd):
                return False
            
            # Send keys
            pyautogui.typewrite(keys)
            time.sleep(self.action_delay)
            
            return True
        except Exception as e:
            print(f"Failed to send keys to window {hwnd}: {e}")
            return False
