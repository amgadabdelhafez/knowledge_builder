from typing import List, Tuple, Dict, Any
import os
from video_metadata import VideoMetadata
from image_processor import ImageProcessor
from text_processor import TextProcessor
from content_segment import ContentSegment, align_transcript_with_slides

class SlideExtractor:
    def __init__(self):
        self.image_processor = ImageProcessor()
        self.text_processor = TextProcessor()

    def process_video(
        self,
        video_path: str,
        output_folder: str,
        metadata: VideoMetadata,
        threshold: float = 0.95
    ) -> Tuple[List[str], List[float], List[Dict[str, Any]]]:
        """Process video to extract and analyze slides"""
        try:
            # Create slides directory if it doesn't exist
            slides_dir = os.path.join(output_folder, 'slides')
            os.makedirs(slides_dir, exist_ok=True)
            
            # Extract slides from video
            print("Extracting slides from video...")
            slide_paths, slide_timestamps = self.image_processor.extract_slides(
                video_path,
                slides_dir,
                threshold
            )
            
            if not slide_paths:
                raise Exception("No slides extracted from video")
            
            # Process each slide
            print("Analyzing slides...")
            slide_analyses = []
            for slide_path in slide_paths:
                analysis = self._analyze_slide(slide_path)
                slide_analyses.append(analysis)
            
            return slide_paths, slide_timestamps, slide_analyses
            
        except Exception as e:
            print(f"Error processing video for slides: {e}")
            return [], [], []

    def _analyze_slide(self, slide_path: str) -> Dict[str, Any]:
        """Analyze a single slide"""
        try:
            # Extract text from slide
            extracted_text = self.image_processor.extract_text_from_image(slide_path)
            
            # Classify content type
            content_type, confidence = self.image_processor.classify_image_content(slide_path)
            
            # Extract keywords and technical terms
            keywords = self.text_processor.extract_keywords(extracted_text)
            technical_terms = self.text_processor.detect_technical_terms(extracted_text)
            
            # Detect diagrams if present
            diagrams = self.image_processor.detect_diagrams(slide_path)
            
            return {
                'extracted_text': extracted_text,
                'content_type': content_type,
                'confidence': confidence,
                'keywords': keywords,
                'technical_terms': technical_terms,
                'diagrams': diagrams
            }
        except Exception as e:
            print(f"Error analyzing slide {slide_path}: {e}")
            return {
                'extracted_text': '',
                'content_type': 'unknown',
                'confidence': 0.0,
                'keywords': [],
                'technical_terms': [],
                'diagrams': []
            }

    def process_transcript_with_slides(
        self,
        transcript: List[Dict[str, Any]],
        slide_paths: List[str],
        slide_timestamps: List[float],
        slide_analyses: List[Dict[str, Any]]
    ) -> List[ContentSegment]:
        """Process transcript with slide timing information"""
        try:
            # Align transcript with slides
            segments = align_transcript_with_slides(transcript, slide_timestamps)
            
            # Enhance segments with slide analysis
            for segment in segments:
                if 0 <= segment.slide_index < len(slide_analyses):
                    analysis = slide_analyses[segment.slide_index]
                    segment.extracted_text = analysis['extracted_text']
                    segment.keywords = analysis['keywords']
                    segment.technical_terms = analysis['technical_terms']
                    segment.content_type = analysis['content_type']
                    segment.confidence = analysis['confidence']
            
            return segments
            
        except Exception as e:
            print(f"Error processing transcript with slides: {e}")
            return []
