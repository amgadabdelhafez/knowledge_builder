import cv2
import numpy as np
import pytesseract
from PIL import Image
import hashlib
from typing import List, Tuple, Dict, Any
from transformers import AutoImageProcessor, AutoModelForImageClassification
import torch

class ImageProcessor:
    def __init__(self):
        # Initialize image classification components
        self.image_processor = AutoImageProcessor.from_pretrained("microsoft/resnet-50")
        self.image_model = AutoModelForImageClassification.from_pretrained("microsoft/resnet-50")
        
        # Content type categories
        self.content_categories = [
            "code_snippet",
            "network_diagram",
            "system_architecture",
            "data_flow",
            "algorithm_explanation",
            "api_documentation",
            "database_schema",
            "infrastructure_diagram",
            "security_architecture",
            "deployment_diagram"
        ]

    def extract_slides(
        self,
        video_path: str,
        output_folder: str,
        threshold: float = 0.95
    ) -> Tuple[List[str], List[float]]:
        """Extract unique slides from video"""
        try:
            cap = cv2.VideoCapture(video_path)
            frame_count = 0
            slide_paths = []
            slide_timestamps = []
            prev_frame_hash = None
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Process every 5th frame for efficiency
                if frame_count % 5 != 0:
                    frame_count += 1
                    continue
                
                # Calculate frame hash for comparison
                frame_hash = self._calculate_frame_hash(frame)
                
                if prev_frame_hash is None or self._hash_difference(frame_hash, prev_frame_hash) > threshold:
                    # Save frame as slide
                    slide_path = f"{output_folder}/slide_{len(slide_paths):03d}.jpg"
                    cv2.imwrite(slide_path, frame)
                    slide_paths.append(slide_path)
                    
                    # Record timestamp
                    timestamp = frame_count / cap.get(cv2.CAP_PROP_FPS)
                    slide_timestamps.append(timestamp)
                    
                    prev_frame_hash = frame_hash
                
                frame_count += 1
            
            cap.release()
            return slide_paths, slide_timestamps
            
        except Exception as e:
            print(f"Error extracting slides: {e}")
            return [], []

    def _calculate_frame_hash(self, frame: np.ndarray) -> str:
        """Calculate perceptual hash of frame"""
        # Resize and convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (32, 32))
        # Calculate hash
        return hashlib.md5(resized.tobytes()).hexdigest()

    def _hash_difference(self, hash1: str, hash2: str) -> float:
        """Calculate difference between two hashes"""
        return sum(c1 != c2 for c1, c2 in zip(hash1, hash2)) / len(hash1)

    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from image using OCR"""
        try:
            # Load image and convert to grayscale
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply thresholding to get better OCR results
            _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            
            # Extract text using pytesseract
            text = pytesseract.image_to_string(binary)
            return text.strip()
            
        except Exception as e:
            print(f"Error extracting text from image: {e}")
            return ""

    def classify_image_content(self, image_path: str) -> Tuple[str, float]:
        """Classify image content type"""
        try:
            # Load and preprocess image
            image = Image.open(image_path)
            inputs = self.image_processor(image, return_tensors="pt")
            
            # Get model predictions
            with torch.no_grad():
                outputs = self.image_model(**inputs)
                probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
                
            # Get predicted class and confidence
            pred_idx = probs.argmax().item()
            confidence = probs[0][pred_idx].item()
            
            # Map to content category
            category_idx = pred_idx % len(self.content_categories)
            content_type = self.content_categories[category_idx]
            
            return content_type, confidence
            
        except Exception as e:
            print(f"Error classifying image: {e}")
            return "unknown", 0.0

    def detect_diagrams(self, image_path: str) -> List[Dict[str, Any]]:
        """Detect and analyze diagrams in image"""
        try:
            # Load image
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect edges
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            diagrams = []
            for contour in contours:
                # Get bounding box
                x, y, w, h = cv2.boundingRect(contour)
                
                # Extract region
                roi = gray[y:y+h, x:x+w]
                
                # Get text in region
                text = pytesseract.image_to_string(roi)
                
                if text.strip():
                    diagrams.append({
                        'position': {'x': x, 'y': y, 'width': w, 'height': h},
                        'text': text.strip(),
                        'type': self._classify_diagram_type(roi, text)
                    })
            
            return diagrams
            
        except Exception as e:
            print(f"Error detecting diagrams: {e}")
            return []

    def _classify_diagram_type(self, image: np.ndarray, text: str) -> str:
        """Classify type of diagram based on image and text"""
        # Simple heuristic based on text content
        text = text.lower()
        if any(word in text for word in ['network', 'topology']):
            return 'network_diagram'
        elif any(word in text for word in ['class', 'object', 'inheritance']):
            return 'class_diagram'
        elif any(word in text for word in ['flow', 'process']):
            return 'flow_diagram'
        elif any(word in text for word in ['database', 'entity', 'relation']):
            return 'database_diagram'
        else:
            return 'generic_diagram'
