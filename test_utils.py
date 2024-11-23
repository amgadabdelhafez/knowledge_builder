import os
import shutil

def cleanup_directory(path: str):
    """Safely cleanup a directory and all its contents"""
    try:
        if os.path.exists(path):
            shutil.rmtree(path)
    except Exception as e:
        print(f"Warning: Failed to cleanup {path}: {e}")

# Common test constants
TEST_VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Short video for testing
TEST_PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLgQxZdQXdhkZlLQVU2laGeCwI63CRvONn"
TEST_OUTPUT_PATH = "test_output"
TEST_SLIDES_PATH = os.path.join(TEST_OUTPUT_PATH, "slides")
