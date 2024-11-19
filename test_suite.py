import pytest
import os
import json
from unittest.mock import Mock, patch
import numpy as np
from datetime import datetime

from video_metadata import VideoMetadata, ProcessingResult
from video_downloader import VideoDownloader
from slide_extractor import SlideExtractor
from results_processor import ResultsProcessor
from lecture_processor import LectureProcessor
from text_processor import TextProcessor
from image_processor import ImageProcessor

# Test data - Using actual video from the playlist
TEST_VIDEO_URL = "https://www.youtube.com/watch?v=-UPfyvDJz9I"  # Machine Learning for AV Perception at Cruise
TEST_PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLgQxZdQXdhkZlLQVU2laGeCwI63CRvONn"

class TestVideoDownloader:
    def test_extract_metadata(self):
        """Test metadata extraction from actual video"""
        downloader = VideoDownloader()
        metadata = downloader.extract_metadata(TEST_VIDEO_URL)
        
        assert isinstance(metadata, VideoMetadata)
        assert metadata.video_id == "-UPfyvDJz9I"
        assert "Machine Learning" in metadata.title
        assert "Cruise" in metadata.title
        assert len(metadata.captions) > 0

    def test_get_playlist_videos(self):
        """Test getting videos from actual playlist"""
        downloader = VideoDownloader()
        videos = downloader.get_playlist_videos(TEST_PLAYLIST_URL)
        
        assert isinstance(videos, list)
        assert len(videos) > 0
        assert all(isinstance(url, str) for url in videos)
        assert all("youtube.com" in url for url in videos)

class TestTextProcessor:
    def test_extract_keywords(self):
        """Test keyword extraction"""
        processor = TextProcessor()
        text = "Machine Learning for Autonomous Vehicle Perception at Cruise"
        keywords = processor.extract_keywords(text)
        
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        assert "machine learning" in [k.lower() for k in keywords]
        assert "autonomous vehicle" in [k.lower() for k in keywords]
        assert "perception" in [k.lower() for k in keywords]

    def test_detect_technical_terms(self):
        """Test technical term detection"""
        processor = TextProcessor()
        text = "Using CNN and LSTM networks for perception. The API endpoint uses REST."
        terms = processor.detect_technical_terms(text)
        
        assert isinstance(terms, list)
        assert len(terms) > 0
        assert "CNN" in terms
        assert "LSTM" in terms
        assert "API" in terms
        assert "REST" in terms

class TestImageProcessor:
    def test_calculate_frame_hash(self):
        """Test frame hash calculation"""
        processor = ImageProcessor()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        hash_value = processor._calculate_frame_hash(frame)
        
        assert isinstance(hash_value, str)
        assert len(hash_value) == 32  # MD5 hash length

    def test_hash_difference(self):
        """Test hash difference calculation"""
        processor = ImageProcessor()
        hash1 = "a" * 32
        hash2 = "b" * 32
        diff = processor._hash_difference(hash1, hash2)
        assert diff == 1.0  # Complete difference
        
        hash3 = hash1  # Same hash
        diff = processor._hash_difference(hash1, hash3)
        assert diff == 0.0  # No difference

class TestResultsProcessor:
    def test_create_content_folder(self):
        """Test folder creation"""
        processor = ResultsProcessor()
        video_id = "test123"
        folder = processor.create_content_folder(video_id)
        
        assert os.path.exists(folder)
        assert os.path.exists(os.path.join(folder, 'slides'))
        assert os.path.exists(os.path.join(folder, 'analysis'))
        assert os.path.exists(os.path.join(folder, 'metadata'))
        assert os.path.exists(os.path.join(folder, 'transcripts'))
        
        # Cleanup
        import shutil
        shutil.rmtree(folder)

class TestLectureProcessor:
    def test_process_video(self):
        """Test processing actual video"""
        processor = LectureProcessor()
        try:
            result = processor.process_video(TEST_VIDEO_URL)
            
            # Verify result structure
            assert isinstance(result, ProcessingResult)
            assert isinstance(result.metadata, VideoMetadata)
            assert result.metadata.video_id == "-UPfyvDJz9I"
            assert "Machine Learning" in result.metadata.title
            assert len(result.transcript) > 0
            assert result.summary is not None
            
            # Check content
            assert len(result.slides) > 0
            assert len(result.content_analysis) > 0
            assert any("machine learning" in [k.lower() for k in segment['keywords']] 
                      for segment in result.content_analysis)
            
            # Cleanup
            base_folder = f"lecture_{result.metadata.video_id}"
            if os.path.exists(base_folder):
                import shutil
                shutil.rmtree(base_folder)
            
        except Exception as e:
            pytest.fail(f"Error processing video {TEST_VIDEO_URL}: {e}")

    def test_process_playlist_subset(self):
        """Test processing first video from playlist"""
        processor = LectureProcessor()
        try:
            # Get first video from playlist
            downloader = VideoDownloader()
            videos = downloader.get_playlist_videos(TEST_PLAYLIST_URL)
            assert len(videos) > 0
            
            # Process first video
            result = processor.process_video(videos[0])
            
            # Verify result
            assert isinstance(result, ProcessingResult)
            assert isinstance(result.metadata, VideoMetadata)
            assert len(result.slides) > 0
            assert len(result.content_analysis) > 0
            assert result.summary is not None
            
            # Cleanup
            base_folder = f"lecture_{result.metadata.video_id}"
            if os.path.exists(base_folder):
                import shutil
                shutil.rmtree(base_folder)
            
        except Exception as e:
            pytest.fail(f"Error processing playlist video: {e}")

if __name__ == "__main__":
    pytest.main(['-v', '--tb=short'])
