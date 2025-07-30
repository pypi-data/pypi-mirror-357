"""
Window detection functionality for finding and identifying application windows.
"""

import platform
import time
from typing import List, Dict, Any, Optional
import psutil

if platform.system() == "Windows":
    import win32gui
    import win32process
    import win32con


class WindowDetector:
    """Detects and identifies application windows."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize window detector.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.supported_browsers = self.config.get('supported_browsers', 
                                                 ['chrome', 'firefox', 'edge', 'safari'])
        self.supported_games = self.config.get('supported_games', 
                                              ['steam', 'epic', 'origin'])
        self.detection_timeout = self.config.get('window_detection_timeout', 5.0)
    
    def find_windows_by_title(self, title_pattern: str, exact_match: bool = False) -> List[Dict[str, Any]]:
        """
        Find windows by title pattern.
        
        Args:
            title_pattern: Pattern to match in window title
            exact_match: Whether to match exactly or partially
            
        Returns:
            List of window information dictionaries
        """
        if platform.system() != "Windows":
            return []
        
        matching_windows = []
        
        def enum_windows_callback(hwnd, windows_list):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if window_title:
                    match = False
                    if exact_match:
                        match = window_title == title_pattern
                    else:
                        match = title_pattern.lower() in window_title.lower()
                    
                    if match:
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
                            
                            windows_list.append({
                                'hwnd': hwnd,
                                'title': window_title,
                                'rect': rect,
                                'width': rect[2] - rect[0],
                                'height': rect[3] - rect[1],
                                'pid': pid,
                                'process_name': process_name,
                                'x': rect[0],
                                'y': rect[1]
                            })
                        except Exception as e:
                            print(f"Error getting window info: {e}")
            return True
        
        try:
            win32gui.EnumWindows(enum_windows_callback, matching_windows)
        except Exception as e:
            print(f"Failed to enumerate windows: {e}")
        
        return matching_windows
    
    def find_windows_by_process(self, process_name: str) -> List[Dict[str, Any]]:
        """
        Find windows by process name.
        
        Args:
            process_name: Name of the process (e.g., 'chrome.exe')
            
        Returns:
            List of window information dictionaries
        """
        if platform.system() != "Windows":
            return []
        
        matching_windows = []
        
        try:
            # Find all processes with matching name
            matching_pids = []
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'].lower() == process_name.lower():
                    matching_pids.append(proc.info['pid'])
            
            if not matching_pids:
                return []
            
            # Find windows for these processes
            def enum_windows_callback(hwnd, windows_list):
                if win32gui.IsWindowVisible(hwnd):
                    window_title = win32gui.GetWindowText(hwnd)
                    if window_title:
                        try:
                            _, pid = win32gui.GetWindowThreadProcessId(hwnd)
                            if pid in matching_pids:
                                rect = win32gui.GetWindowRect(hwnd)
                                windows_list.append({
                                    'hwnd': hwnd,
                                    'title': window_title,
                                    'rect': rect,
                                    'width': rect[2] - rect[0],
                                    'height': rect[3] - rect[1],
                                    'pid': pid,
                                    'process_name': process_name,
                                    'x': rect[0],
                                    'y': rect[1]
                                })
                        except Exception as e:
                            print(f"Error getting window info: {e}")
                return True
            
            win32gui.EnumWindows(enum_windows_callback, matching_windows)
            
        except Exception as e:
            print(f"Failed to find windows by process '{process_name}': {e}")
        
        return matching_windows
    
    def find_browser_windows(self, browser_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Find browser windows.
        
        Args:
            browser_type: Specific browser type to find (e.g., 'chrome', 'firefox')
            
        Returns:
            List of browser window information dictionaries
        """
        browser_processes = {
            'chrome': ['chrome.exe', 'msedge.exe'],
            'firefox': ['firefox.exe'],
            'edge': ['msedge.exe'],
            'safari': ['safari.exe']
        }
        
        all_browser_windows = []
        
        if browser_type:
            if browser_type.lower() in browser_processes:
                for process_name in browser_processes[browser_type.lower()]:
                    windows = self.find_windows_by_process(process_name)
                    for window in windows:
                        window['browser_type'] = browser_type.lower()
                    all_browser_windows.extend(windows)
        else:
            # Find all browser windows
            for browser, processes in browser_processes.items():
                for process_name in processes:
                    windows = self.find_windows_by_process(process_name)
                    for window in windows:
                        window['browser_type'] = browser
                    all_browser_windows.extend(windows)
        
        return all_browser_windows
    
    def find_game_windows(self) -> List[Dict[str, Any]]:
        """
        Find game-related windows.
        
        Returns:
            List of game window information dictionaries
        """
        game_processes = [
            'steam.exe', 'steamwebhelper.exe',
            'epicgameslauncher.exe', 'unrealengine.exe',
            'origin.exe', 'originwebhelperservice.exe',
            'battle.net.exe', 'wow.exe', 'overwatch.exe',
            'league of legends.exe', 'riotclientservices.exe',
            'discord.exe'
        ]
        
        all_game_windows = []
        
        for process_name in game_processes:
            windows = self.find_windows_by_process(process_name)
            for window in windows:
                window['window_type'] = 'game'
            all_game_windows.extend(windows)
        
        return all_game_windows
    
    def get_active_window(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the currently active window.
        
        Returns:
            Active window information dictionary or None
        """
        if platform.system() != "Windows":
            return None
        
        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                window_title = win32gui.GetWindowText(hwnd)
                rect = win32gui.GetWindowRect(hwnd)
                _, pid = win32gui.GetWindowThreadProcessId(hwnd)
                
                # Get process information
                process_name = ""
                try:
                    process = psutil.Process(pid)
                    process_name = process.name()
                except:
                    pass
                
                return {
                    'hwnd': hwnd,
                    'title': window_title,
                    'rect': rect,
                    'width': rect[2] - rect[0],
                    'height': rect[3] - rect[1],
                    'pid': pid,
                    'process_name': process_name,
                    'x': rect[0],
                    'y': rect[1]
                }
        except Exception as e:
            print(f"Failed to get active window: {e}")
        
        return None
    
    def wait_for_window(self, title_pattern: str, timeout: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Wait for a window with specified title pattern to appear.
        
        Args:
            title_pattern: Pattern to match in window title
            timeout: Maximum time to wait in seconds
            
        Returns:
            Window information dictionary or None if timeout
        """
        if timeout is None:
            timeout = self.detection_timeout
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            windows = self.find_windows_by_title(title_pattern)
            if windows:
                return windows[0]  # Return first matching window
            
            time.sleep(0.5)
        
        return None
    
    def is_window_minimized(self, hwnd: int) -> bool:
        """
        Check if a window is minimized.
        
        Args:
            hwnd: Window handle
            
        Returns:
            True if window is minimized, False otherwise
        """
        if platform.system() != "Windows":
            return False
        
        try:
            return win32gui.IsIconic(hwnd)
        except:
            return False
    
    def is_window_maximized(self, hwnd: int) -> bool:
        """
        Check if a window is maximized.
        
        Args:
            hwnd: Window handle
            
        Returns:
            True if window is maximized, False otherwise
        """
        if platform.system() != "Windows":
            return False
        
        try:
            return win32gui.IsZoomed(hwnd)
        except:
            return False
