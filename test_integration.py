import pytest
import os
import shutil
from typing import List, Dict, Any
from video_downloader import VideoDownloader
from image_processor import ImageProcessor
from text_processor import TextProcessor
from slide_extractor import SlideExtractor
from content_segment import ContentSegment, align_transcript_with_slides

# Test data - Using a short video segment
TEST_VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Short video for testing

def cleanup_directory(path: str):
    """Safely cleanup a directory and all its contents"""
    try:
        if os.path.exists(path):
            shutil.rmtree(path)
    except Exception as e:
        print(f"Warning: Failed to cleanup {path}: {e}")

class TestIntegration:
    def setUp(self):
        """Setup test environment"""
        self.output_path = "test_output"
        self.slides_path = os.path.join(self.output_path, "slides")
        cleanup_directory(self.output_path)
        os.makedirs(self.output_path, exist_ok=True)
        os.makedirs(self.slides_path, exist_ok=True)
    
    def tearDown(self):
        """Cleanup test environment"""
        cleanup_directory(self.output_path)

    def test_video_download_and_metadata(self):
        """Test video download and metadata extraction"""
        self.setUp()
        try:
            print("\nTesting video download and metadata extraction...")
            
            # Configure downloader for quick download
            downloader = VideoDownloader()
            downloader.ydl_opts.update({
                'format': 'worst[height>=360]',
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
            })
            
            # Extract metadata first (faster than downloading)
            print("Extracting metadata...")
            metadata = downloader.extract_metadata(TEST_VIDEO_URL)
            
            # Verify metadata
            assert metadata.video_id == "dQw4w9WgXcQ"
            assert len(metadata.title) > 0
            assert len(metadata.description) > 0
            assert metadata.length > 0
            assert len(metadata.captions) > 0
            
            print(f"Video title: {metadata.title}")
            print(f"Duration: {metadata.length} seconds")
            print(f"Caption segments: {len(metadata.captions)}")
            
            # Download video
            print("\nDownloading video...")
            video_path = downloader.download_video(TEST_VIDEO_URL, self.output_path)
            
            # Verify download
            assert video_path is not None
            assert os.path.exists(video_path)
            assert os.path.getsize(video_path) > 0
            
            print(f"Video downloaded to: {video_path}")
            print(f"File size: {os.path.getsize(video_path)} bytes")
            
        except Exception as e:
            pytest.fail(f"Error in video download and metadata test: {e}")
        finally:
            self.tearDown()

    def test_frame_extraction_and_analysis(self):
        """Test frame extraction and analysis"""
        self.setUp()
        try:
            print("\nTesting frame extraction and analysis...")
            
            # Create a sample video frame
            import cv2
            import numpy as np
            
            # Create a test frame with text
            frame = np.ones((480, 640, 3), dtype=np.uint8) * 255
            cv2.putText(frame, "Test Frame Content", (50, 240),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            
            # Save test frame
            frame_path = os.path.join(self.slides_path, "test_frame.jpg")
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

if __name__ == "__main__":
    pytest.main(['-v', '--tb=short'])
