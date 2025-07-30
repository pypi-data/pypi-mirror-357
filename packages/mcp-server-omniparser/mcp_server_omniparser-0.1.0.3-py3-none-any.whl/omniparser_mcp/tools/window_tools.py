"""
MCP tools for window management operations.
"""

from typing import Dict, Any, Optional, List
from ..window_manager.window_detector import WindowDetector
from ..window_manager.window_controller import WindowController


class WindowTools:
    """MCP tools for window management operations."""
    
    def __init__(self, window_detector: WindowDetector, window_controller: WindowController):
        """
        Initialize window tools.
        
        Args:
            window_detector: Window detector instance
            window_controller: Window controller instance
        """
        self.detector = window_detector
        self.controller = window_controller
    
    def list_windows(self, window_type: Optional[str] = None) -> Dict[str, Any]:
        """
        List all available windows.
        
        Args:
            window_type: Filter by window type ('browser', 'game', or None for all)
            
        Returns:
            Dictionary containing list of windows
        """
        try:
            if window_type == 'browser':
                windows = self.detector.find_browser_windows()
            elif window_type == 'game':
                windows = self.detector.find_game_windows()
            else:
                # Get all windows using the detector's method
                all_windows = []
                
                # Get browser windows
                browser_windows = self.detector.find_browser_windows()
                for window in browser_windows:
                    window['window_type'] = 'browser'
                all_windows.extend(browser_windows)
                
                # Get game windows
                game_windows = self.detector.find_game_windows()
                all_windows.extend(game_windows)
                
                # Get other windows by enumerating all
                try:
                    import platform
                    if platform.system() == "Windows":
                        import win32gui
                        import psutil
                        
                        other_windows = []
                        
                        def enum_windows_callback(hwnd, windows_list):
                            if win32gui.IsWindowVisible(hwnd):
                                window_title = win32gui.GetWindowText(hwnd)
                                if window_title:
                                    try:
                                        rect = win32gui.GetWindowRect(hwnd)
                                        _, pid = win32gui.GetWindowThreadProcessId(hwnd)
                                        
                                        # Get process information
                                        process_name = ""
                                        try:
                                            process = psutil.Process(pid)
                                            process_name = process.name()
                                        except:
                                            pass
                                        
                                        # Check if this window is already in browser or game lists
                                        is_duplicate = False
                                        for existing_window in all_windows:
                                            if existing_window.get('hwnd') == hwnd:
                                                is_duplicate = True
                                                break
                                        
                                        if not is_duplicate:
                                            windows_list.append({
                                                'hwnd': hwnd,
                                                'title': window_title,
                                                'rect': rect,
                                                'width': rect[2] - rect[0],
                                                'height': rect[3] - rect[1],
                                                'pid': pid,
                                                'process_name': process_name,
                                                'x': rect[0],
                                                'y': rect[1],
                                                'window_type': 'application'
                                            })
                                    except Exception as e:
                                        pass
                            return True
                        
                        win32gui.EnumWindows(enum_windows_callback, other_windows)
                        all_windows.extend(other_windows)
                except:
                    pass
                
                windows = all_windows
            
            return {
                "success": True,
                "windows": windows,
                "count": len(windows),
                "filter": window_type
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def find_window(self, title_pattern: str, exact_match: bool = False) -> Dict[str, Any]:
        """
        Find window by title pattern.
        
        Args:
            title_pattern: Pattern to match in window title
            exact_match: Whether to match exactly or partially
            
        Returns:
            Dictionary containing found window information
        """
        try:
            windows = self.detector.find_windows_by_title(title_pattern, exact_match)
            
            if not windows:
                return {
                    "success": False,
                    "error": f"No windows found matching pattern: '{title_pattern}'"
                }
            
            return {
                "success": True,
                "window": windows[0],  # Return first match
                "all_matches": windows,
                "match_count": len(windows)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_active_window(self) -> Dict[str, Any]:
        """
        Get information about the currently active window.
        
        Returns:
            Dictionary containing active window information
        """
        try:
            window = self.detector.get_active_window()
            
            if not window:
                return {
                    "success": False,
                    "error": "Could not get active window information"
                }
            
            return {
                "success": True,
                "window": window
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def focus_window(self, title_pattern: str, exact_match: bool = False) -> Dict[str, Any]:
        """
        Focus a window by title pattern.
        
        Args:
            title_pattern: Pattern to match in window title
            exact_match: Whether to match exactly or partially
            
        Returns:
            Dictionary containing operation result
        """
        try:
            # Find the window first
            find_result = self.find_window(title_pattern, exact_match)
            if not find_result["success"]:
                return find_result
            
            window = find_result["window"]
            hwnd = window["hwnd"]
            
            # Focus the window
            success = self.controller.focus_window(hwnd)
            
            return {
                "success": success,
                "action": "focus_window",
                "window": window
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def minimize_window(self, title_pattern: str, exact_match: bool = False) -> Dict[str, Any]:
        """
        Minimize a window by title pattern.
        
        Args:
            title_pattern: Pattern to match in window title
            exact_match: Whether to match exactly or partially
            
        Returns:
            Dictionary containing operation result
        """
        try:
            find_result = self.find_window(title_pattern, exact_match)
            if not find_result["success"]:
                return find_result
            
            window = find_result["window"]
            hwnd = window["hwnd"]
            
            success = self.controller.minimize_window(hwnd)
            
            return {
                "success": success,
                "action": "minimize_window",
                "window": window
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def maximize_window(self, title_pattern: str, exact_match: bool = False) -> Dict[str, Any]:
        """
        Maximize a window by title pattern.
        
        Args:
            title_pattern: Pattern to match in window title
            exact_match: Whether to match exactly or partially
            
        Returns:
            Dictionary containing operation result
        """
        try:
            find_result = self.find_window(title_pattern, exact_match)
            if not find_result["success"]:
                return find_result
            
            window = find_result["window"]
            hwnd = window["hwnd"]
            
            success = self.controller.maximize_window(hwnd)
            
            return {
                "success": success,
                "action": "maximize_window",
                "window": window
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def close_window(self, title_pattern: str, exact_match: bool = False) -> Dict[str, Any]:
        """
        Close a window by title pattern.
        
        Args:
            title_pattern: Pattern to match in window title
            exact_match: Whether to match exactly or partially
            
        Returns:
            Dictionary containing operation result
        """
        try:
            find_result = self.find_window(title_pattern, exact_match)
            if not find_result["success"]:
                return find_result
            
            window = find_result["window"]
            hwnd = window["hwnd"]
            
            success = self.controller.close_window(hwnd)
            
            return {
                "success": success,
                "action": "close_window",
                "window": window
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def move_window(self, title_pattern: str, x: int, y: int, 
                   exact_match: bool = False) -> Dict[str, Any]:
        """
        Move a window to specified coordinates.
        
        Args:
            title_pattern: Pattern to match in window title
            x: New X coordinate
            y: New Y coordinate
            exact_match: Whether to match exactly or partially
            
        Returns:
            Dictionary containing operation result
        """
        try:
            find_result = self.find_window(title_pattern, exact_match)
            if not find_result["success"]:
                return find_result
            
            window = find_result["window"]
            hwnd = window["hwnd"]
            
            success = self.controller.move_window(hwnd, x, y)
            
            return {
                "success": success,
                "action": "move_window",
                "window": window,
                "new_position": {"x": x, "y": y}
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def resize_window(self, title_pattern: str, width: int, height: int,
                     exact_match: bool = False) -> Dict[str, Any]:
        """
        Resize a window to specified dimensions.
        
        Args:
            title_pattern: Pattern to match in window title
            width: New width
            height: New height
            exact_match: Whether to match exactly or partially
            
        Returns:
            Dictionary containing operation result
        """
        try:
            find_result = self.find_window(title_pattern, exact_match)
            if not find_result["success"]:
                return find_result
            
            window = find_result["window"]
            hwnd = window["hwnd"]
            
            success = self.controller.resize_window(hwnd, width, height)
            
            return {
                "success": success,
                "action": "resize_window",
                "window": window,
                "new_size": {"width": width, "height": height}
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
