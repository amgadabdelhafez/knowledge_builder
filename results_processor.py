import os
import json
from typing import Dict, List, Any
from datetime import datetime
from video_metadata import VideoMetadata, ProcessingResult
from content_segment import ContentSegment
from text_processor import TextProcessor

class ResultsProcessor:
    def __init__(self):
        self.text_processor = TextProcessor()

    def create_content_folder(self, video_id: str) -> str:
        """Create organized folder structure for content"""
        # Generate safe folder name
        base_folder = self.text_processor.get_safe_filename(
            f"lecture_{video_id}",
            max_length=100
        )
        
        # Create required directories
        folders = {
            'slides': os.path.join(base_folder, 'slides'),
            'analysis': os.path.join(base_folder, 'analysis'),
            'metadata': os.path.join(base_folder, 'metadata'),
            'transcripts': os.path.join(base_folder, 'transcripts'),
        }
        
        for folder in folders.values():
            os.makedirs(folder, exist_ok=True)
            
        return base_folder

    def save_results(
        self,
        metadata: VideoMetadata,
        segments: List[ContentSegment],
        slide_info: List[Dict[str, Any]],
        base_folder: str
    ) -> ProcessingResult:
        """Save processing results and return result object"""
        try:
            # Generate summary
            summary = self._generate_summary(metadata, segments, slide_info)
            
            # Create result object
            result = ProcessingResult(
                metadata=metadata,
                slides=slide_info,
                content_analysis=[segment.to_dict() for segment in segments],
                transcript=metadata.captions,
                summary=summary
            )
            
            # Save files
            self._save_metadata(result.metadata, base_folder)
            self._save_content_analysis(result.content_analysis, base_folder)
            self._save_transcript(result.transcript, base_folder)
            self._save_summary(result.summary, base_folder)
            
            return result
            
        except Exception as e:
            print(f"Error saving results: {e}")
            raise

    def _generate_summary(
        self,
        metadata: VideoMetadata,
        segments: List[ContentSegment],
        slide_info: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate comprehensive summary of video content"""
        try:
            # Collect all keywords and technical terms
            all_keywords = set()
            all_terms = set()
            content_types = {}
            
            for segment in segments:
                all_keywords.update(segment.keywords)
                all_terms.update(segment.technical_terms)
                content_types[segment.content_type] = content_types.get(segment.content_type, 0) + 1
            
            # Get main topics based on keyword frequency
            main_topics = self._get_main_topics(segments)
            
            return {
                'title': metadata.title,
                'author': metadata.author,
                'duration': str(metadata.length),
                'date': metadata.publish_date,
                'slide_count': len(slide_info),
                'main_topics': main_topics,
                'content_types': content_types,
                'technical_terms': sorted(list(all_terms)),
                'keywords': sorted(list(all_keywords)),
                'statistics': {
                    'total_segments': len(segments),
                    'total_keywords': len(all_keywords),
                    'total_technical_terms': len(all_terms),
                    'content_type_distribution': content_types
                }
            }
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return {}

    def _get_main_topics(self, segments: List[ContentSegment]) -> List[Tuple[str, int]]:
        """Extract main topics based on keyword frequency"""
        keyword_freq = {}
        for segment in segments:
            for keyword in segment.keywords:
                keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1
        
        # Sort by frequency and return top 10
        sorted_topics = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
        return sorted_topics[:10]

    def _save_metadata(self, metadata: VideoMetadata, base_folder: str):
        """Save video metadata"""
        path = os.path.join(base_folder, 'metadata', 'video_metadata.json')
        self._save_json(metadata.__dict__, path)

    def _save_content_analysis(self, analysis: List[Dict], base_folder: str):
        """Save content analysis results"""
        path = os.path.join(base_folder, 'analysis', 'content_analysis.json')
        self._save_json(analysis, path)

    def _save_transcript(self, transcript: List[Dict], base_folder: str):
        """Save transcript"""
        path = os.path.join(base_folder, 'transcripts', 'transcript.json')
        self._save_json(transcript, path)

    def _save_summary(self, summary: Dict, base_folder: str):
        """Save content summary"""
        path = os.path.join(base_folder, 'analysis', 'summary.json')
        self._save_json(summary, path)

    def _save_json(self, data: Any, path: str):
        """Save data as JSON file"""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving JSON file {path}: {e}")
            raise
