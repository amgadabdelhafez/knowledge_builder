import os
import cv2
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass

from image_preprocessing import ImagePreprocessor
from ocr_processor import OCRProcessor
from similarity_analyzer import SimilarityAnalyzer

@dataclass
class SlideInfo:
    """Store slide information"""
    frame: np.ndarray
    timestamp: float
    text: str
    chapter: str
    chapter_index: int
    content_regions: List[Dict]

class ImageProcessor:
    def __init__(self):
        # Initialize specialized processors
        self.preprocessor = ImagePreprocessor()
        self.ocr = OCRProcessor()
        self.similarity = SimilarityAnalyzer()
        
        # Initialize state
        self.previous_slides: List[SlideInfo] = []
        self.history_size = 10
        self.slide_counter = 0  # Global counter for slide numbering

    def _save_slide(self, slide: SlideInfo, output_path: str) -> Tuple[str, float]:
        """Save a single slide with sequential numbering"""
        self.slide_counter += 1
        filename = f"{self.slide_counter:03d}.jpg"
        slide_path = os.path.join(output_path, filename)
        
        # Ensure the frame is not None and is valid
        if slide.frame is not None and slide.frame.size > 0:
            try:
                # Create output directory if it doesn't exist
                os.makedirs(output_path, exist_ok=True)
                
                # Save the image
                cv2.imwrite(slide_path, slide.frame)
                print(f"Saved slide {filename}")
                
                # Verify the file was saved
                if not os.path.exists(slide_path):
                    print(f"Error: Failed to save slide {filename}")
                    self.slide_counter -= 1  # Revert counter if save failed
                    return None, None
                
                return slide_path, slide.timestamp
            except Exception as e:
                print(f"Error saving slide {filename}: {e}")
                self.slide_counter -= 1  # Revert counter if save failed
        return None, None

    def _is_duplicate_slide(self, frame: np.ndarray, text: str) -> bool:
        """Check if slide is duplicate using similarity analyzer"""
        if not self.previous_slides:
            return False
            
        # Get previous texts and images
        prev_texts = [slide.text for slide in self.previous_slides[-self.history_size:]]
        prev_frames = [slide.frame for slide in self.previous_slides[-self.history_size:]]
        
        return self.similarity.find_similar_slides(text, frame, prev_texts, prev_frames)

    def extract_slides(
        self,
        video_path: str,
        output_path: str,
        threshold: float = 0.99,
        max_samples: Optional[int] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        chapter_info: Optional[Dict] = None
    ) -> Tuple[List[str], List[float]]:
        """Extract slides with improved white background and content detection"""
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_path, exist_ok=True)
        
        # Reset state for new video, but keep slide counter
        self.previous_slides = []
        slide_paths = []
        slide_timestamps = []
        
        # Open video file
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception("Could not open video file")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Calculate start and end frames
        start_frame = int(start_time * fps) if start_time is not None else 0
        end_frame = int(end_time * fps) if end_time is not None else total_frames
        
        # Set position to start frame
        if start_frame > 0:
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        # Calculate frame interval
        frame_range = end_frame - start_frame
        if max_samples and max_samples > 0:
            frame_interval = frame_range // max_samples
        else:
            minutes = frame_range / fps / 60
            max_samples = int(minutes * 2)
            frame_interval = frame_range // max_samples if max_samples > 0 else frame_range
        
        frame_interval = max(1, frame_interval)
        
        print(f"\nExtracting slides over {frame_range/fps:.1f} seconds...")
        
        frame_idx = start_frame
        processed_samples = 0
        
        last_percentage = -1
        current_chapter = None
        current_chapter_idx = 0
        
        while cap.isOpened() and frame_idx < end_frame:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Update progress
            percentage = int((frame_idx - start_frame) * 100 / frame_range)
            if percentage != last_percentage:
                print(f"\rProgress: {percentage}%", end="", flush=True)
                last_percentage = percentage
            
            # Update chapter info if provided
            if chapter_info:
                timestamp = frame_idx / fps
                for idx, chapter in chapter_info.items():
                    if chapter['start_time'] <= timestamp < chapter['end_time']:
                        if current_chapter != chapter['title']:
                            current_chapter = chapter['title']
                            current_chapter_idx = idx
            
            # Check if frame is likely a slide
            if not self.preprocessor.is_likely_slide(frame):
                frame_idx += frame_interval
                processed_samples += 1
                continue
            
            # Preprocess frame for OCR
            processed_frame = self.preprocessor.preprocess_for_ocr(frame)
            if processed_frame is None:
                frame_idx += frame_interval
                processed_samples += 1
                continue
            
            # Detect content regions
            content_regions = self.preprocessor.detect_content_regions(frame)
            if not content_regions:
                frame_idx += frame_interval
                processed_samples += 1
                continue
            
            # Extract text from frame
            text = self.ocr.extract_text(processed_frame)
            
            # Skip if insufficient text
            if not self.ocr.has_sufficient_text(text):
                frame_idx += frame_interval
                processed_samples += 1
                continue
            
            # Skip if duplicate
            if self._is_duplicate_slide(frame, text):
                frame_idx += frame_interval
                processed_samples += 1
                continue
            
            # Store slide info
            timestamp = frame_idx / fps
            slide_info = SlideInfo(
                frame=frame.copy(),
                timestamp=timestamp,
                text=text,
                chapter=current_chapter or "Unknown",
                chapter_index=current_chapter_idx,
                content_regions=content_regions
            )
            self.previous_slides.append(slide_info)
            
            # Save slide immediately
            slide_path, slide_timestamp = self._save_slide(slide_info, output_path)
            if slide_path and slide_timestamp:
                slide_paths.append(slide_path)
                slide_timestamps.append(slide_timestamp)
                print(f"\nExtracted and saved slide {len(slide_paths)}")
            
            frame_idx += frame_interval
            processed_samples += 1
        
        cap.release()
        print(f"\nExtracted and saved {len(slide_paths)} slides")
        
        return slide_paths, slide_timestamps

    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from saved image"""
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                raise Exception(f"Could not read image: {image_path}")
            
            # Check if image is likely a slide
            if not self.preprocessor.is_likely_slide(img):
                return ""
            
            # Preprocess and extract text
            processed = self.preprocessor.preprocess_for_ocr(img)
            if processed is None:
                return ""
                
            return self.ocr.extract_text(processed)
            
        except Exception as e:
            print(f"Error extracting text from {image_path}: {e}")
            return ""

    def classify_image_content(self, image_path: str) -> Tuple[str, float]:
        """Classify image content type and return confidence"""
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                return "unknown", 0.0
            
            # Check if image is likely a slide
            if not self.preprocessor.is_likely_slide(img):
                return "unknown", 0.0
            
            # Detect content regions
            regions = self.preprocessor.detect_content_regions(img)
            if not regions:
                return "unknown", 0.0
            
            # Count region types
            text_regions = sum(1 for r in regions if r['type'] == 'text')
            diagram_regions = sum(1 for r in regions if r['type'] == 'diagram')
            
            total_regions = len(regions)
            if total_regions == 0:
                return "unknown", 0.0
            
            # Calculate confidence based on region distribution
            if text_regions > diagram_regions:
                confidence = text_regions / total_regions
                return "text", confidence
            elif diagram_regions > text_regions:
                confidence = diagram_regions / total_regions
                return "diagram", confidence
            else:
                return "mixed", 0.8
                
        except Exception as e:
            print(f"Error classifying image {image_path}: {e}")
            return "unknown", 0.0

    def detect_diagrams(self, image_path: str) -> List[Dict[str, Any]]:
        """Detect diagrams in image"""
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                return []
            
            # Check if image is likely a slide
            if not self.preprocessor.is_likely_slide(img):
                return []
            
            # Detect content regions
            regions = self.preprocessor.detect_content_regions(img)
            
            # Filter for diagram regions
            diagrams = []
            for region in regions:
                if region['type'] != 'diagram':
                    continue
                
                x, y, w, h = region['bbox']
                
                # Extract text from region
                roi = img[y:y+h, x:x+w]
                processed_roi = self.preprocessor.preprocess_for_ocr(roi)
                if processed_roi is not None:
                    text = self.ocr.extract_text(processed_roi)
                else:
                    text = ""
                
                # Store diagram info
                diagrams.append({
                    'bbox': (x, y, w, h),
                    'area': region['area'],
                    'text': text
                })
            
            return diagrams
            
        except Exception as e:
            print(f"Error detecting diagrams in {image_path}: {e}")
            return []
