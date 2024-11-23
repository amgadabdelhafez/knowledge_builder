from dataclasses import dataclass
from typing import Dict, List, Any, Optional
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

def _extract_transcript_values(entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Extract and validate transcript entry values"""
    try:
        # Extract required fields with default values
        start_time = float(entry.get('start', 0))
        duration = float(entry.get('duration', 0))
        text = str(entry.get('text', ''))
        
        # Return normalized values
        return {
            'start': start_time,
            'duration': duration,
            'text': text
        }
    except (TypeError, ValueError):
        return None

def align_transcript_with_slides(
    transcript: List[Dict[str, Any]], 
    slide_timestamps: List[float]
) -> List[ContentSegment]:
    """Align transcript segments with slides based on temporal proximity"""
    segments = []
    current_slide = 0
    
    # Convert slide timestamps to floats to ensure they're hashable
    slide_timestamps = [float(ts) for ts in slide_timestamps]
    
    # Process each transcript entry
    for entry in transcript:
        # Extract and validate transcript values
        values = _extract_transcript_values(entry)
        if values is None:
            continue
        
        # Find corresponding slide
        while (current_slide < len(slide_timestamps) - 1 and 
               values['start'] >= slide_timestamps[current_slide + 1]):
            current_slide += 1
        
        # Create segment
        segment = ContentSegment(
            start_time=values['start'],
            end_time=values['start'] + values['duration'],
            slide_index=current_slide,
            transcript_text=values['text'],
            extracted_text="",  # Will be filled later
            keywords=[],        # Will be filled later
            technical_terms=[], # Will be filled later
            content_type="",    # Will be filled later
            confidence=0.0      # Will be filled later
        )
        segments.append(segment)
    
    return segments
