from dataclasses import dataclass
from typing import Dict, List, Any
from urllib.parse import parse_qs, urlparse

@dataclass
class VideoMetadata:
    """Metadata for a video"""
    video_id: str
    title: str
    description: str
    author: str
    length: int
    keywords: List[str]
    publish_date: str
    views: int
    initial_keywords: List[str]
    transcript_keywords: List[str]
    category: str
    tags: List[str]
    captions: List[Dict[str, Any]]
    thumbnail_url: str

@dataclass
class ProcessingResult:
    """Result of processing a video"""
    metadata: VideoMetadata
    slides: List[Dict[str, Any]]
    content_analysis: List[Dict[str, Any]]
    transcript: List[Dict[str, Any]]
    summary: Dict[str, Any]

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
