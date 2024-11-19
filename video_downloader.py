import os
from typing import Dict, List, Optional, Any
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from datetime import datetime
from video_metadata import VideoMetadata

def clean_youtube_url(url: str) -> str:
    """Clean YouTube URL by removing tracking parameters"""
    # Extract video ID from different URL formats
    if 'youtu.be/' in url:
        video_id = url.split('youtu.be/')[-1].split('?')[0]
    elif 'watch?v=' in url:
        video_id = url.split('watch?v=')[-1].split('&')[0]
    else:
        raise ValueError(f"Invalid YouTube URL format: {url}")
    
    # Return clean URL
    return f"https://www.youtube.com/watch?v={video_id}"

class VideoDownloader:
    def __init__(self):
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best',  # Default to best quality
            'writesubtitles': True,
            'writeautomaticsub': True,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',  # Convert to MP4
            }],
        }

    def clean_youtube_url(self, url: str) -> str:
        """Clean YouTube URL by removing tracking parameters"""
        return clean_youtube_url(url)

    def extract_metadata(self, video_url: str) -> VideoMetadata:
        """Extract comprehensive metadata from video"""
        try:
            # Clean URL
            clean_url = self.clean_youtube_url(video_url)
            
            # Configure options for metadata extraction
            meta_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
            }
            
            # Extract metadata using yt-dlp
            with yt_dlp.YoutubeDL(meta_opts) as ydl:
                info = ydl.extract_info(clean_url, download=False)
                if not info:
                    raise Exception("Could not extract video info")
                
                # Get transcript
                transcript = self._get_transcript(info['id'])
                
                # Create metadata object
                metadata = VideoMetadata(
                    video_id=info['id'],
                    title=info.get('title', ''),
                    description=info.get('description', ''),
                    author=info.get('uploader', ''),
                    length=info.get('duration', 0),
                    keywords=[],  # Will be filled by content extractor
                    publish_date=str(datetime.fromtimestamp(info.get('upload_date_timestamp', 0))),
                    views=info.get('view_count', 0),
                    initial_keywords=[],  # Will be filled by content extractor
                    transcript_keywords=[],  # Will be filled by content extractor
                    category=info.get('categories', [''])[0] if info.get('categories') else '',
                    tags=info.get('tags', []),
                    captions=transcript,
                    thumbnail_url=info.get('thumbnail', '')
                )
                
                return metadata
            
        except Exception as e:
            print(f"Error extracting metadata: {e}")
            raise

    def _get_transcript(self, video_id: str) -> List[Dict[str, Any]]:
        """Get video transcript with timestamps"""
        try:
            # Try to get manual transcripts first
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                return transcript
            except Exception:
                # If manual transcript fails, try auto-generated
                transcript = YouTubeTranscriptApi.get_transcript(video_id, ['en'])
                return transcript
        except Exception as e:
            print(f"Error getting transcript: {e}")
            return []

    def download_video(self, url: str, output_path: str) -> Optional[str]:
        """Download video with progress tracking"""
        try:
            # Clean URL
            clean_url = self.clean_youtube_url(url)
            
            # Configure download options
            download_opts = {
                **self.ydl_opts,
                'outtmpl': os.path.join(output_path, '%(id)s.%(ext)s'),
            }
            
            # Download video
            with yt_dlp.YoutubeDL(download_opts) as ydl:
                # Extract info first
                info = ydl.extract_info(clean_url, download=False)
                if not info:
                    raise Exception("Could not extract video info")
                
                # Download the video
                ydl.download([clean_url])
                
                # Get the output path
                video_id = info['id']
                video_path = os.path.join(output_path, f"{video_id}.mp4")
                
                if not os.path.exists(video_path):
                    # Try other common extensions if mp4 not found
                    for ext in ['mkv', 'webm']:
                        alt_path = os.path.join(output_path, f"{video_id}.{ext}")
                        if os.path.exists(alt_path):
                            video_path = alt_path
                            break
                
                if not os.path.exists(video_path):
                    raise Exception(f"Downloaded file not found at {video_path}")
                
                print("\nDownload completed!")
                return video_path
                
        except Exception as e:
            print(f"\nError downloading video: {e}")
            return None

    def get_playlist_videos(self, playlist_url: str) -> List[str]:
        """Get list of video URLs from a playlist"""
        try:
            # Configure yt-dlp options for playlist
            playlist_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'ignoreerrors': True,  # Skip unavailable videos
            }
            
            # Get playlist info
            with yt_dlp.YoutubeDL(playlist_opts) as ydl:
                playlist_info = ydl.extract_info(playlist_url, download=False)
                if not playlist_info:
                    raise Exception("Could not extract playlist info")
                
                # Extract video URLs
                video_urls = []
                for entry in playlist_info['entries']:
                    if entry and entry.get('id'):
                        video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                        video_urls.append(video_url)
                
                return video_urls
                
        except Exception as e:
            print(f"Error getting playlist videos: {e}")
            return []