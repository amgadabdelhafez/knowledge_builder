from dataclasses import dataclass
from typing import Dict, List, Any
from datetime import timedelta

@dataclass
class ContentSegment:
    """Represents a segment of content with timing and analysis"""
    start_time: float
    end_time: float
    slide_index: int
    transcript_text: str
    extracted_text: str
    keywords: List[str]
    technical_terms: List[str]
    content_type: str
    confidence: float

    def get_duration(self) -> timedelta:
        """Get segment duration as timedelta"""
        return timedelta(seconds=self.end_time - self.start_time)

    def to_dict(self) -> Dict[str, Any]:
        """Convert segment to dictionary"""
        return {
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': str(self.get_duration()),
            'slide_index': self.slide_index,
            'transcript_text': self.transcript_text,
            'extracted_text': self.extracted_text,
            'keywords': self.keywords,
            'technical_terms': self.technical_terms,
            'content_type': self.content_type,
            'confidence': self.confidence
        }

@dataclass
class DiagramComponent:
    """Represents a component in a technical diagram"""
    component_type: str
    text: str
    position: Dict[str, int]
    connections: List[str]
    confidence: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert component to dictionary"""
        return {
            'component_type': self.component_type,
            'text': self.text,
            'position': self.position,
            'connections': self.connections,
            'confidence': self.confidence
        }

def align_transcript_with_slides(
    transcript: List[Dict[str, Any]], 
    slide_timestamps: List[float]
) -> List[ContentSegment]:
    """Align transcript segments with slides based on temporal proximity"""
    segments = []
    current_slide = 0
    
    for i, entry in enumerate(transcript):
        # Find corresponding slide
        while (current_slide < len(slide_timestamps) - 1 and 
               entry['start'] >= slide_timestamps[current_slide + 1]):
            current_slide += 1
        
        # Create segment
        segment = ContentSegment(
            start_time=entry['start'],
            end_time=entry['start'] + entry.get('duration', 0),
            slide_index=current_slide,
            transcript_text=entry['text'],
            extracted_text="",  # Will be filled later
            keywords=[],        # Will be filled later
            technical_terms=[], # Will be filled later
            content_type="",    # Will be filled later
            confidence=0.0      # Will be filled later
        )
        segments.append(segment)
    
    return segments
