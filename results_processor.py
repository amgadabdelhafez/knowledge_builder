import os
import json
import re
from typing import Dict, List, Any, Tuple
from datetime import datetime
from collections import Counter
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
            # Generate improved summary
            summary = self._generate_summary(metadata, segments, slide_info)
            
            # Create result object
            result = ProcessingResult(
                metadata=metadata,
                slides=slide_info if process_slides else [],
                content_analysis=[] if not process_slides else [segment.to_dict() for segment in segments],
                transcript=None,
                summary=summary
            )
            
            # Get safe title for filenames
            safe_title = os.path.basename(base_folder)
            
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
        """Generate improved comprehensive summary of video content"""
        try:
            if not segments:
                return self._generate_basic_summary(metadata, slide_info)

            # Extract key concepts and themes
            concepts = self._extract_key_concepts(segments)
            themes = self._identify_themes(segments)
            
            # Generate chapter summaries
            chapter_summaries = self._generate_chapter_summaries(segments, metadata.chapters)
            
            # Calculate content statistics
            content_stats = self._calculate_content_statistics(segments)
            
            return {
                'title': metadata.title,
                'author': metadata.author,
                'duration': str(metadata.length),
                'date': metadata.publish_date,
                'overview': {
                    'key_concepts': concepts[:5] if concepts else [],  # Top 5 key concepts
                    'main_themes': themes[:3] if themes else [],      # Top 3 themes
                    'slide_count': len(slide_info),
                    'chapter_count': len(metadata.chapters)
                },
                'chapter_summaries': chapter_summaries,
                'technical_content': {
                    'key_terms': self._get_significant_technical_terms(segments),
                    'technologies_discussed': self._extract_technologies(segments),
                    'content_types': self._analyze_content_types(segments)
                },
                'statistics': content_stats
            }
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return {}

    def _generate_basic_summary(self, metadata: VideoMetadata, slide_info: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate basic summary when no segments are available"""
        return {
            'title': metadata.title,
            'author': metadata.author,
            'duration': str(metadata.length),
            'date': metadata.publish_date,
            'overview': {
                'slide_count': len(slide_info),
                'chapter_count': len(metadata.chapters)
            }
        }

    def _extract_key_concepts(self, segments: List[ContentSegment]) -> List[Dict[str, Any]]:
        """Extract key concepts with relevance scores"""
        # Collect all keywords from segments
        all_keywords = []
        for segment in segments:
            all_keywords.extend(segment.keywords)
        
        # Count frequencies
        concept_scores = Counter(all_keywords)
        
        # Calculate relevance scores
        total_segments = len(segments) if segments else 1
        concepts = []
        for concept, count in concept_scores.most_common(10):
            relevance = count / total_segments
            concepts.append({
                'concept': concept,
                'relevance': relevance,
                'frequency': count
            })
        
        return concepts

    def _identify_themes(self, segments: List[ContentSegment]) -> List[Dict[str, Any]]:
        """Identify main themes from segments"""
        # Combine related keywords into themes
        theme_keywords = {}
        
        for segment in segments:
            for keyword in segment.keywords:
                related_theme = None
                # Try to find a related existing theme
                for theme, keywords in theme_keywords.items():
                    if any(self._are_terms_related(keyword, k) for k in keywords):
                        related_theme = theme
                        break
                
                if related_theme:
                    theme_keywords[related_theme].add(keyword)
                else:
                    theme_keywords[keyword] = {keyword}
        
        # Score themes by size and keyword relevance
        theme_scores = [
            {
                'theme': self._get_theme_name(list(keywords)),  # Convert set to list
                'keywords': list(keywords),
                'relevance': len(keywords) / len(segments) if segments else 0
            }
            for keywords in theme_keywords.values()
            if len(keywords) > 1  # Only include themes with multiple related keywords
        ]
        
        return sorted(theme_scores, key=lambda x: x['relevance'], reverse=True)

    def _are_terms_related(self, term1: str, term2: str) -> bool:
        """Check if two terms are semantically related"""
        # Use spaCy similarity
        doc1 = self.text_processor.nlp(term1)
        doc2 = self.text_processor.nlp(term2)
        return doc1.similarity(doc2) > 0.6

    def _get_theme_name(self, keywords: List[str]) -> str:
        """Generate a representative name for a theme"""
        # Use the most frequent keyword as the theme name
        keyword_freq = Counter(keywords)
        return keyword_freq.most_common(1)[0][0] if keywords else "unknown"

    def _generate_chapter_summaries(self, segments: List[ContentSegment], chapters: List[Any]) -> List[Dict[str, Any]]:
        """Generate concise summaries for each chapter"""
        chapter_segments = {}
        
        # Group segments by chapter
        for segment in segments:
            chapter_idx = self._find_chapter_index(segment, chapters)
            if chapter_idx is not None:
                if chapter_idx not in chapter_segments:
                    chapter_segments[chapter_idx] = []
                chapter_segments[chapter_idx].append(segment)
        
        # Generate summaries
        summaries = []
        for idx, chapter in enumerate(chapters):
            if idx in chapter_segments:
                chapter_segs = chapter_segments[idx]
                summaries.append({
                    'title': chapter.title,
                    'duration': chapter.end_time - chapter.start_time,
                    'key_points': self._extract_key_points(chapter_segs),
                    'technical_terms': list(set().union(*(set(seg.technical_terms) for seg in chapter_segs)))[:5]
                })
        
        return summaries

    def _find_chapter_index(self, segment: ContentSegment, chapters: List[Any]) -> int:
        """Find which chapter a segment belongs to"""
        for idx, chapter in enumerate(chapters):
            if chapter.start_time <= segment.start_time < chapter.end_time:
                return idx
        return None

    def _extract_key_points(self, segments: List[ContentSegment]) -> List[str]:
        """Extract key points from a group of segments"""
        # Combine keywords and find most significant ones
        all_keywords = []
        for segment in segments:
            all_keywords.extend(segment.keywords)
        
        # Return top 3 most frequent keywords
        return [kw for kw, _ in Counter(all_keywords).most_common(3)] if all_keywords else []

    def _get_significant_technical_terms(self, segments: List[ContentSegment]) -> List[str]:
        """Get most significant technical terms"""
        all_terms = []
        for segment in segments:
            all_terms.extend(segment.technical_terms)
        
        term_freq = Counter(all_terms)
        return [term for term, freq in term_freq.items() if freq > 1]

    def _extract_technologies(self, segments: List[ContentSegment]) -> List[str]:
        """Extract mentioned technologies"""
        technologies = set()
        for segment in segments:
            # Look for technology-related terms in both transcript and extracted text
            combined_text = f"{segment.transcript_text} {segment.extracted_text}"
            # Look for technology-related terms
            tech_patterns = [
                r'\b[A-Z][A-Za-z0-9]+(\.js|\.py|\.java)?\b',  # Programming languages and frameworks
                r'\b[A-Z][A-Z0-9]+\b',  # Acronyms
                r'\b(API|SDK|Framework|Platform|Tool|Library)\b'  # Technical terms
            ]
            for pattern in tech_patterns:
                matches = re.finditer(pattern, combined_text)
                technologies.update(match.group() for match in matches)
        
        return sorted(list(technologies))

    def _analyze_content_types(self, segments: List[ContentSegment]) -> Dict[str, int]:
        """Analyze distribution of content types"""
        type_counts = Counter(segment.content_type for segment in segments)
        return dict(type_counts)

    def _calculate_content_statistics(self, segments: List[ContentSegment]) -> Dict[str, Any]:
        """Calculate detailed content statistics"""
        if not segments:
            return {
                'total_segments': 0,
                'avg_segment_duration': 0,
                'keyword_density': 0,
                'technical_density': 0
            }
            
        total_keywords = sum(len(segment.keywords) for segment in segments)
        total_terms = sum(len(segment.technical_terms) for segment in segments)
        
        return {
            'total_segments': len(segments),
            'avg_segment_duration': sum((s.end_time - s.start_time) for s in segments) / len(segments),
            'keyword_density': total_keywords / len(segments),
            'technical_density': total_terms / len(segments)
        }

    def _save_metadata(self, metadata: VideoMetadata, base_folder: str, safe_title: str):
        """Save video metadata"""
        metadata_dict = metadata.to_dict()
        metadata_dict.pop('captions', None)
        path = os.path.join(base_folder, 'metadata', 'metadata.json')
        self._save_json(metadata_dict, path)

    def _save_content_analysis(self, analysis: List[Dict], base_folder: str, safe_title: str):
        """Save content analysis results"""
        path = os.path.join(base_folder, 'analysis', 'content_analysis.json')
        self._save_json(analysis, path)

    def _save_transcripts(self, transcript: List[Dict], chapters: List[Any], base_folder: str, safe_title: str):
        """Save transcripts in multiple formats"""
        # Save raw transcript
        raw_path = os.path.join(base_folder, 'transcripts', 'transcript_raw.json')
        self._save_json(transcript, raw_path)
        
        # Save clean transcript
        clean_transcript = self._generate_clean_transcript(transcript, chapters)
        clean_path = os.path.join(base_folder, 'transcripts', 'transcript_clean.txt')
        
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
            timestamp = entry.get('start', 0)
            text = entry.get('text', '').strip()
            
            if not text:
                continue
            
            new_chapter = None
            for chapter in chapters:
                if chapter.start_time <= timestamp < chapter.end_time:
                    new_chapter = chapter.title
                    break
            
            if new_chapter != current_chapter:
                add_paragraph()
                if new_chapter:
                    result.append(f"\n\n## {new_chapter}\n")
                current_chapter = new_chapter
            
            current_paragraph.append(text)
            
            if text[-1] in '.!?':
                add_paragraph()
        
        add_paragraph()
        return '\n'.join(result)

    def _save_summary(self, summary: Dict, base_folder: str, safe_title: str):
        """Save content summary"""
        path = os.path.join(base_folder, 'analysis', 'summary.json')
        self._save_json(summary, path)

    def _save_json(self, data: Any, path: str):
        """Save data as JSON file"""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving JSON file {path}: {e}")
            raise
