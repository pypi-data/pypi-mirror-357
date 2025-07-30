"""
MCP tools for screen parsing and element detection using OmniParser.
"""

import base64
import io
from typing import Dict, List, Any, Optional
from PIL import Image

from ..omniparser_client import OmniParserClient
from ..automation.screen_capture import ScreenCapture


class ScreenTools:
    """MCP tools for screen parsing operations."""
    
    def __init__(self, omniparser_client: OmniParserClient, screen_capture: ScreenCapture):
        """
        Initialize screen tools.
        
        Args:
            omniparser_client: OmniParser client instance
            screen_capture: Screen capture instance
        """
        self.omniparser = omniparser_client
        self.screen_capture = screen_capture
    
    def parse_screen(self, window_title: Optional[str] = None, monitor_index: int = 0) -> Dict[str, Any]:
        """
        Parse current screen or specific window to detect UI elements.
        
        Args:
            window_title: Title of window to capture (None for full screen)
            monitor_index: Monitor index for full screen capture
            
        Returns:
            Dictionary containing parsed elements and labeled image
        """
        try:
            # Capture screenshot
            if window_title:
                image = self.screen_capture.capture_window_by_title(window_title)
                if image is None:
                    return {
                        "success": False,
                        "error": f"Window '{window_title}' not found"
                    }
            else:
                image = self.screen_capture.capture_screen(monitor_index)
            
            # Parse image with OmniParser
            labeled_image, parsed_elements = self.omniparser.parse_image(image)
            
            # Convert labeled image to base64 for return
            buffer = io.BytesIO()
            labeled_image.save(buffer, format='PNG')
            labeled_image_b64 = base64.b64encode(buffer.getvalue()).decode()
            
            return {
                "success": True,
                "elements": parsed_elements,
                "labeled_image_base64": labeled_image_b64,
                "image_size": image.size,
                "total_elements": len(parsed_elements)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_elements(self, window_title: Optional[str] = None, 
                    element_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get list of UI elements from screen or window.
        
        Args:
            window_title: Title of window to analyze (None for full screen)
            element_type: Filter by element type (e.g., 'button', 'text', 'input')
            
        Returns:
            Dictionary containing list of elements
        """
        try:
            # Parse screen first
            parse_result = self.parse_screen(window_title)
            if not parse_result["success"]:
                return parse_result
            
            elements = parse_result["elements"]
            
            # Filter by element type if specified
            if element_type:
                filtered_elements = []
                for element in elements:
                    element_desc = element.get('description', '').lower()
                    element_text = element.get('text', '').lower()
                    
                    if element_type.lower() in element_desc or element_type.lower() in element_text:
                        filtered_elements.append(element)
                
                elements = filtered_elements
            
            return {
                "success": True,
                "elements": elements,
                "count": len(elements),
                "filtered_by": element_type
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def find_element(self, description: str, window_title: Optional[str] = None) -> Dict[str, Any]:
        """
        Find specific UI element by description.
        
        Args:
            description: Description of element to find
            window_title: Title of window to search in (None for full screen)
            
        Returns:
            Dictionary containing found element information
        """
        try:
            # Parse screen first
            parse_result = self.parse_screen(window_title)
            if not parse_result["success"]:
                return parse_result
            
            elements = parse_result["elements"]
            
            # Find matching elements
            matching_elements = self.omniparser.find_elements_by_description(elements, description)
            
            if not matching_elements:
                return {
                    "success": False,
                    "error": f"No elements found matching description: '{description}'"
                }
            
            # Return the best match (first one)
            best_match = matching_elements[0]
            
            # Get center coordinates
            try:
                center_x, center_y = self.omniparser.get_element_center(best_match)
                best_match['center_x'] = center_x
                best_match['center_y'] = center_y
            except:
                pass
            
            return {
                "success": True,
                "element": best_match,
                "all_matches": matching_elements,
                "match_count": len(matching_elements)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_element_at_position(self, x: int, y: int, 
                               window_title: Optional[str] = None) -> Dict[str, Any]:
        """
        Get UI element at specific screen coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            window_title: Title of window to search in (None for full screen)
            
        Returns:
            Dictionary containing element at position
        """
        try:
            # Parse screen first
            parse_result = self.parse_screen(window_title)
            if not parse_result["success"]:
                return parse_result
            
            elements = parse_result["elements"]
            
            # Find element containing the point
            for element in elements:
                if 'coordinates' in element:
                    coords = element['coordinates']
                    if isinstance(coords, list) and len(coords) >= 4:
                        x1, y1, x2, y2 = coords[:4]
                        if x1 <= x <= x2 and y1 <= y <= y2:
                            # Add center coordinates
                            try:
                                center_x, center_y = self.omniparser.get_element_center(element)
                                element['center_x'] = center_x
                                element['center_y'] = center_y
                            except:
                                pass
                            
                            return {
                                "success": True,
                                "element": element,
                                "position": {"x": x, "y": y}
                            }
            
            return {
                "success": False,
                "error": f"No element found at position ({x}, {y})"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def capture_screenshot(self, window_title: Optional[str] = None, 
                          monitor_index: int = 0) -> Dict[str, Any]:
        """
        Capture screenshot without parsing.
        
        Args:
            window_title: Title of window to capture (None for full screen)
            monitor_index: Monitor index for full screen capture
            
        Returns:
            Dictionary containing screenshot as base64
        """
        try:
            # Capture screenshot
            if window_title:
                image = self.screen_capture.capture_window_by_title(window_title)
                if image is None:
                    return {
                        "success": False,
                        "error": f"Window '{window_title}' not found"
                    }
            else:
                image = self.screen_capture.capture_screen(monitor_index)
            
            # Convert to base64
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            image_b64 = base64.b64encode(buffer.getvalue()).decode()
            
            return {
                "success": True,
                "image_base64": image_b64,
                "image_size": image.size,
                "window_title": window_title,
                "monitor_index": monitor_index
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
