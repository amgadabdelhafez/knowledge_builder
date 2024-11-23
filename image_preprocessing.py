import cv2
import numpy as np
from typing import Tuple

class ImagePreprocessor:
    def __init__(self):
        # Thresholds for white background detection
        self.white_threshold = 200  # Minimum brightness for white
        self.white_percentage_threshold = 0.70  # Minimum percentage of white pixels

    def is_likely_slide(self, image: np.ndarray) -> bool:
        """Determine if image is likely a slide based on white background and content"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Calculate percentage of white pixels
        white_pixels = np.sum(gray > self.white_threshold)
        total_pixels = gray.size
        white_percentage = white_pixels / total_pixels
        
        # Must have significant white background
        if white_percentage < self.white_percentage_threshold:
            return False
            
        # Check for content in the white areas
        # Apply edge detection to find content
        edges = cv2.Canny(gray, 50, 150)
        content_pixels = np.sum(edges > 0)
        content_percentage = content_pixels / total_pixels
        
        # Must have some content (between 1% and 30% of image)
        return 0.01 <= content_percentage <= 0.30

    def detect_skew(self, image: np.ndarray) -> float:
        """Detect skew angle of text in image"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply edge detection
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # Use Hough transform to detect lines
        lines = cv2.HoughLines(edges, 1, np.pi/180, 100)
        
        if lines is None:
            return 0.0
        
        # Calculate angles and find dominant angle
        angles = []
        for rho, theta in lines[:, 0]:
            angle = np.degrees(theta) % 180
            if angle < 45 or angle > 135:  # Consider only near-horizontal lines
                angles.append(angle)
        
        if not angles:
            return 0.0
        
        # Return median angle deviation from horizontal
        median_angle = np.median(angles)
        if median_angle > 90:
            median_angle -= 180
        
        return median_angle

    def correct_skew(self, image: np.ndarray, angle: float) -> np.ndarray:
        """Correct image skew by rotating"""
        if abs(angle) < 0.1:  # Skip if angle is negligible
            return image
            
        # Get image dimensions
        height, width = image.shape[:2]
        center = (width//2, height//2)
        
        # Create rotation matrix
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # Perform rotation
        rotated = cv2.warpAffine(
            image, 
            rotation_matrix, 
            (width, height),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )
        
        return rotated

    def remove_borders(self, image: np.ndarray) -> np.ndarray:
        """Remove dark borders from image"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Threshold to binary
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return image
            
        # Find largest contour (main content)
        main_contour = max(contours, key=cv2.contourArea)
        
        # Get bounding rectangle
        x, y, w, h = cv2.boundingRect(main_contour)
        
        # Add small padding
        pad = 10
        x = max(0, x - pad)
        y = max(0, y - pad)
        w = min(image.shape[1] - x, w + 2*pad)
        h = min(image.shape[0] - y, h + 2*pad)
        
        # Crop image
        return image[y:y+h, x:x+w]

    def detect_content_regions(self, image: np.ndarray) -> list:
        """Detect regions containing text or diagrams"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding
        binary = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter and sort content regions
        regions = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 100:  # Skip very small regions
                continue
            
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h if h > 0 else 0
            
            # Classify region type (text vs diagram)
            region_type = "text" if 0.1 <= aspect_ratio <= 15 else "diagram"
            
            regions.append({
                'bbox': (x, y, w, h),
                'area': area,
                'type': region_type
            })
        
        return sorted(regions, key=lambda x: x['bbox'][1])  # Sort by y-coordinate

    def enhance_text(self, image: np.ndarray) -> np.ndarray:
        """Enhance text visibility using adaptive methods"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Calculate average brightness
        avg_brightness = np.mean(gray)
        
        if avg_brightness < 127:
            # Dark background - invert image
            gray = cv2.bitwise_not(gray)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Apply bilateral filter to reduce noise while preserving edges
        denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)
        
        # Apply adaptive thresholding
        binary = cv2.adaptiveThreshold(
            denoised, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        
        return binary

    def preprocess_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """Complete preprocessing pipeline for OCR"""
        try:
            # Check if image is likely a slide
            if not self.is_likely_slide(image):
                return None
            
            # Detect and correct skew
            angle = self.detect_skew(image)
            deskewed = self.correct_skew(image, angle)
            
            # Remove borders
            cropped = self.remove_borders(deskewed)
            
            # Detect content regions
            regions = self.detect_content_regions(cropped)
            if not regions:
                return None
            
            # Enhance text
            enhanced = self.enhance_text(cropped)
            
            return enhanced
            
        except Exception as e:
            print(f"Error in preprocessing: {e}")
            return None
