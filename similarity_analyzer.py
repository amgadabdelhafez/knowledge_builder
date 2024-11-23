import cv2
import numpy as np
from difflib import SequenceMatcher
from typing import Set, Tuple

class SimilarityAnalyzer:
    def __init__(self):
        self.text_similarity_threshold = 0.8
        self.visual_similarity_threshold = 0.85

    def calculate_visual_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Calculate visual similarity between two images"""
        try:
            # Resize images to same size
            size = (300, 300)  # Reduced size for efficiency
            img1_resized = cv2.resize(img1, size)
            img2_resized = cv2.resize(img2, size)
            
            # Convert to grayscale
            gray1 = cv2.cvtColor(img1_resized, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2_resized, cv2.COLOR_BGR2GRAY)
            
            # Calculate histograms
            hist1 = cv2.calcHist([gray1], [0], None, [256], [0, 256])
            hist2 = cv2.calcHist([gray2], [0], None, [256], [0, 256])
            
            # Normalize histograms
            cv2.normalize(hist1, hist1)
            cv2.normalize(hist2, hist2)
            
            # Compare histograms
            similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            
            return max(0, similarity)  # Ensure non-negative
            
        except Exception as e:
            print(f"Error calculating visual similarity: {e}")
            return 0.0

    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings"""
        if not text1 or not text2:
            return 0.0
        
        # Calculate string similarity
        string_ratio = SequenceMatcher(None, text1, text2).ratio()
        
        # Calculate word overlap
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
            
        overlap = len(words1.intersection(words2))
        overlap_ratio = overlap / max(len(words1), len(words2))
        
        # Combined similarity score
        return (string_ratio + overlap_ratio) / 2

    def get_text_features(self, text: str) -> Tuple[Set[str], Set[str]]:
        """Extract features from text for comparison"""
        # Convert to lowercase and split into words
        words = text.lower().split()
        
        # Get word bigrams
        bigrams = {f"{words[i]} {words[i+1]}" for i in range(len(words)-1)}
        
        return set(words), bigrams

    def is_similar(self, text1: str, text2: str, img1: np.ndarray = None, img2: np.ndarray = None) -> bool:
        """Determine if two slides are similar using both text and visual comparison"""
        # Calculate text similarity
        text_similarity = self.calculate_text_similarity(text1, text2)
        
        # If text similarity is very low, return False early
        if text_similarity < self.text_similarity_threshold / 2:
            return False
        
        # If text similarity is very high, return True early
        if text_similarity > self.text_similarity_threshold * 1.5:
            return True
        
        # If images are provided, include visual similarity in decision
        if img1 is not None and img2 is not None:
            visual_similarity = self.calculate_visual_similarity(img1, img2)
            
            # Combined decision using both similarities
            combined_similarity = (text_similarity + visual_similarity) / 2
            return combined_similarity > (self.text_similarity_threshold + self.visual_similarity_threshold) / 2
        
        # If no images provided, use only text similarity
        return text_similarity > self.text_similarity_threshold

    def find_similar_slides(self, current_text: str, current_image: np.ndarray, 
                          previous_texts: list, previous_images: list) -> bool:
        """Check if current slide is similar to any in history"""
        for prev_text, prev_image in zip(previous_texts, previous_images):
            if self.is_similar(current_text, prev_text, current_image, prev_image):
                return True
        return False
