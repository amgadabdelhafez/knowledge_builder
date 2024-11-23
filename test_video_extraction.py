import pytest
import os
import yt_dlp
from video_metadata import VideoMetadata
from video_downloader import VideoDownloader
from test_utils import (
    cleanup_directory,
    TEST_VIDEO_URL,
    TEST_PLAYLIST_URL,
    TEST_OUTPUT_PATH
)

def get_smallest_format(url: str) -> str:
    """Get the format ID of the smallest available video format"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = info['formats']
        
        # Filter for video formats
        video_formats = [f for f in formats if f.get('vcodec') != 'none']
        
        # Try to find format with smallest filesize
        min_size = float('inf')
        best_format = None
        
        for fmt in video_formats:
            # Skip formats without filesize info
            if fmt.get('filesize') is None:
                continue
                
            if fmt['filesize'] < min_size:
                min_size = fmt['filesize']
                best_format = fmt
        
        # If no format with filesize found, use resolution as fallback
        if best_format is None:
            video_formats.sort(key=lambda x: (
                x.get('height', float('inf')),
                x.get('width', float('inf'))
            ))
            best_format = video_formats[0] if video_formats else None
        
        # Return format ID or fallback to lowest quality
        if best_format:
            return best_format['format_id']
        return 'worst'

class TestVideoExtraction:
    def setUp(self):
        """Setup test environment"""
        cleanup_directory(TEST_OUTPUT_PATH)
        os.makedirs(TEST_OUTPUT_PATH, exist_ok=True)
    
    def tearDown(self):
        """Cleanup test environment"""
        cleanup_directory(TEST_OUTPUT_PATH)

    def test_url_cleaning_variations(self):
        """Test URL cleaning with various URL formats"""
        downloader = VideoDownloader()
        
        # Test youtu.be short URL with parameters
        url = "https://youtu.be/-UPfyvDJz9I?si=lyRoQf248d13q94p"
        clean_url = downloader.clean_youtube_url(url)
        assert clean_url == "https://www.youtube.com/watch?v=-UPfyvDJz9I"
        
        # Test standard watch URL with extra parameters
        url = "https://www.youtube.com/watch?v=-UPfyvDJz9I&t=120s&feature=youtu.be"
        clean_url = downloader.clean_youtube_url(url)
        assert clean_url == "https://www.youtube.com/watch?v=-UPfyvDJz9I"
        
        # Test embedded URL
        url = "https://www.youtube.com/embed/-UPfyvDJz9I"
        clean_url = downloader.clean_youtube_url(url)
        assert clean_url == "https://www.youtube.com/watch?v=-UPfyvDJz9I"

    def test_transcript_structure(self):
        """Test detailed transcript structure and content"""
        downloader = VideoDownloader()
        transcript = downloader._get_transcript("-UPfyvDJz9I")
        
        assert isinstance(transcript, list)
        assert len(transcript) > 0
        
        # Detailed transcript structure validation
        for entry in transcript[:5]:  # Check first 5 entries
            assert 'text' in entry
            assert 'start' in entry
            assert 'duration' in entry
            assert isinstance(entry['text'], str)
            assert isinstance(entry['start'], (int, float))
            assert isinstance(entry['duration'], (int, float))
            assert entry['start'] >= 0
            assert entry['duration'] > 0
            assert len(entry['text'].strip()) > 0
        
        # Check transcript continuity
        for i in range(1, len(transcript)):
            current_start = transcript[i]['start']
            previous_start = transcript[i-1]['start']
            previous_duration = transcript[i-1]['duration']
            
            # Verify timestamps are sequential
            assert current_start >= previous_start
            # Verify no large gaps
            assert current_start - (previous_start + previous_duration) < 5.0

    def test_optimized_video_download(self):
        """Test downloading video with optimal format selection"""
        self.setUp()
        try:
            downloader = VideoDownloader()
            
            # Get the smallest available format
            format_id = get_smallest_format(TEST_VIDEO_URL)
            print(f"\nUsing optimal format ID: {format_id}")
            
            # Configure for optimal download
            downloader.ydl_opts.update({
                'format': format_id,
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
            })
            
            video_path = downloader.download_video(TEST_VIDEO_URL, TEST_OUTPUT_PATH)
            
            assert video_path is not None
            assert os.path.exists(video_path)
            file_size = os.path.getsize(video_path)
            assert file_size > 0
            
            print(f"Downloaded video to: {video_path}")
            print(f"Optimized file size: {file_size} bytes")
            
            # Verify video file integrity
            import cv2
            cap = cv2.VideoCapture(video_path)
            assert cap.isOpened()
            
            # Check video properties
            width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            
            assert width > 0
            assert height > 0
            assert fps > 0
            assert frame_count > 0
            
            print(f"Video properties - Resolution: {width}x{height}, FPS: {fps}, Frames: {frame_count}")
            
            cap.release()
            
        except Exception as e:
            pytest.fail(f"Error in optimized video download: {e}")
        finally:
            self.tearDown()
