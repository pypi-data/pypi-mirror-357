"""
Main MCP server implementation for OmniParser UI automation.
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource
)

from .omniparser_client import OmniParserClient
from .automation.screen_capture import ScreenCapture
from .automation.mouse import MouseController
from .automation.keyboard import KeyboardController
from .window_manager.window_detector import WindowDetector
from .window_manager.window_controller import WindowController
from .tools.screen_tools import ScreenTools
from .tools.automation_tools import AutomationTools
from .tools.window_tools import WindowTools


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OmniParserMCPServer:
    """MCP Server for OmniParser UI automation."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the MCP server.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.server = Server("omniparser-mcp-server")
        
        # Initialize components
        self._initialize_components()
        
        # Register tools
        self._register_tools()
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file."""
        if config_path is None:
            # Look for config.json in current directory or parent directories
            current_dir = Path(__file__).parent
            for _ in range(5):  # Search up to 5 levels up
                config_file = current_dir / "config.json"
                if config_file.exists():
                    config_path = str(config_file)
                    break
                current_dir = current_dir.parent
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info(f"Loaded configuration from {config_path}")
                return config
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
        
        # Default configuration
        logger.info("Using default configuration")
        return {
            "omniparser": {
                "som_model_path": "weights/icon_detect/model.pt",
                "caption_model_name": "florence2",
                "caption_model_path": "weights/icon_caption_florence",
                "box_threshold": 0.05
            },
            "automation": {
                "screenshot_delay": 0.1,
                "action_delay": 0.5,
                "confidence_threshold": 0.8
            },
            "window_manager": {
                "supported_browsers": ["chrome", "firefox", "edge", "safari"],
                "supported_games": ["steam", "epic", "origin"],
                "window_detection_timeout": 5.0
            },
            "logging": {
                "level": "INFO",
                "file": "omniparser_mcp.log"
            }
        }
    
    def _initialize_components(self):
        """Initialize all components."""
        try:
            # Initialize OmniParser client
            self.omniparser_client = OmniParserClient(self.config["omniparser"])
            
            # Initialize automation components
            self.screen_capture = ScreenCapture(self.config["automation"])
            self.mouse_controller = MouseController(self.config["automation"])
            self.keyboard_controller = KeyboardController(self.config["automation"])
            
            # Initialize window management components
            self.window_detector = WindowDetector(self.config["window_manager"])
            self.window_controller = WindowController(self.config["automation"])
            
            # Initialize tool collections
            self.screen_tools = ScreenTools(self.omniparser_client, self.screen_capture)
            self.automation_tools = AutomationTools(
                self.mouse_controller, 
                self.keyboard_controller, 
                self.screen_tools
            )
            self.window_tools = WindowTools(self.window_detector, self.window_controller)
            
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
    
    def _register_tools(self):
        """Register MCP tools."""
        
        # Screen parsing tools
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List available tools."""
            tools = [
                Tool(
                    name="parse_screen",
                    description="Parse current screen or window to detect UI elements using OmniParser",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "window_title": {
                                "type": "string",
                                "description": "Title of window to capture (optional, captures full screen if not provided)"
                            },
                            "monitor_index": {
                                "type": "integer",
                                "description": "Monitor index for full screen capture (default: 0)",
                                "default": 0
                            }
                        }
                    }
                ),
                Tool(
                    name="find_element",
                    description="Find a specific UI element by description",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "description": {
                                "type": "string",
                                "description": "Description of the element to find"
                            },
                            "window_title": {
                                "type": "string",
                                "description": "Title of window to search in (optional)"
                            }
                        },
                        "required": ["description"]
                    }
                ),
                Tool(
                    name="click_element",
                    description="Click on a UI element identified by description",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "description": {
                                "type": "string",
                                "description": "Description of the element to click"
                            },
                            "window_title": {
                                "type": "string",
                                "description": "Title of window containing element (optional)"
                            },
                            "button": {
                                "type": "string",
                                "description": "Mouse button to use (left, right, middle)",
                                "default": "left"
                            },
                            "clicks": {
                                "type": "integer",
                                "description": "Number of clicks",
                                "default": 1
                            }
                        },
                        "required": ["description"]
                    }
                ),
                Tool(
                    name="type_text",
                    description="Type text at current cursor position",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "Text to type"
                            },
                            "clear_first": {
                                "type": "boolean",
                                "description": "Whether to clear existing text first",
                                "default": False
                            }
                        },
                        "required": ["text"]
                    }
                ),
                Tool(
                    name="type_in_element",
                    description="Click on an element and type text into it",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "description": {
                                "type": "string",
                                "description": "Description of the element to type in"
                            },
                            "text": {
                                "type": "string",
                                "description": "Text to type"
                            },
                            "window_title": {
                                "type": "string",
                                "description": "Title of window containing element (optional)"
                            },
                            "clear_first": {
                                "type": "boolean",
                                "description": "Whether to clear existing text first",
                                "default": True
                            }
                        },
                        "required": ["description", "text"]
                    }
                ),
                Tool(
                    name="list_windows",
                    description="List all available windows",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "window_type": {
                                "type": "string",
                                "description": "Filter by window type (browser, game, or all)",
                                "enum": ["browser", "game", "all"]
                            }
                        }
                    }
                ),
                Tool(
                    name="focus_window",
                    description="Focus a window by title pattern",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title_pattern": {
                                "type": "string",
                                "description": "Pattern to match in window title"
                            },
                            "exact_match": {
                                "type": "boolean",
                                "description": "Whether to match exactly or partially",
                                "default": False
                            }
                        },
                        "required": ["title_pattern"]
                    }
                ),
                Tool(
                    name="capture_screenshot",
                    description="Capture screenshot without parsing",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "window_title": {
                                "type": "string",
                                "description": "Title of window to capture (optional)"
                            },
                            "monitor_index": {
                                "type": "integer",
                                "description": "Monitor index for full screen capture",
                                "default": 0
                            }
                        }
                    }
                )
            ]
            
            return ListToolsResult(tools=tools)

        @self.server.call_tool()
        async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
            """Handle tool calls."""
            try:
                tool_name = request.params.name
                arguments = request.params.arguments or {}

                # Screen parsing tools
                if tool_name == "parse_screen":
                    result = self.screen_tools.parse_screen(
                        window_title=arguments.get("window_title"),
                        monitor_index=arguments.get("monitor_index", 0)
                    )

                elif tool_name == "find_element":
                    result = self.screen_tools.find_element(
                        description=arguments["description"],
                        window_title=arguments.get("window_title")
                    )

                elif tool_name == "capture_screenshot":
                    result = self.screen_tools.capture_screenshot(
                        window_title=arguments.get("window_title"),
                        monitor_index=arguments.get("monitor_index", 0)
                    )

                # Automation tools
                elif tool_name == "click_element":
                    result = self.automation_tools.click_element(
                        description=arguments["description"],
                        window_title=arguments.get("window_title"),
                        button=arguments.get("button", "left"),
                        clicks=arguments.get("clicks", 1)
                    )

                elif tool_name == "type_text":
                    result = self.automation_tools.type_text(
                        text=arguments["text"],
                        clear_first=arguments.get("clear_first", False)
                    )

                elif tool_name == "type_in_element":
                    result = self.automation_tools.type_in_element(
                        description=arguments["description"],
                        text=arguments["text"],
                        window_title=arguments.get("window_title"),
                        clear_first=arguments.get("clear_first", True)
                    )

                # Window management tools
                elif tool_name == "list_windows":
                    result = self.window_tools.list_windows(
                        window_type=arguments.get("window_type")
                    )

                elif tool_name == "focus_window":
                    result = self.window_tools.focus_window(
                        title_pattern=arguments["title_pattern"],
                        exact_match=arguments.get("exact_match", False)
                    )

                else:
                    result = {
                        "success": False,
                        "error": f"Unknown tool: {tool_name}"
                    }

                # Format result for MCP
                if result.get("success", False):
                    content = [TextContent(type="text", text=json.dumps(result, indent=2))]

                    # Add image content if available
                    if "labeled_image_base64" in result:
                        content.append(ImageContent(
                            type="image",
                            data=result["labeled_image_base64"],
                            mimeType="image/png"
                        ))
                    elif "image_base64" in result:
                        content.append(ImageContent(
                            type="image",
                            data=result["image_base64"],
                            mimeType="image/png"
                        ))

                    return CallToolResult(content=content)
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=json.dumps(result, indent=2))],
                        isError=True
                    )

            except Exception as e:
                logger.error(f"Error handling tool call {request.params.name}: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")],
                    isError=True
                )

    async def run(self):
        """Run the MCP server."""
        logger.info("Starting OmniParser MCP Server...")

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="omniparser-mcp-server",
                    server_version="0.1.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities={}
                    )
                )
            )


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="OmniParser MCP Server")
    parser.add_argument("--config", help="Path to configuration file")
    args = parser.parse_args()

    try:
        server = OmniParserMCPServer(config_path=args.config)
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main()
