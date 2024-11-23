from dataclasses import dataclass, asdict
from typing import Dict, List, Any
from urllib.parse import parse_qs, urlparse

@dataclass
class Chapter:
    """Video chapter information"""
    title: str
    start_time: float
    end_time: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert chapter to dictionary for JSON serialization"""
        return {
            'title': self.title,
            'start_time': self.start_time,
            'end_time': self.end_time
        }

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
    chapters: List[Chapter]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary for JSON serialization"""
        data = asdict(self)
        # Convert chapters to dictionaries
        data['chapters'] = [chapter.to_dict() for chapter in self.chapters]
        return data

@dataclass
class ProcessingResult:
    """Result of processing a video"""
    metadata: VideoMetadata
    slides: List[Dict[str, Any]]
    content_analysis: List[Dict[str, Any]]
    transcript: List[Dict[str, Any]]
    summary: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for JSON serialization"""
        return {
            'metadata': self.metadata.to_dict(),
            'slides': self.slides,
            'content_analysis': self.content_analysis,
            'transcript': self.transcript,
            'summary': self.summary
        }

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
