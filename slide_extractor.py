from typing import List, Tuple, Dict, Any, Optional
import os
import re
from video_metadata import VideoMetadata, Chapter
from image_processor import ImageProcessor
from text_processor import TextProcessor
from content_segment import ContentSegment, align_transcript_with_slides

class SlideExtractor:
    def __init__(self):
        self.image_processor = ImageProcessor()
        self.text_processor = TextProcessor()

    def _prepare_chapter_info(self, chapters: List[Chapter]) -> Dict:
        """Convert chapters list to dictionary with timing info"""
        chapter_info = {}
        for idx, chapter in enumerate(chapters, 1):
            chapter_info[idx] = {
                'title': chapter.title,
                'start_time': chapter.start_time,
                'end_time': chapter.end_time
            }
        return chapter_info

    def _should_skip_chapter(self, chapter_title: str) -> bool:
        """Determine if a chapter should be skipped based on its title"""
        # Convert to lowercase for case-insensitive matching
        title = chapter_title.lower()
        
        # Skip patterns
        skip_patterns = [
            r'intro',
            r'introduction',
            r'about\s+(?:us|company|speaker|me)',
            r'agenda',
            r'overview',
            r'welcome',
            r'opening',
            r'preface',
            r'disclaimer',
            r'background',
            r'outro',
            r'conclusion',
            r'closing',
            r'credits',
            r'thank\s+you',
            r'questions',
            r'q\s*&\s*a',
        ]
        
        # Check against skip patterns
        for pattern in skip_patterns:
            if re.search(pattern, title, re.IGNORECASE):
                return True
        
        return False

    def _calculate_samples_for_duration(self, duration: float, samples_per_minute: float) -> int:
        """Calculate number of samples for a given duration"""
        # Convert duration to minutes and multiply by samples_per_minute
        samples = int((duration / 60.0) * samples_per_minute)
        # Ensure at least 1 sample
        return max(1, samples)

    def process_video(
        self,
        video_path: str,
        output_folder: str,
        metadata: VideoMetadata,
        threshold: float = 0.99,
        max_frames: Optional[int] = None,
        duration_limit: Optional[int] = None,
        samples_per_minute: float = 2.0
    ) -> Tuple[List[str], List[float], List[Dict[str, Any]]]:
        """Process video to extract and analyze slides"""
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_folder, exist_ok=True)
            
            # Print chapter information if available
            if metadata.chapters:
                print("\nDetected chapters:")
                for i, chapter in enumerate(metadata.chapters, 1):
                    skip = self._should_skip_chapter(chapter.title)
                    status = "SKIP" if skip else "PROCESS"
                    duration = chapter.end_time - chapter.start_time
                    samples = self._calculate_samples_for_duration(duration, samples_per_minute)
                    print(f"{i}. [{status}] {chapter.title} ({chapter.start_time:.1f}s - {chapter.end_time:.1f}s) - {samples} samples")
            
            # Extract slides from video
            print("\nExtracting slides from video...")
            slide_paths = []
            slide_timestamps = []
            slide_analyses = []
            
            if metadata.chapters:
                # Prepare chapter info for image processor
                chapter_info = self._prepare_chapter_info(metadata.chapters)
                
                # Process each chapter
                for i, chapter in enumerate(metadata.chapters, 1):
                    # Skip introductory/outro chapters
                    if self._should_skip_chapter(chapter.title):
                        print(f"\nSkipping chapter: {chapter.title}")
                        continue
                    
                    print(f"\nProcessing chapter: {chapter.title}")
                    # Calculate samples for this chapter
                    duration = chapter.end_time - chapter.start_time
                    samples = self._calculate_samples_for_duration(duration, samples_per_minute)
                    
                    # Extract slides for this chapter
                    chapter_paths, chapter_timestamps = self.image_processor.extract_slides(
                        video_path,
                        output_folder,  # Pass the output folder directly
                        threshold,
                        max_samples=samples,
                        start_time=chapter.start_time,
                        end_time=chapter.end_time,
                        chapter_info=chapter_info
                    )
                    
                    # Add chapter slides
                    slide_paths.extend(chapter_paths)
                    slide_timestamps.extend(chapter_timestamps)
            else:
                # No chapters, process entire video
                # Skip first 60 seconds if no chapters (likely intro)
                start_time = 60 if not duration_limit or duration_limit > 60 else 0
                end_time = duration_limit if duration_limit else None
                
                # Calculate total samples
                video_duration = (end_time or metadata.length) - start_time
                total_samples = self._calculate_samples_for_duration(video_duration, samples_per_minute)
                
                slide_paths, slide_timestamps = self.image_processor.extract_slides(
                    video_path,
                    output_folder,  # Pass the output folder directly
                    threshold,
                    max_samples=total_samples,
                    start_time=start_time,
                    end_time=end_time
                )
            
            if not slide_paths:
                raise Exception("No slides extracted from video")
            
            # Process each slide
            print("\nAnalyzing slides...")
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
                    
                    # Keep slide's extracted text and content type
                    segment.extracted_text = analysis.get('extracted_text', '')
                    segment.content_type = analysis.get('content_type', 'unknown')
                    segment.confidence = analysis.get('confidence', 0.0)
                    
                    # Generate unique keywords for this segment by analyzing both
                    # the slide content and the transcript text
                    slide_keywords = set(analysis.get('keywords', []))
                    transcript_keywords = set(self.text_processor.extract_keywords(segment.transcript_text))
                    
                    # Combine keywords, prioritizing those that appear in both
                    common_keywords = slide_keywords.intersection(transcript_keywords)
                    unique_keywords = slide_keywords.union(transcript_keywords)
                    
                    # Sort keywords: common ones first, then others
                    segment.keywords = list(common_keywords) + list(unique_keywords - common_keywords)
                    
                    # Only include technical terms that appear in the transcript
                    slide_terms = set(analysis.get('technical_terms', []))
                    segment.technical_terms = [
                        term for term in slide_terms 
                        if term.lower() in segment.transcript_text.lower()
                    ]
                else:
                    # If no matching slide, use empty values
                    segment.extracted_text = ''
                    segment.keywords = []
                    segment.technical_terms = []
                    segment.content_type = 'unknown'
                    segment.confidence = 0.0
            
            return segments
            
        except Exception as e:
            print(f"Error processing transcript with slides: {e}")
            return []
