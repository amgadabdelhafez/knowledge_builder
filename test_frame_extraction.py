import pytest
import os
import shutil
import numpy as np
import cv2
from typing import List, Dict, Any
from image_processor import ImageProcessor

# Test data - Using a shorter video for testing
TEST_VIDEO_PATH = "test_data/test_video.mp4"  # Short test video
TEST_OUTPUT_PATH = "test_output/slides"

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
        # Create test directories
        os.makedirs(os.path.dirname(TEST_VIDEO_PATH), exist_ok=True)
        cleanup_directory(TEST_OUTPUT_PATH)
        os.makedirs(TEST_OUTPUT_PATH, exist_ok=True)
    
    def tearDown(self):
        """Cleanup test environment"""
        cleanup_directory(TEST_OUTPUT_PATH)
        if os.path.exists(TEST_VIDEO_PATH):
            os.remove(TEST_VIDEO_PATH)

    @pytest.mark.timeout(60)  # 1 minute timeout
    def test_frame_extraction(self):
        """Test frame extraction from video"""
        self.setUp()
        try:
            # Create a small test video file
            out = cv2.VideoWriter(
                TEST_VIDEO_PATH, 
                cv2.VideoWriter_fourcc(*'mp4v'), 
                1, 
                (640, 480)
            )
            
            # Create 3 distinct frames
            frames = []
            for i in range(3):
                # Create a frame with a different pattern for each iteration
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                # Draw something different in each frame
                cv2.rectangle(frame, (50*i, 50*i), (200+50*i, 200+50*i), (255, 255, 255), -1)
                frames.append(frame)
                out.write(frame)
            out.release()
            
            # Extract frames
            image_processor = ImageProcessor()
            slide_paths, slide_timestamps = image_processor.extract_slides(
                TEST_VIDEO_PATH,
                TEST_OUTPUT_PATH,
                threshold=0.8
            )
            
            # Verify results
            assert len(slide_paths) > 0
            assert len(slide_timestamps) == len(slide_paths)
            assert all(os.path.exists(path) for path in slide_paths)
            
        except Exception as e:
            pytest.fail(f"Error in frame extraction: {e}")
        finally:
            self.tearDown()

    def test_frame_hashing(self):
        """Test frame hash calculation"""
        processor = ImageProcessor()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        hash_value = processor._calculate_frame_hash(frame)
        
        assert isinstance(hash_value, str)
        assert len(hash_value) == 32  # MD5 hash length

    def test_text_extraction(self):
        """Test text extraction from image"""
        self.setUp()
        try:
            # Create test image with text
            img = np.full((480, 640, 3), 255, dtype=np.uint8)  # White background
            
            # Add black text
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(img, 'Test Text', (50, 240), font, 2, (0, 0, 0), 2)
            
            # Save test image
            test_image = os.path.join(TEST_OUTPUT_PATH, 'test_text.jpg')
            cv2.imwrite(test_image, img)
            
            # Extract text
            processor = ImageProcessor()
            text = processor.extract_text_from_image(test_image)
            
            # Verify text was extracted
            assert len(text) > 0
            assert 'Test' in text or 'TEXT' in text.upper()
            
        except Exception as e:
            pytest.fail(f"Error in text extraction: {e}")
        finally:
            self.tearDown()

if __name__ == "__main__":
    pytest.main(['-v', '--tb=short'])
