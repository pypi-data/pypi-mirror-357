"""
OmniParser client for UI screenshot parsing and element detection.
"""

import sys
import os
import json
import base64
import io
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path

import torch
from PIL import Image
import numpy as np

# Add OmniParser path to sys.path
OMNIPARSER_PATH = Path(__file__).parent.parent.parent.parent / "OmniParser-master"
sys.path.insert(0, str(OMNIPARSER_PATH))

try:
    from util.utils import get_som_labeled_img, get_caption_model_processor, get_yolo_model, check_ocr_box
except ImportError as e:
    raise ImportError(f"Failed to import OmniParser utilities. Make sure OmniParser is properly installed: {e}")


class OmniParserClient:
    """Client for OmniParser model to parse UI screenshots."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize OmniParser client.
        
        Args:
            config: Configuration dictionary containing model paths and settings
        """
        self.config = config
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # Initialize models
        self._load_models()
        
    def _load_models(self):
        """Load OmniParser models."""
        try:
            # Load SOM (Set-of-Mark) detection model
            som_model_path = self.config.get('som_model_path')
            if not som_model_path or not os.path.exists(som_model_path):
                raise FileNotFoundError(f"SOM model not found at: {som_model_path}")
            
            self.som_model = get_yolo_model(model_path=som_model_path)
            self.som_model.to(self.device)
            
            # Load caption model
            caption_model_name = self.config.get('caption_model_name', 'florence2')
            caption_model_path = self.config.get('caption_model_path')
            
            if not caption_model_path or not os.path.exists(caption_model_path):
                raise FileNotFoundError(f"Caption model not found at: {caption_model_path}")
            
            self.caption_model_processor = get_caption_model_processor(
                model_name=caption_model_name,
                model_name_or_path=caption_model_path,
                device=self.device
            )
            
            print(f"OmniParser models loaded successfully on {self.device}")
            
        except Exception as e:
            raise RuntimeError(f"Failed to load OmniParser models: {e}")
    
    def parse_image(self, image: Image.Image) -> Tuple[Image.Image, List[Dict]]:
        """
        Parse UI screenshot to detect interactive elements.
        
        Args:
            image: PIL Image to parse
            
        Returns:
            Tuple of (labeled_image, parsed_elements_list)
        """
        try:
            print(f'Parsing image of size: {image.size}')
            
            # Calculate box overlay ratio for drawing
            box_overlay_ratio = max(image.size) / 3200
            draw_bbox_config = {
                'text_scale': 0.8 * box_overlay_ratio,
                'text_thickness': max(int(2 * box_overlay_ratio), 1),
                'text_padding': max(int(3 * box_overlay_ratio), 1),
                'thickness': max(int(3 * box_overlay_ratio), 1),
            }
            
            # Perform OCR to detect text elements
            (text, ocr_bbox), _ = check_ocr_box(
                image, 
                display_img=False, 
                output_bb_format='xyxy', 
                easyocr_args={'text_threshold': 0.8}, 
                use_paddleocr=False
            )
            
            # Get SOM labeled image and parsed content
            labeled_img, label_coordinates, parsed_content_list = get_som_labeled_img(
                image, 
                self.som_model, 
                BOX_TRESHOLD=self.config.get('box_threshold', 0.05),
                output_coord_in_ratio=True, 
                ocr_bbox=ocr_bbox,
                draw_bbox_config=draw_bbox_config, 
                caption_model_processor=self.caption_model_processor, 
                ocr_text=text,
                use_local_semantics=True, 
                iou_threshold=0.7, 
                scale_img=False, 
                batch_size=128
            )
            
            return labeled_img, parsed_content_list
            
        except Exception as e:
            raise RuntimeError(f"Failed to parse image: {e}")
    
    def parse_image_from_base64(self, image_base64: str) -> Tuple[Image.Image, List[Dict]]:
        """
        Parse UI screenshot from base64 encoded image.
        
        Args:
            image_base64: Base64 encoded image string
            
        Returns:
            Tuple of (labeled_image, parsed_elements_list)
        """
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_bytes))
            
            return self.parse_image(image)
            
        except Exception as e:
            raise RuntimeError(f"Failed to parse base64 image: {e}")
    
    def find_elements_by_description(self, parsed_elements: List[Dict], description: str) -> List[Dict]:
        """
        Find elements matching a description.
        
        Args:
            parsed_elements: List of parsed elements from parse_image
            description: Description to search for
            
        Returns:
            List of matching elements
        """
        matching_elements = []
        description_lower = description.lower()
        
        for element in parsed_elements:
            element_text = element.get('text', '').lower()
            element_description = element.get('description', '').lower()
            
            if (description_lower in element_text or 
                description_lower in element_description or
                any(desc_word in element_text for desc_word in description_lower.split()) or
                any(desc_word in element_description for desc_word in description_lower.split())):
                matching_elements.append(element)
        
        return matching_elements
    
    def get_element_center(self, element: Dict) -> Tuple[int, int]:
        """
        Get the center coordinates of an element.
        
        Args:
            element: Element dictionary with coordinate information
            
        Returns:
            Tuple of (x, y) center coordinates
        """
        if 'coordinates' in element:
            coords = element['coordinates']
            if isinstance(coords, list) and len(coords) >= 4:
                x1, y1, x2, y2 = coords[:4]
                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)
                return center_x, center_y
        
        raise ValueError("Element does not contain valid coordinates")
