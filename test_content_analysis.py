import pytest
import os
import shutil
from typing import List, Dict, Any
from video_downloader import VideoDownloader
from image_processor import ImageProcessor
from text_processor import TextProcessor
from slide_extractor import SlideExtractor
from content_segment import ContentSegment, align_transcript_with_slides

# Test data - Using a shorter video for testing
TEST_VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Short video for testing

def cleanup_directory(path: str):
    """Safely cleanup a directory and all its contents"""
    try:
        if os.path.exists(path):
            shutil.rmtree(path)
    except Exception as e:
        print(f"Warning: Failed to cleanup {path}: {e}")

class TestContentAnalysis:
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

    def test_keyword_extraction(self):
        """Test keyword extraction from technical content"""
        text_processor = TextProcessor()
        
        # Test with technical content
        technical_text = """
        Machine Learning algorithms are used for autonomous vehicle perception.
        The CNN architecture processes sensor data through multiple convolutional layers.
        We use LSTM networks for temporal sequence analysis of the sensor data.
        The model is trained using PyTorch and deployed using TensorRT for real-time inference.
        """
        
        keywords = text_processor.extract_keywords(technical_text)
        technical_terms = text_processor.detect_technical_terms(technical_text)
        
        print(f"\nExtracted keywords: {keywords}")
        print(f"Technical terms: {technical_terms}")
        
        # Convert everything to lowercase for comparison
        found_keywords = {k.lower() for k in keywords}
        found_terms = {t.upper() for t in technical_terms}
        
        # Check for presence of important technical concepts
        important_keywords = {
            'machine learning',
            'algorithm',
            'autonomous',
            'vehicle',
            'perception',
            'cnn',
            'architecture',
            'sensor',
            'data',
            'convolutional',
            'lstm',
            'network',
            'temporal',
            'sequence',
            'analysis',
            'pytorch',
            'tensorrt',
            'inference'
        }
        
        # Check for presence of technical terms
        important_terms = {
            'CNN',
            'LSTM',
            'PYTORCH',
            'TENSORRT'
        }
        
        # Print coverage details for debugging
        print("\nKeyword coverage details:")
        found_keywords_list = sorted(important_keywords.intersection(found_keywords))
        missing_keywords = sorted(important_keywords - found_keywords)
        print(f"Found keywords: {found_keywords_list}")
        print(f"Missing keywords: {missing_keywords}")
        
        # Print term coverage details
        print("\nTechnical term coverage details:")
        found_terms_list = sorted(important_terms.intersection(found_terms))
        missing_terms = sorted(important_terms - found_terms)
        print(f"Found terms: {found_terms_list}")
        print(f"Missing terms: {missing_terms}")
        
        # Verify that at least 60% of important keywords are found
        found_important = len(important_keywords.intersection(found_keywords))
        keyword_coverage = found_important / len(important_keywords)
        assert keyword_coverage >= 0.6, f"Only found {keyword_coverage:.0%} of important keywords"
        
        # Verify that at least 75% of technical terms are found
        found_important_terms = len(important_terms.intersection(found_terms))
        term_coverage = found_important_terms / len(important_terms)
        assert term_coverage >= 0.75, f"Only found {term_coverage:.0%} of technical terms"

    def test_content_classification(self):
        """Test content type classification"""
        text_processor = TextProcessor()
        
        # Test different types of content
        test_cases = [
            {
                'content': """
                def process_image(img):
                    # Import required libraries
                    import cv2
                    import numpy as np
                    
                    # Convert to grayscale
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    
                    # Apply thresholding
                    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
                    
                    return binary
                """,
                'expected_domain': 'programming'
            },
            {
                'content': """
                Neural Network Architecture:
                
                1. Input Layer:
                   - 784 neurons (28x28 image)
                   - Flatten operation
                
                2. Hidden Layers:
                   - Dense layer with 128 neurons
                   - ReLU activation function
                   - Dropout rate: 0.3
                
                3. Output Layer:
                   - 10 neurons (one per class)
                   - Softmax activation
                   
                Training Parameters:
                - Learning rate: 0.001
                - Batch size: 32
                - Epochs: 100
                """,
                'expected_domain': 'machine_learning'
            },
            {
                'content': """
                Database Schema Design:
                
                CREATE TABLE Users (
                    id INT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE,
                    email VARCHAR(100),
                    created_at TIMESTAMP
                );
                
                CREATE TABLE Posts (
                    id INT PRIMARY KEY,
                    user_id INT REFERENCES Users(id),
                    title VARCHAR(200),
                    content TEXT,
                    published BOOLEAN
                );
                
                CREATE INDEX idx_user_posts ON Posts(user_id);
                """,
                'expected_domain': 'database_systems'
            },
            {
                'content': """
                Network Configuration:
                
                1. Router Setup:
                   - IP: 192.168.1.1
                   - Subnet: 255.255.255.0
                   - DHCP Range: 192.168.1.100-200
                
                2. Firewall Rules:
                   - Allow TCP ports 80, 443
                   - Block incoming UDP except DNS
                   - Enable NAT for internal network
                
                3. DNS Configuration:
                   - Primary: 8.8.8.8
                   - Secondary: 8.8.4.4
                """,
                'expected_domain': 'networking'
            }
        ]
        
        for case in test_cases:
            domain = text_processor.classify_domain(case['content'])
            print(f"\nTesting content type: {case['expected_domain']}")
            print(f"Classified as: {domain}")
            assert domain == case['expected_domain'], \
                f"Expected {case['expected_domain']}, but got {domain}"

    def test_transcript_alignment(self):
        """Test aligning transcript with slides"""
        # Create sample transcript and slide timestamps
        transcript = [
            {'text': 'First slide content', 'start': 0.0, 'duration': 5.0},
            {'text': 'Still on first slide', 'start': 5.0, 'duration': 5.0},
            {'text': 'Moving to second slide', 'start': 10.0, 'duration': 5.0},
            {'text': 'Third slide begins', 'start': 15.0, 'duration': 5.0}
        ]
        
        slide_timestamps = [0.0, 10.0, 15.0]  # Three slides
        
        # Align transcript with slides
        segments = align_transcript_with_slides(transcript, slide_timestamps)
        
        # Verify alignment
        assert len(segments) == len(transcript)
        assert segments[0].slide_index == 0  # First slide
        assert segments[1].slide_index == 0  # Still first slide
        assert segments[2].slide_index == 1  # Second slide
        assert segments[3].slide_index == 2  # Third slide
        
        print("\nTranscript segments aligned with slides:")
        for seg in segments:
            print(f"Time {seg.start_time:.1f}-{seg.end_time:.1f}: Slide {seg.slide_index}")

    def test_end_to_end_analysis(self):
        """Test end-to-end content analysis pipeline with a short video"""
        self.setUp()
        try:
            print("\nStarting end-to-end content analysis test...")
            
            # Configure downloader for short segment
            downloader = VideoDownloader()
            downloader.ydl_opts.update({
                'format': 'worst[height>=360]',  # Use low quality but visible format
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
            })
            
            print("Downloading test video...")
            video_path = downloader.download_video(TEST_VIDEO_URL, self.output_path)
            assert video_path is not None
            print(f"Video downloaded to: {video_path}")
            
            print("Extracting metadata...")
            metadata = downloader.extract_metadata(TEST_VIDEO_URL)
            assert len(metadata.captions) > 0
            print(f"Found {len(metadata.captions)} caption segments")
            
            print("Processing video for slides...")
            slide_extractor = SlideExtractor()
            slide_paths, slide_timestamps, slide_analyses = slide_extractor.process_video(
                video_path,
                self.slides_path,
                metadata,
                threshold=0.8  # Lower threshold for test
            )
            
            # Verify slide extraction
            assert len(slide_paths) > 0
            assert len(slide_timestamps) == len(slide_paths)
            assert len(slide_analyses) == len(slide_paths)
            print(f"Extracted {len(slide_paths)} slides")
            
            print("Processing transcript with slides...")
            segments = slide_extractor.process_transcript_with_slides(
                metadata.captions[:10],  # Use first 10 segments for quick test
                slide_paths,
                slide_timestamps,
                slide_analyses
            )
            
            # Verify segment analysis
            assert len(segments) > 0
            print(f"Processed {len(segments)} content segments")
            
            # Basic validation of segment properties
            for i, segment in enumerate(segments):
                assert isinstance(segment, ContentSegment)
                assert hasattr(segment, 'keywords')
                assert hasattr(segment, 'technical_terms')
                assert hasattr(segment, 'content_type')
                print(f"\nSegment {i + 1}:")
                print(f"- Start time: {segment.start_time:.1f}s")
                print(f"- Slide index: {segment.slide_index}")
                print(f"- Content type: {segment.content_type}")
            
            print("\nEnd-to-end test completed successfully!")
            
        except Exception as e:
            pytest.fail(f"Error in content analysis: {e}")
        finally:
            self.tearDown()

if __name__ == "__main__":
    pytest.main(['-v', '--tb=short'])
