import os
import json
import re
from typing import Dict, List, Any, Tuple
from datetime import datetime
from video_metadata import VideoMetadata, ProcessingResult
from content_segment import ContentSegment
from text_processor import TextProcessor

class ResultsProcessor:
    def __init__(self):
        self.text_processor = TextProcessor()

    def _sanitize_filename(self, filename: str, max_length: int = 50) -> str:
        """Create a safe filename from a string"""
        # Remove invalid characters
        safe_name = re.sub(r'[<>:"/\\|?*]', '', filename)
        # Replace spaces and other characters with underscores
        safe_name = re.sub(r'[\s\-]+', '_', safe_name)
        # Remove any non-ASCII characters
        safe_name = ''.join(c for c in safe_name if ord(c) < 128)
        # Truncate to max length while keeping words intact
        if len(safe_name) > max_length:
            safe_name = safe_name[:max_length].rsplit('_', 1)[0]
        return safe_name.strip('_').lower()

    def create_content_folder(self, title: str, video_order: int = 1, playlist_name: str = "km") -> str:
        """Create organized folder structure for content"""
        # Generate safe folder name with order prefix
        safe_title = self._sanitize_filename(title)
        safe_playlist = self._sanitize_filename(playlist_name)
        base_folder = f"{safe_playlist}_{video_order:02d}_{safe_title}"
        
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

    def create_merged_content(self, results: List[ProcessingResult], playlist_name: str = "km") -> None:
        """Create a merged content file with all video information"""
        merged_content = []
        safe_playlist = self._sanitize_filename(playlist_name)
        
        for idx, result in enumerate(results, 1):
            # Add video title as header
            merged_content.append(f"# {result.metadata.title}\n")
            
            # Add description
            if result.metadata.description:
                merged_content.append("## Description\n")
                merged_content.append(f"{result.metadata.description}\n")
            
            # Add clean transcript
            merged_content.append("## Transcript\n")
            transcript_path = os.path.join(
                f"{safe_playlist}_{idx:02d}_{self._sanitize_filename(result.metadata.title)}",
                'transcripts',
                'transcript_clean.txt'
            )
            try:
                with open(transcript_path, 'r', encoding='utf-8') as f:
                    transcript = f.read()
                merged_content.append(transcript)
            except Exception as e:
                print(f"Error reading transcript for {result.metadata.title}: {e}")
            
            # Add separator between videos
            merged_content.append("\n---\n\n")
        
        # Save merged content
        output_path = f"{safe_playlist}_merged_content.md"
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(merged_content))
            print(f"\nCreated merged content file: {output_path}")
        except Exception as e:
            print(f"Error creating merged content file: {e}")

    def save_results(
        self,
        metadata: VideoMetadata,
        segments: List[ContentSegment],
        slide_info: List[Dict[str, Any]],
        base_folder: str,
        process_slides: bool = True
    ) -> ProcessingResult:
        """Save processing results and return result object"""
        try:
            # Generate summary
            summary = self._generate_summary(metadata, segments, slide_info)
            
            # Create result object
            result = ProcessingResult(
                metadata=metadata,
                slides=slide_info if process_slides else [],
                content_analysis=[] if not process_slides else [segment.to_dict() for segment in segments],
                transcript=None,  # No longer storing transcript in metadata
                summary=summary
            )
            
            # Get safe title for filenames
            safe_title = os.path.basename(base_folder)  # Use folder name for consistency
            
            # Save files with descriptive names
            self._save_metadata(result.metadata, base_folder, safe_title)
            if process_slides:
                self._save_content_analysis(result.content_analysis, base_folder, safe_title)
            self._save_transcripts(metadata.captions, metadata.chapters, base_folder, safe_title)
            self._save_summary(result.summary, base_folder, safe_title)
            
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
            
            if segments:  # Only process if segments exist
                for segment in segments:
                    all_keywords.update(segment.keywords)
                    all_terms.update(segment.technical_terms)
                    content_types[segment.content_type] = content_types.get(segment.content_type, 0) + 1
            
                # Get main topics based on keyword frequency
                main_topics = self._get_main_topics(segments)
            else:
                main_topics = []
            
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

    def _save_metadata(self, metadata: VideoMetadata, base_folder: str, safe_title: str):
        """Save video metadata"""
        # Create a copy of metadata without the captions
        metadata_dict = metadata.to_dict()
        metadata_dict.pop('captions', None)  # Remove captions from metadata
        
        filename = f"metadata.json"
        path = os.path.join(base_folder, 'metadata', filename)
        self._save_json(metadata_dict, path)

    def _save_content_analysis(self, analysis: List[Dict], base_folder: str, safe_title: str):
        """Save content analysis results"""
        filename = f"content_analysis.json"
        path = os.path.join(base_folder, 'analysis', filename)
        self._save_json(analysis, path)

    def _save_transcripts(self, transcript: List[Dict], chapters: List[Any], base_folder: str, safe_title: str):
        """Save transcripts in multiple formats"""
        # Save raw transcript with timestamps
        raw_filename = f"transcript_raw.json"
        raw_path = os.path.join(base_folder, 'transcripts', raw_filename)
        self._save_json(transcript, raw_path)
        
        # Save clean transcript grouped by chapters
        clean_transcript = self._generate_clean_transcript(transcript, chapters)
        clean_filename = f"transcript_clean.txt"
        clean_path = os.path.join(base_folder, 'transcripts', clean_filename)
        
        try:
            with open(clean_path, 'w', encoding='utf-8') as f:
                f.write(clean_transcript)
        except Exception as e:
            print(f"Error saving clean transcript: {e}")

    def _generate_clean_transcript(self, transcript: List[Dict], chapters: List[Any]) -> str:
        """Generate clean transcript grouped by chapters"""
        result = []
        current_chapter = None
        current_paragraph = []
        
        def add_paragraph():
            if current_paragraph:
                result.append(' '.join(current_paragraph))
                current_paragraph.clear()
        
        for entry in transcript:
            # Get timestamp and text
            timestamp = entry.get('start', 0)
            text = entry.get('text', '').strip()
            
            # Skip empty text
            if not text:
                continue
            
            # Find current chapter
            new_chapter = None
            for chapter in chapters:
                if chapter.start_time <= timestamp < chapter.end_time:
                    new_chapter = chapter.title
                    break
            
            # Handle chapter change
            if new_chapter != current_chapter:
                add_paragraph()  # End current paragraph
                if new_chapter:
                    result.append(f"\n\n## {new_chapter}\n")
                current_chapter = new_chapter
            
            # Add text to current paragraph
            current_paragraph.append(text)
            
            # End paragraph on sentence-ending punctuation
            if text[-1] in '.!?':
                add_paragraph()
        
        # Add any remaining text
        add_paragraph()
        
        return '\n'.join(result)

    def _save_summary(self, summary: Dict, base_folder: str, safe_title: str):
        """Save content summary"""
        filename = f"summary.json"
        path = os.path.join(base_folder, 'analysis', filename)
        self._save_json(summary, path)

    def _save_json(self, data: Any, path: str):
        """Save data as JSON file"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            # Save JSON file
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving JSON file {path}: {e}")
            raise
