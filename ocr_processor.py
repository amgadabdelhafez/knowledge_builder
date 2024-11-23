import pytesseract
import re
import numpy as np
from typing import List

class OCRProcessor:
    def __init__(self):
        # OCR settings
        self.min_text_length = 10
        self.min_word_count = 3

    def clean_text(self, text: str) -> str:
        """Enhanced text cleaning"""
        # Remove common noise patterns
        noise_patterns = [
            r'\s+',          # Multiple whitespace
            r'[|_=]{2,}',    # Repeated separators
            r'[\u0000-\u001F\u007F-\u009F]',  # Control characters
            r'[^\x00-\x7F]+' # Non-ASCII characters
        ]
        
        cleaned = text
        for pattern in noise_patterns:
            cleaned = re.sub(pattern, ' ', cleaned)
        
        # Normalize whitespace
        cleaned = ' '.join(cleaned.split())
        
        # Remove single characters except 'a' and 'i'
        words = cleaned.split()
        cleaned = ' '.join(w for w in words if len(w) > 1 or w.lower() in {'a', 'i'})
        
        return cleaned.strip()

    def extract_text(self, image: np.ndarray) -> str:
        """Extract text from image using OCR"""
        try:
            # Configure OCR
            custom_config = r'--oem 3 --psm 6'
            
            # Perform OCR with increased timeout
            pytesseract.pytesseract.timeout = 10
            text = pytesseract.image_to_string(image, config=custom_config)
            
            # Clean text
            cleaned = self.clean_text(text)
            
            return cleaned
            
        except Exception as e:
            print(f"Error extracting text: {e}")
            return ""

    def has_sufficient_text(self, text: str) -> bool:
        """Check if text content is sufficient"""
        # Remove common noise words
        noise_words = {'', ' ', '|', '-', '_', '=', '.', ',', ':', ';'}
        cleaned_text = ''.join(c for c in text if c not in noise_words)
        
        # Count alphanumeric characters
        alpha_count = sum(c.isalnum() for c in cleaned_text)
        
        # Count words
        words = [w for w in text.split() if len(w) > 1]
        word_count = len(words)
        
        return alpha_count >= self.min_text_length and word_count >= self.min_word_count

    def extract_keywords(self, text: str) -> List[str]:
        """Extract potential keywords from text"""
        # Split into words
        words = text.split()
        
        # Filter words
        keywords = []
        for word in words:
            # Keep words that:
            # 1. Are longer than 3 characters
            # 2. Start with a capital letter (potential proper nouns)
            # 3. Contain numbers (potential technical terms)
            if (len(word) > 3 and 
                (word[0].isupper() or 
                 any(c.isdigit() for c in word))):
                keywords.append(word)
        
        return list(set(keywords))  # Remove duplicates
