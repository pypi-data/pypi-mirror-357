"""
MCP tools for automation operations like clicking, typing, and dragging.
"""

from typing import Dict, Any, Optional, List
from ..automation.mouse import MouseController
from ..automation.keyboard import KeyboardController
from ..tools.screen_tools import ScreenTools


class AutomationTools:
    """MCP tools for automation operations."""
    
    def __init__(self, mouse_controller: MouseController, 
                 keyboard_controller: KeyboardController,
                 screen_tools: ScreenTools):
        """
        Initialize automation tools.
        
        Args:
            mouse_controller: Mouse controller instance
            keyboard_controller: Keyboard controller instance
            screen_tools: Screen tools instance
        """
        self.mouse = mouse_controller
        self.keyboard = keyboard_controller
        self.screen_tools = screen_tools
    
    def click_element(self, description: str, window_title: Optional[str] = None,
                     button: str = 'left', clicks: int = 1) -> Dict[str, Any]:
        """
        Click on a UI element identified by description.
        
        Args:
            description: Description of element to click
            window_title: Title of window containing element
            button: Mouse button to use ('left', 'right', 'middle')
            clicks: Number of clicks
            
        Returns:
            Dictionary containing operation result
        """
        try:
            # Find the element
            find_result = self.screen_tools.find_element(description, window_title)
            if not find_result["success"]:
                return find_result
            
            element = find_result["element"]
            
            # Get click coordinates
            if 'center_x' in element and 'center_y' in element:
                x, y = element['center_x'], element['center_y']
            else:
                try:
                    from ..omniparser_client import OmniParserClient
                    # Create temporary client to get center
                    x, y = OmniParserClient.get_element_center(None, element)
                except:
                    return {
                        "success": False,
                        "error": "Could not determine element coordinates"
                    }
            
            # Perform click
            success = self.mouse.click(x, y, button=button, clicks=clicks)
            
            return {
                "success": success,
                "action": "click",
                "element": element,
                "coordinates": {"x": x, "y": y},
                "button": button,
                "clicks": clicks
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def click_coordinates(self, x: int, y: int, button: str = 'left', 
                         clicks: int = 1) -> Dict[str, Any]:
        """
        Click at specific coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button to use
            clicks: Number of clicks
            
        Returns:
            Dictionary containing operation result
        """
        try:
            success = self.mouse.click(x, y, button=button, clicks=clicks)
            
            return {
                "success": success,
                "action": "click_coordinates",
                "coordinates": {"x": x, "y": y},
                "button": button,
                "clicks": clicks
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def double_click_element(self, description: str, 
                            window_title: Optional[str] = None) -> Dict[str, Any]:
        """
        Double click on a UI element.
        
        Args:
            description: Description of element to double click
            window_title: Title of window containing element
            
        Returns:
            Dictionary containing operation result
        """
        return self.click_element(description, window_title, button='left', clicks=2)
    
    def right_click_element(self, description: str, 
                           window_title: Optional[str] = None) -> Dict[str, Any]:
        """
        Right click on a UI element.
        
        Args:
            description: Description of element to right click
            window_title: Title of window containing element
            
        Returns:
            Dictionary containing operation result
        """
        return self.click_element(description, window_title, button='right', clicks=1)
    
    def type_text(self, text: str, clear_first: bool = False, 
                  interval: float = 0.0) -> Dict[str, Any]:
        """
        Type text at current cursor position.
        
        Args:
            text: Text to type
            clear_first: Whether to clear existing text first
            interval: Interval between keystrokes
            
        Returns:
            Dictionary containing operation result
        """
        try:
            if clear_first:
                self.keyboard.clear_text()
            
            success = self.keyboard.type_text(text, interval=interval)
            
            return {
                "success": success,
                "action": "type_text",
                "text": text,
                "clear_first": clear_first,
                "interval": interval
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def type_in_element(self, description: str, text: str, 
                       window_title: Optional[str] = None,
                       clear_first: bool = True) -> Dict[str, Any]:
        """
        Click on an element and type text into it.
        
        Args:
            description: Description of element to type in
            text: Text to type
            window_title: Title of window containing element
            clear_first: Whether to clear existing text first
            
        Returns:
            Dictionary containing operation result
        """
        try:
            # First click on the element
            click_result = self.click_element(description, window_title)
            if not click_result["success"]:
                return click_result
            
            # Then type the text
            type_result = self.type_text(text, clear_first=clear_first)
            
            return {
                "success": type_result["success"],
                "action": "type_in_element",
                "element": click_result["element"],
                "text": text,
                "clear_first": clear_first,
                "click_result": click_result,
                "type_result": type_result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def press_key(self, key: str, presses: int = 1) -> Dict[str, Any]:
        """
        Press a key or key combination.
        
        Args:
            key: Key to press (e.g., 'enter', 'space', 'ctrl+c')
            presses: Number of times to press
            
        Returns:
            Dictionary containing operation result
        """
        try:
            success = self.keyboard.press_key(key, presses=presses)
            
            return {
                "success": success,
                "action": "press_key",
                "key": key,
                "presses": presses
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def drag_element(self, from_description: str, to_description: str,
                    window_title: Optional[str] = None, 
                    duration: float = 1.0) -> Dict[str, Any]:
        """
        Drag from one element to another.
        
        Args:
            from_description: Description of source element
            to_description: Description of target element
            window_title: Title of window containing elements
            duration: Duration of drag operation
            
        Returns:
            Dictionary containing operation result
        """
        try:
            # Find source element
            from_result = self.screen_tools.find_element(from_description, window_title)
            if not from_result["success"]:
                return {
                    "success": False,
                    "error": f"Source element not found: {from_result['error']}"
                }
            
            # Find target element
            to_result = self.screen_tools.find_element(to_description, window_title)
            if not to_result["success"]:
                return {
                    "success": False,
                    "error": f"Target element not found: {to_result['error']}"
                }
            
            from_element = from_result["element"]
            to_element = to_result["element"]
            
            # Get coordinates
            from_x, from_y = from_element.get('center_x'), from_element.get('center_y')
            to_x, to_y = to_element.get('center_x'), to_element.get('center_y')
            
            if None in [from_x, from_y, to_x, to_y]:
                return {
                    "success": False,
                    "error": "Could not determine element coordinates"
                }
            
            # Perform drag
            success = self.mouse.drag(from_x, from_y, to_x, to_y, duration=duration)
            
            return {
                "success": success,
                "action": "drag_element",
                "from_element": from_element,
                "to_element": to_element,
                "from_coordinates": {"x": from_x, "y": from_y},
                "to_coordinates": {"x": to_x, "y": to_y},
                "duration": duration
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def scroll(self, x: int, y: int, clicks: int, 
              direction: str = 'vertical') -> Dict[str, Any]:
        """
        Scroll at specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            clicks: Number of scroll clicks (positive for up/right, negative for down/left)
            direction: Scroll direction ('vertical' or 'horizontal')
            
        Returns:
            Dictionary containing operation result
        """
        try:
            success = self.mouse.scroll(x, y, clicks, direction=direction)
            
            return {
                "success": success,
                "action": "scroll",
                "coordinates": {"x": x, "y": y},
                "clicks": clicks,
                "direction": direction
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def scroll_element(self, description: str, clicks: int,
                      window_title: Optional[str] = None,
                      direction: str = 'vertical') -> Dict[str, Any]:
        """
        Scroll within a specific element.
        
        Args:
            description: Description of element to scroll in
            clicks: Number of scroll clicks
            window_title: Title of window containing element
            direction: Scroll direction
            
        Returns:
            Dictionary containing operation result
        """
        try:
            # Find the element
            find_result = self.screen_tools.find_element(description, window_title)
            if not find_result["success"]:
                return find_result
            
            element = find_result["element"]
            x, y = element.get('center_x'), element.get('center_y')
            
            if None in [x, y]:
                return {
                    "success": False,
                    "error": "Could not determine element coordinates"
                }
            
            # Perform scroll
            success = self.mouse.scroll(x, y, clicks, direction=direction)
            
            return {
                "success": success,
                "action": "scroll_element",
                "element": element,
                "coordinates": {"x": x, "y": y},
                "clicks": clicks,
                "direction": direction
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
