import pytest
import os
import shutil
import cv2
import numpy as np
from video_downloader import VideoDownloader
from image_processor import ImageProcessor

# Test data
TEST_VIDEO_URL = "https://www.youtube.com/watch?v=-UPfyvDJz9I"  # Machine Learning for AV Perception at Cruise

def cleanup_directory(path: str):
    """Safely cleanup a directory and all its contents"""
    try:
        if os.path.exists(path):
            shutil.rmtree(path)
    except Exception as e:
        print(f"Warning: Failed to cleanup {path}: {e}")

class TestFrameExtraction:
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

    def test_frame_extraction(self):
        """Test extracting frames from video"""
        self.setUp()
        try:
            # First download a video segment
            downloader = VideoDownloader()
            video_path = downloader.download_video(TEST_VIDEO_URL, self.output_path)
            assert video_path is not None
            assert os.path.exists(video_path)
            
            # Extract frames
            image_processor = ImageProcessor()
            slide_paths, slide_timestamps = image_processor.extract_slides(
                video_path,
                self.slides_path,
                threshold=0.95  # High threshold to detect significant changes
            )
            
            # Verify extraction results
            assert len(slide_paths) > 0
            assert len(slide_timestamps) == len(slide_paths)
            
            # Check that extracted frames are valid images
            for path in slide_paths:
                assert os.path.exists(path)
                assert os.path.getsize(path) > 0
                
                # Try to read with OpenCV to verify it's a valid image
                img = cv2.imread(path)
                assert img is not None
                assert isinstance(img, np.ndarray)
                assert img.shape[2] == 3  # Should be BGR image
                
                # Check reasonable dimensions
                assert img.shape[0] > 100  # height
                assert img.shape[1] > 100  # width
            
            # Check timestamps are monotonically increasing
            assert all(t2 > t1 for t1, t2 in zip(slide_timestamps[:-1], slide_timestamps[1:]))
            
            print(f"\nExtracted {len(slide_paths)} frames")
            print(f"First frame: {slide_paths[0]}")
            print(f"First timestamp: {slide_timestamps[0]:.2f}s")
            
        except Exception as e:
            pytest.fail(f"Error extracting frames: {e}")
        finally:
            self.tearDown()

    def test_frame_hashing(self):
        """Test frame hash calculation and comparison"""
        image_processor = ImageProcessor()
        
        # Create two different test frames
        frame1 = np.zeros((480, 640, 3), dtype=np.uint8)  # Black frame
        frame2 = np.ones((480, 640, 3), dtype=np.uint8) * 255  # White frame
        
        # Calculate hashes
        hash1 = image_processor._calculate_frame_hash(frame1)
        hash2 = image_processor._calculate_frame_hash(frame2)
        
        # Verify hashes are different
        assert hash1 != hash2
        
        # Test hash difference calculation
        diff = image_processor._hash_difference(hash1, hash2)
        assert diff > 0.9  # Should be very different
        
        # Test identical frames
        diff = image_processor._hash_difference(hash1, hash1)
        assert diff == 0.0  # Should be identical

    def test_text_extraction(self):
        """Test extracting text from frames"""
        self.setUp()
        try:
            # Create a test image with text
            img = np.ones((200, 800, 3), dtype=np.uint8) * 255  # White background
            cv2.putText(img, "Test Slide Content", (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 2)
            
            # Save test image
            test_image_path = os.path.join(self.slides_path, "test_slide.jpg")
            cv2.imwrite(test_image_path, img)
            
            # Extract text
            image_processor = ImageProcessor()
            extracted_text = image_processor.extract_text_from_image(test_image_path)
            
            # Verify text extraction
            assert "Test" in extracted_text
            assert "Slide" in extracted_text
            assert "Content" in extracted_text
            
            print(f"\nExtracted text: {extracted_text}")
            
        except Exception as e:
            pytest.fail(f"Error extracting text: {e}")
        finally:
            self.tearDown()

if __name__ == "__main__":
    pytest.main(['-v', '--tb=short'])
