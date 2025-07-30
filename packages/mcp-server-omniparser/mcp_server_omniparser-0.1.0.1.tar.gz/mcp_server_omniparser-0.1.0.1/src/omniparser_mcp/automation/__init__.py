"""
Automation module for keyboard and mouse operations.
"""

from .keyboard import KeyboardController
from .mouse import MouseController
from .screen_capture import ScreenCapture

__all__ = ["KeyboardController", "MouseController", "ScreenCapture"]
