"""
Tests for automation functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.omniparser_mcp.automation.mouse import MouseController
from src.omniparser_mcp.automation.keyboard import KeyboardController
from src.omniparser_mcp.automation.screen_capture import ScreenCapture


class TestMouseController:
    """Test cases for MouseController."""
    
    @pytest.fixture
    def mouse_controller(self):
        """Create MouseController instance for testing."""
        return MouseController({"action_delay": 0.1})
    
    @patch('pyautogui.click')
    def test_click_success(self, mock_click, mouse_controller):
        """Test successful mouse click."""
        mock_click.return_value = None
        
        result = mouse_controller.click(100, 200, button='left', clicks=1)
        
        assert result is True
        mock_click.assert_called_once_with(100, 200, clicks=1, interval=0.0, button='left')
    
    @patch('pyautogui.click')
    def test_click_failure(self, mock_click, mouse_controller):
        """Test mouse click failure."""
        mock_click.side_effect = Exception("Click failed")
        
        result = mouse_controller.click(100, 200)
        
        assert result is False
    
    @patch('pyautogui.drag')
    def test_drag_success(self, mock_drag, mouse_controller):
        """Test successful drag operation."""
        mock_drag.return_value = None
        
        result = mouse_controller.drag(100, 100, 200, 200, duration=1.0)
        
        assert result is True
        mock_drag.assert_called_once_with(100, 100, 100, 100, duration=1.0, button='left')
    
    @patch('pyautogui.scroll')
    @patch('pyautogui.moveTo')
    def test_scroll_vertical(self, mock_move, mock_scroll, mouse_controller):
        """Test vertical scrolling."""
        mock_move.return_value = None
        mock_scroll.return_value = None
        
        result = mouse_controller.scroll(100, 100, 3, direction='vertical')
        
        assert result is True
        mock_move.assert_called_once_with(100, 100)
        mock_scroll.assert_called_once_with(3, x=100, y=100)
    
    @patch('pyautogui.position')
    def test_get_position(self, mock_position, mouse_controller):
        """Test getting mouse position."""
        mock_position.return_value = (150, 250)
        
        x, y = mouse_controller.get_position()
        
        assert x == 150
        assert y == 250


class TestKeyboardController:
    """Test cases for KeyboardController."""
    
    @pytest.fixture
    def keyboard_controller(self):
        """Create KeyboardController instance for testing."""
        return KeyboardController({"action_delay": 0.1})
    
    @patch('pyautogui.typewrite')
    def test_type_text_success(self, mock_typewrite, keyboard_controller):
        """Test successful text typing."""
        mock_typewrite.return_value = None
        
        result = keyboard_controller.type_text("Hello World", interval=0.1)
        
        assert result is True
        mock_typewrite.assert_called_once_with("Hello World", interval=0.1)
    
    @patch('pyautogui.typewrite')
    def test_type_text_failure(self, mock_typewrite, keyboard_controller):
        """Test text typing failure."""
        mock_typewrite.side_effect = Exception("Type failed")
        
        result = keyboard_controller.type_text("Hello World")
        
        assert result is False
    
    @patch('pyautogui.press')
    def test_press_key_single(self, mock_press, keyboard_controller):
        """Test pressing a single key."""
        mock_press.return_value = None
        
        result = keyboard_controller.press_key('enter', presses=1)
        
        assert result is True
        mock_press.assert_called_once_with('enter', presses=1, interval=0.0)
    
    @patch('pyautogui.hotkey')
    def test_press_key_combination(self, mock_hotkey, keyboard_controller):
        """Test pressing key combination."""
        mock_hotkey.return_value = None
        
        result = keyboard_controller.press_key('ctrl+c')
        
        assert result is True
        mock_hotkey.assert_called_once_with('ctrl', 'c')
    
    @patch('pyautogui.hotkey')
    def test_key_combination(self, mock_hotkey, keyboard_controller):
        """Test key combination method."""
        mock_hotkey.return_value = None
        
        result = keyboard_controller.key_combination(['ctrl', 'shift', 'n'])
        
        assert result is True
        mock_hotkey.assert_called_once_with('ctrl', 'shift', 'n')
    
    @patch('pyautogui.hotkey')
    @patch('pyautogui.press')
    def test_clear_text_ctrl_a(self, mock_press, mock_hotkey, keyboard_controller):
        """Test clearing text with Ctrl+A method."""
        mock_hotkey.return_value = None
        mock_press.return_value = None
        
        result = keyboard_controller.clear_text(method='ctrl+a')
        
        assert result is True
        mock_hotkey.assert_called_once_with('ctrl', 'a')
        mock_press.assert_called_once_with('delete')


class TestScreenCapture:
    """Test cases for ScreenCapture."""
    
    @pytest.fixture
    def screen_capture(self):
        """Create ScreenCapture instance for testing."""
        return ScreenCapture({"screenshot_delay": 0.1})
    
    @patch('pyautogui.screenshot')
    @patch('screeninfo.get_monitors')
    def test_capture_screen_success(self, mock_monitors, mock_screenshot, screen_capture):
        """Test successful screen capture."""
        # Mock monitor info
        mock_monitor = Mock()
        mock_monitor.x = 0
        mock_monitor.y = 0
        mock_monitor.width = 1920
        mock_monitor.height = 1080
        mock_monitors.return_value = [mock_monitor]
        
        # Mock screenshot
        mock_image = Mock()
        mock_screenshot.return_value = mock_image
        
        result = screen_capture.capture_screen(monitor_index=0)
        
        assert result == mock_image
        mock_screenshot.assert_called_once_with(region=(0, 0, 1920, 1080))
    
    @patch('screeninfo.get_monitors')
    def test_capture_screen_invalid_monitor(self, mock_monitors, screen_capture):
        """Test screen capture with invalid monitor index."""
        mock_monitor = Mock()
        mock_monitor.x = 0
        mock_monitor.y = 0
        mock_monitor.width = 1920
        mock_monitor.height = 1080
        mock_monitors.return_value = [mock_monitor]
        
        with patch('pyautogui.screenshot') as mock_screenshot:
            mock_image = Mock()
            mock_screenshot.return_value = mock_image
            
            # Request monitor index 5 when only 1 monitor exists
            result = screen_capture.capture_screen(monitor_index=5)
            
            # Should fallback to monitor 0
            assert result == mock_image
            mock_screenshot.assert_called_once_with(region=(0, 0, 1920, 1080))
    
    @patch('platform.system')
    def test_capture_window_non_windows(self, mock_system, screen_capture):
        """Test window capture on non-Windows system."""
        mock_system.return_value = "Linux"
        
        with patch.object(screen_capture, 'capture_screen') as mock_capture_screen:
            mock_image = Mock()
            mock_capture_screen.return_value = mock_image
            
            result = screen_capture.capture_window_by_title("Test Window")
            
            assert result == mock_image
            mock_capture_screen.assert_called_once()
    
    @patch('screeninfo.get_monitors')
    def test_get_screen_size(self, mock_monitors, screen_capture):
        """Test getting screen size."""
        mock_monitor = Mock()
        mock_monitor.width = 1920
        mock_monitor.height = 1080
        mock_monitors.return_value = [mock_monitor]
        
        width, height = screen_capture.get_screen_size(monitor_index=0)
        
        assert width == 1920
        assert height == 1080


if __name__ == "__main__":
    pytest.main([__file__])
