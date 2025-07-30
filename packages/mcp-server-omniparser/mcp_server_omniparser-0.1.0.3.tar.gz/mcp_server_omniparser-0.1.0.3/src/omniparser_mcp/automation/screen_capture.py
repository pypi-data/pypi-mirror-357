"""
Screen capture functionality for taking screenshots of windows and screens.
"""

import time
import platform
from typing import Optional, Tuple, List, Dict, Any
from PIL import Image
import pyautogui
import screeninfo

if platform.system() == "Windows":
    import win32gui
    import win32ui
    import win32con
    import win32api
    from ctypes import windll


class ScreenCapture:
    """Handles screen and window capture operations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize screen capture.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.screenshot_delay = self.config.get('screenshot_delay', 0.1)
        
        # Disable pyautogui failsafe for automation
        pyautogui.FAILSAFE = False
        
    def capture_screen(self, monitor_index: int = 0) -> Image.Image:
        """
        Capture screenshot of entire screen or specific monitor.
        
        Args:
            monitor_index: Index of monitor to capture (0 for primary)
            
        Returns:
            PIL Image of the screenshot
        """
        try:
            time.sleep(self.screenshot_delay)
            
            monitors = screeninfo.get_monitors()
            if monitor_index >= len(monitors):
                monitor_index = 0
            
            monitor = monitors[monitor_index]
            
            # Capture the specified monitor
            screenshot = pyautogui.screenshot(
                region=(monitor.x, monitor.y, monitor.width, monitor.height)
            )
            
            return screenshot
            
        except Exception as e:
            raise RuntimeError(f"Failed to capture screen: {e}")
    
    def capture_window_by_title(self, window_title: str, exact_match: bool = False) -> Optional[Image.Image]:
        """
        Capture screenshot of a specific window by title.
        
        Args:
            window_title: Title of the window to capture
            exact_match: Whether to match title exactly or partially
            
        Returns:
            PIL Image of the window screenshot, or None if window not found
        """
        if platform.system() != "Windows":
            # Fallback to full screen capture on non-Windows systems
            return self.capture_screen()
        
        try:
            hwnd = self._find_window_by_title(window_title, exact_match)
            if not hwnd:
                return None
            
            return self._capture_window_by_hwnd(hwnd)
            
        except Exception as e:
            print(f"Failed to capture window '{window_title}': {e}")
            return None
    
    def capture_window_by_process(self, process_name: str) -> Optional[Image.Image]:
        """
        Capture screenshot of a window by process name.
        
        Args:
            process_name: Name of the process (e.g., 'chrome.exe')
            
        Returns:
            PIL Image of the window screenshot, or None if window not found
        """
        if platform.system() != "Windows":
            return self.capture_screen()
        
        try:
            hwnd = self._find_window_by_process(process_name)
            if not hwnd:
                return None
            
            return self._capture_window_by_hwnd(hwnd)
            
        except Exception as e:
            print(f"Failed to capture window for process '{process_name}': {e}")
            return None
    
    def list_windows(self) -> List[Dict[str, Any]]:
        """
        List all visible windows.
        
        Returns:
            List of window information dictionaries
        """
        if platform.system() != "Windows":
            return []
        
        windows = []
        
        def enum_windows_callback(hwnd, windows_list):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if window_title:
                    try:
                        rect = win32gui.GetWindowRect(hwnd)
                        windows_list.append({
                            'hwnd': hwnd,
                            'title': window_title,
                            'rect': rect,
                            'width': rect[2] - rect[0],
                            'height': rect[3] - rect[1]
                        })
                    except:
                        pass
            return True
        
        try:
            win32gui.EnumWindows(enum_windows_callback, windows)
        except Exception as e:
            print(f"Failed to enumerate windows: {e}")
        
        return windows
    
    def _find_window_by_title(self, window_title: str, exact_match: bool = False) -> Optional[int]:
        """Find window handle by title."""
        if exact_match:
            hwnd = win32gui.FindWindow(None, window_title)
            return hwnd if hwnd else None
        
        # Search for partial match
        windows = self.list_windows()
        for window in windows:
            if window_title.lower() in window['title'].lower():
                return window['hwnd']
        
        return None
    
    def _find_window_by_process(self, process_name: str) -> Optional[int]:
        """Find window handle by process name."""
        import psutil
        
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'].lower() == process_name.lower():
                    pid = proc.info['pid']
                    
                    # Find window associated with this process
                    def enum_windows_callback(hwnd, pid_to_find):
                        _, window_pid = win32gui.GetWindowThreadProcessId(hwnd)
                        if window_pid == pid_to_find and win32gui.IsWindowVisible(hwnd):
                            window_title = win32gui.GetWindowText(hwnd)
                            if window_title:  # Only consider windows with titles
                                return hwnd
                        return True
                    
                    result = []
                    win32gui.EnumWindows(lambda hwnd, param: result.append(hwnd) if enum_windows_callback(hwnd, pid) != True else True, None)
                    if result:
                        return result[0]
        except Exception as e:
            print(f"Error finding window by process: {e}")
        
        return None
    
    def _capture_window_by_hwnd(self, hwnd: int) -> Image.Image:
        """Capture window screenshot by window handle."""
        try:
            # Bring window to foreground
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(self.screenshot_delay)
            
            # Get window rectangle
            rect = win32gui.GetWindowRect(hwnd)
            x, y, x2, y2 = rect
            width = x2 - x
            height = y2 - y
            
            # Capture window
            hwnd_dc = win32gui.GetWindowDC(hwnd)
            mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()
            
            bitmap = win32ui.CreateBitmap()
            bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
            save_dc.SelectObject(bitmap)
            
            # Copy window content
            result = windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 3)
            
            if result:
                # Convert to PIL Image
                bmpinfo = bitmap.GetInfo()
                bmpstr = bitmap.GetBitmapBits(True)
                
                image = Image.frombuffer(
                    'RGB',
                    (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                    bmpstr, 'raw', 'BGRX', 0, 1
                )
            else:
                # Fallback to region screenshot
                image = pyautogui.screenshot(region=(x, y, width, height))
            
            # Cleanup
            win32gui.DeleteObject(bitmap.GetHandle())
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwnd_dc)
            
            return image
            
        except Exception as e:
            # Fallback to region screenshot
            rect = win32gui.GetWindowRect(hwnd)
            x, y, x2, y2 = rect
            return pyautogui.screenshot(region=(x, y, x2-x, y2-y))
    
    def get_screen_size(self, monitor_index: int = 0) -> Tuple[int, int]:
        """
        Get screen size for specified monitor.
        
        Args:
            monitor_index: Index of monitor
            
        Returns:
            Tuple of (width, height)
        """
        monitors = screeninfo.get_monitors()
        if monitor_index >= len(monitors):
            monitor_index = 0
        
        monitor = monitors[monitor_index]
        return monitor.width, monitor.height
