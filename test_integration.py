import pytest
import os
import cv2
import numpy as np
from typing import List, Dict, Any
from text_processor import TextProcessor
from image_processor import ImageProcessor
from content_segment import align_transcript_with_slides
from test_utils import cleanup_directory, TEST_OUTPUT_PATH, TEST_SLIDES_PATH

class TestIntegration:
    def setUp(self):
        """Setup test environment"""
        cleanup_directory(TEST_OUTPUT_PATH)
        os.makedirs(TEST_OUTPUT_PATH, exist_ok=True)
        os.makedirs(TEST_SLIDES_PATH, exist_ok=True)
    
    def tearDown(self):
        """Cleanup test environment"""
        cleanup_directory(TEST_OUTPUT_PATH)

    def test_frame_extraction_and_analysis(self):
        """Test frame extraction and analysis"""
        self.setUp()
        try:
            print("\nTesting frame extraction and analysis...")
            
            # Create a test frame with text
            frame = np.ones((480, 640, 3), dtype=np.uint8) * 255
            cv2.putText(frame, "Test Frame Content", (50, 240),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            
            # Save test frame
            frame_path = os.path.join(TEST_SLIDES_PATH, "test_frame.jpg")
            cv2.imwrite(frame_path, frame)
            
            # Process frame
            image_processor = ImageProcessor()
            text_processor = TextProcessor()
            
            # Extract text
            print("Extracting text from frame...")
            extracted_text = image_processor.extract_text_from_image(frame_path)
            assert "Test" in extracted_text
            assert "Frame" in extracted_text
            print(f"Extracted text: {extracted_text}")
            
            # Extract keywords
            print("\nExtracting keywords...")
            keywords = text_processor.extract_keywords(extracted_text)
            assert len(keywords) > 0
            print(f"Keywords: {keywords}")
            
            # Classify content
            print("\nClassifying content...")
            content_type = text_processor.classify_domain(extracted_text)
            assert isinstance(content_type, str)
            print(f"Content type: {content_type}")
            
        except Exception as e:
            pytest.fail(f"Error in frame extraction and analysis test: {e}")
        finally:
            self.tearDown()

    def test_transcript_processing(self):
        """Test transcript processing and alignment"""
        self.setUp()
        try:
            print("\nTesting transcript processing...")
            
            # Create sample transcript and timestamps
            transcript = [
                {'text': 'Introduction to the topic', 'start': 0.0, 'duration': 5.0},
                {'text': 'Key concepts explained', 'start': 5.0, 'duration': 5.0},
                {'text': 'Technical details covered', 'start': 10.0, 'duration': 5.0},
                {'text': 'Summary and conclusion', 'start': 15.0, 'duration': 5.0}
            ]
            
            slide_timestamps = [0.0, 10.0, 15.0]  # Three slides
            
            # Process transcript
            text_processor = TextProcessor()
            
            print("Processing transcript segments...")
            for segment in transcript:
                # Extract keywords
                keywords = text_processor.extract_keywords(segment['text'])
                assert isinstance(keywords, list)
                
                # Classify content
                content_type = text_processor.classify_domain(segment['text'])
                assert isinstance(content_type, str)
                
                print(f"\nSegment: {segment['text']}")
                print(f"Keywords: {keywords}")
                print(f"Content type: {content_type}")
            
            # Test alignment
            print("\nTesting transcript alignment...")
            segments = align_transcript_with_slides(transcript, slide_timestamps)
            
            assert len(segments) == len(transcript)
            assert segments[0].slide_index == 0
            assert segments[2].slide_index == 1
            assert segments[3].slide_index == 2
            
            print("Transcript alignment successful")
            
        except Exception as e:
            pytest.fail(f"Error in transcript processing test: {e}")
        finally:
            self.tearDown()
