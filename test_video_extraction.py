import pytest
import os
import shutil
import yt_dlp
from video_metadata import VideoMetadata
from video_downloader import VideoDownloader

# Test data - Using actual video from the playlist
TEST_VIDEO_URL = "https://www.youtube.com/watch?v=-UPfyvDJz9I"  # Machine Learning for AV Perception at Cruise
TEST_PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLgQxZdQXdhkZlLQVU2laGeCwI63CRvONn"

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

def cleanup_directory(path: str):
    """Safely cleanup a directory and all its contents"""
    try:
        if os.path.exists(path):
            shutil.rmtree(path)
    except Exception as e:
        print(f"Warning: Failed to cleanup {path}: {e}")

class TestVideoDownloader:
    def setUp(self):
        """Setup test environment"""
        self.output_path = "test_output"
        cleanup_directory(self.output_path)
        os.makedirs(self.output_path, exist_ok=True)
    
    def tearDown(self):
        """Cleanup test environment"""
        cleanup_directory(self.output_path)

    def test_clean_url(self):
        """Test URL cleaning"""
        downloader = VideoDownloader()
        # Test full URL with parameters
        url = "https://youtu.be/-UPfyvDJz9I?si=lyRoQf248d13q94p"
        clean_url = downloader.clean_youtube_url(url)
        assert clean_url == "https://www.youtube.com/watch?v=-UPfyvDJz9I"
        
        # Test standard watch URL
        url = "https://www.youtube.com/watch?v=-UPfyvDJz9I"
        clean_url = downloader.clean_youtube_url(url)
        assert clean_url == url

    def test_extract_basic_metadata(self):
        """Test basic metadata extraction without processing"""
        downloader = VideoDownloader()
        metadata = downloader.extract_metadata(TEST_VIDEO_URL)
        
        # Basic metadata checks
        assert isinstance(metadata, VideoMetadata)
        assert metadata.video_id == "-UPfyvDJz9I"
        assert len(metadata.video_id) > 0
        assert len(metadata.title) > 0
        assert len(metadata.description) > 0
        assert metadata.length > 0
        assert metadata.views >= 0
        
        print(f"\nVideo Title: {metadata.title}")
        print(f"Duration: {metadata.length} seconds")
        print(f"Author: {metadata.author}")

    def test_get_transcript(self):
        """Test transcript retrieval"""
        downloader = VideoDownloader()
        transcript = downloader._get_transcript("-UPfyvDJz9I")
        
        assert isinstance(transcript, list)
        assert len(transcript) > 0
        
        # Check transcript structure
        first_entry = transcript[0]
        assert 'text' in first_entry
        assert 'start' in first_entry
        assert isinstance(first_entry['text'], str)
        assert isinstance(first_entry['start'], (int, float))
        
        print(f"\nFirst transcript entry: {first_entry['text']}")
        print(f"Transcript length: {len(transcript)} segments")

    def test_download_video_segment(self):
        """Test downloading a small segment of the video"""
        self.setUp()
        try:
            downloader = VideoDownloader()
            
            # Get the smallest available format
            format_id = get_smallest_format(TEST_VIDEO_URL)
            print(f"\nUsing format ID: {format_id}")
            
            # Configure for small segment and low quality
            downloader.ydl_opts.update({
                'format': format_id,
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
            })
            
            video_path = downloader.download_video(TEST_VIDEO_URL, self.output_path)
            
            assert video_path is not None
            assert os.path.exists(video_path)
            assert os.path.getsize(video_path) > 0
            
            print(f"Downloaded video to: {video_path}")
            print(f"File size: {os.path.getsize(video_path)} bytes")
            
        except Exception as e:
            pytest.fail(f"Error downloading video: {e}")
        finally:
            self.tearDown()

    def test_get_playlist_info(self):
        """Test getting basic playlist information"""
        downloader = VideoDownloader()
        videos = downloader.get_playlist_videos(TEST_PLAYLIST_URL)
        
        assert isinstance(videos, list)
        assert len(videos) > 0
        assert all(isinstance(url, str) for url in videos)
        assert all("youtube.com/watch?v=" in url for url in videos)
        
        print(f"\nFound {len(videos)} videos in playlist")
        print(f"First video URL: {videos[0]}")

if __name__ == "__main__":
    pytest.main(['-v', '--tb=short'])
