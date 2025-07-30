"""
Tests for OmniParser client functionality.
"""

import pytest
import json
import base64
import io
from PIL import Image
from unittest.mock import Mock, patch, MagicMock

from src.omniparser_mcp.omniparser_client import OmniParserClient


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    return {
        "som_model_path": "test_weights/icon_detect/model.pt",
        "caption_model_name": "florence2",
        "caption_model_path": "test_weights/icon_caption_florence",
        "box_threshold": 0.05
    }


@pytest.fixture
def sample_image():
    """Create a sample test image."""
    # Create a simple test image
    image = Image.new('RGB', (800, 600), color='white')
    return image


@pytest.fixture
def sample_image_base64(sample_image):
    """Convert sample image to base64."""
    buffer = io.BytesIO()
    sample_image.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode()


@pytest.fixture
def mock_parsed_elements():
    """Mock parsed elements from OmniParser."""
    return [
        {
            "text": "Submit Button",
            "description": "clickable button",
            "coordinates": [100, 50, 200, 80],
            "confidence": 0.95
        },
        {
            "text": "Username",
            "description": "text input field",
            "coordinates": [50, 100, 300, 130],
            "confidence": 0.90
        },
        {
            "text": "Login",
            "description": "clickable link",
            "coordinates": [400, 200, 450, 220],
            "confidence": 0.85
        }
    ]


class TestOmniParserClient:
    """Test cases for OmniParserClient."""
    
    @patch('src.omniparser_mcp.omniparser_client.get_yolo_model')
    @patch('src.omniparser_mcp.omniparser_client.get_caption_model_processor')
    @patch('torch.cuda.is_available')
    def test_init_success(self, mock_cuda, mock_caption, mock_yolo, mock_config):
        """Test successful initialization of OmniParserClient."""
        mock_cuda.return_value = False
        mock_yolo.return_value = Mock()
        mock_caption.return_value = Mock()
        
        with patch('os.path.exists', return_value=True):
            client = OmniParserClient(mock_config)
            
            assert client.config == mock_config
            assert client.device == 'cpu'
            mock_yolo.assert_called_once()
            mock_caption.assert_called_once()
    
    @patch('src.omniparser_mcp.omniparser_client.get_yolo_model')
    @patch('src.omniparser_mcp.omniparser_client.get_caption_model_processor')
    def test_init_missing_model_files(self, mock_caption, mock_yolo, mock_config):
        """Test initialization with missing model files."""
        with patch('os.path.exists', return_value=False):
            with pytest.raises(FileNotFoundError):
                OmniParserClient(mock_config)
    
    @patch('src.omniparser_mcp.omniparser_client.get_som_labeled_img')
    @patch('src.omniparser_mcp.omniparser_client.check_ocr_box')
    def test_parse_image_success(self, mock_ocr, mock_som, sample_image, mock_parsed_elements):
        """Test successful image parsing."""
        # Mock OCR results
        mock_ocr.return_value = (["text1", "text2"], []), None
        
        # Mock SOM results
        mock_labeled_image = Image.new('RGB', (800, 600), color='red')
        mock_som.return_value = (mock_labeled_image, [], mock_parsed_elements)
        
        # Create client with mocked models
        with patch('src.omniparser_mcp.omniparser_client.get_yolo_model'), \
             patch('src.omniparser_mcp.omniparser_client.get_caption_model_processor'), \
             patch('os.path.exists', return_value=True):
            
            client = OmniParserClient({
                "som_model_path": "test_path",
                "caption_model_name": "florence2",
                "caption_model_path": "test_path",
                "box_threshold": 0.05
            })
            
            labeled_img, parsed_elements = client.parse_image(sample_image)
            
            assert isinstance(labeled_img, Image.Image)
            assert parsed_elements == mock_parsed_elements
            mock_ocr.assert_called_once()
            mock_som.assert_called_once()
    
    def test_parse_image_from_base64(self, sample_image_base64, mock_parsed_elements):
        """Test parsing image from base64 string."""
        with patch.object(OmniParserClient, 'parse_image') as mock_parse:
            mock_labeled_image = Image.new('RGB', (800, 600), color='blue')
            mock_parse.return_value = (mock_labeled_image, mock_parsed_elements)
            
            with patch('src.omniparser_mcp.omniparser_client.get_yolo_model'), \
                 patch('src.omniparser_mcp.omniparser_client.get_caption_model_processor'), \
                 patch('os.path.exists', return_value=True):
                
                client = OmniParserClient({
                    "som_model_path": "test_path",
                    "caption_model_name": "florence2", 
                    "caption_model_path": "test_path"
                })
                
                labeled_img, parsed_elements = client.parse_image_from_base64(sample_image_base64)
                
                assert isinstance(labeled_img, Image.Image)
                assert parsed_elements == mock_parsed_elements
                mock_parse.assert_called_once()
    
    def test_find_elements_by_description(self, mock_parsed_elements):
        """Test finding elements by description."""
        with patch('src.omniparser_mcp.omniparser_client.get_yolo_model'), \
             patch('src.omniparser_mcp.omniparser_client.get_caption_model_processor'), \
             patch('os.path.exists', return_value=True):
            
            client = OmniParserClient({
                "som_model_path": "test_path",
                "caption_model_name": "florence2",
                "caption_model_path": "test_path"
            })
            
            # Test finding button
            results = client.find_elements_by_description(mock_parsed_elements, "button")
            assert len(results) == 1
            assert "Submit Button" in results[0]["text"]
            
            # Test finding input field
            results = client.find_elements_by_description(mock_parsed_elements, "input")
            assert len(results) == 1
            assert "Username" in results[0]["text"]
            
            # Test no matches
            results = client.find_elements_by_description(mock_parsed_elements, "nonexistent")
            assert len(results) == 0
    
    def test_get_element_center(self, mock_parsed_elements):
        """Test getting element center coordinates."""
        with patch('src.omniparser_mcp.omniparser_client.get_yolo_model'), \
             patch('src.omniparser_mcp.omniparser_client.get_caption_model_processor'), \
             patch('os.path.exists', return_value=True):
            
            client = OmniParserClient({
                "som_model_path": "test_path",
                "caption_model_name": "florence2",
                "caption_model_path": "test_path"
            })
            
            element = mock_parsed_elements[0]  # Submit Button: [100, 50, 200, 80]
            center_x, center_y = client.get_element_center(element)
            
            assert center_x == 150  # (100 + 200) / 2
            assert center_y == 65   # (50 + 80) / 2
    
    def test_get_element_center_invalid_coordinates(self):
        """Test getting center with invalid coordinates."""
        with patch('src.omniparser_mcp.omniparser_client.get_yolo_model'), \
             patch('src.omniparser_mcp.omniparser_client.get_caption_model_processor'), \
             patch('os.path.exists', return_value=True):
            
            client = OmniParserClient({
                "som_model_path": "test_path",
                "caption_model_name": "florence2",
                "caption_model_path": "test_path"
            })
            
            # Element without coordinates
            element = {"text": "test", "description": "test"}
            
            with pytest.raises(ValueError):
                client.get_element_center(element)
            
            # Element with invalid coordinates
            element = {"coordinates": [100, 50]}  # Not enough coordinates
            
            with pytest.raises(ValueError):
                client.get_element_center(element)


if __name__ == "__main__":
    pytest.main([__file__])
