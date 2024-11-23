import os
import json
import shutil
from typing import List, Optional, Tuple
from video_metadata import VideoMetadata, Chapter, ProcessingResult
from video_downloader import VideoDownloader
from slide_extractor import SlideExtractor
from results_processor import ResultsProcessor
from text_processor import TextProcessor

class LectureProcessor:
    def __init__(self):
        self.video_downloader = VideoDownloader()
        self.slide_extractor = SlideExtractor()
        self.results_processor = ResultsProcessor()
        self.text_processor = TextProcessor()
        # Create cache directory
        self.cache_dir = os.path.join(os.getcwd(), '.cache', 'results')
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_playlist_info(self, playlist_url: str) -> Tuple[str, List[str]]:
        """Get playlist name and video URLs"""
        try:
            # Get playlist metadata
            playlist_info = self.video_downloader.get_playlist_info(playlist_url)
            playlist_name = playlist_info.get('title', 'km')
            
            # Get video URLs
            video_urls = self.video_downloader.get_playlist_videos(playlist_url)
            
            return playlist_name, video_urls
        except Exception as e:
            print(f"Error getting playlist info: {e}")
            return 'km', []

    def _reconstruct_metadata(self, data: dict) -> VideoMetadata:
        """Reconstruct VideoMetadata object from dictionary"""
        # Convert chapters data to Chapter objects
        chapters = [
            Chapter(
                title=chapter['title'],
                start_time=chapter['start_time'],
                end_time=chapter['end_time']
            )
            for chapter in data.get('chapters', [])
        ]
        
        # Create VideoMetadata object
        return VideoMetadata(
            video_id=data['video_id'],
            title=data['title'],
            description=data['description'],
            author=data['author'],
            length=data['length'],
            keywords=data['keywords'],
            publish_date=data['publish_date'],
            views=data['views'],
            initial_keywords=data['initial_keywords'],
            transcript_keywords=data['transcript_keywords'],
            category=data['category'],
            tags=data['tags'],
            captions=data.get('captions', []),  # Make captions optional
            thumbnail_url=data['thumbnail_url'],
            chapters=chapters
        )

    def _get_cached_result(self, video_id: str) -> Optional[ProcessingResult]:
        """Get cached processing result if it exists"""
        cache_path = os.path.join(self.cache_dir, f"{video_id}.json")
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert metadata dictionary to VideoMetadata object
                    metadata = self._reconstruct_metadata(data['metadata'])
                    # Create ProcessingResult object
                    return ProcessingResult(
                        metadata=metadata,
                        slides=data['slides'],
                        content_analysis=data['content_analysis'],
                        transcript=None,  # No longer storing transcript in result
                        summary=data['summary']
                    )
            except Exception as e:
                print(f"Error loading cached result: {e}")
        return None

    def _save_cached_result(self, video_id: str, result: ProcessingResult):
        """Save processing result to cache"""
        try:
            cache_path = os.path.join(self.cache_dir, f"{video_id}.json")
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving result to cache: {e}")

    def _clean_slides_folder(self, base_folder: str):
        """Clean only the slides folder"""
        slides_dir = os.path.join(base_folder, 'slides')
        if os.path.exists(slides_dir):
            # Instead of removing the directory, just remove its contents
            for file in os.listdir(slides_dir):
                file_path = os.path.join(slides_dir, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"Error removing file {file_path}: {e}")
        else:
            os.makedirs(slides_dir, exist_ok=True)

    def process_video(
        self,
        video_url: str,
        duration_limit: Optional[int] = None,
        samples_per_minute: float = 2.0,
        force: bool = False,
        force_slides: bool = False,
        process_slides: bool = True,
        video_order: int = 1,
        playlist_name: str = "km"
    ) -> ProcessingResult:
        """Process single video comprehensively"""
        try:
            # Extract metadata first to get title
            print("Extracting video metadata...")
            metadata = self.video_downloader.extract_metadata(video_url)
            
            # Create folder structure using video title and order
            base_folder = self.results_processor.create_content_folder(
                metadata.title, 
                video_order,
                playlist_name
            )
            
            # Check cache first
            cached_result = None
            if not force:
                cached_result = self._get_cached_result(metadata.video_id)
                if cached_result and not force_slides:
                    print("Using cached processing result...")
                    return cached_result
            
            # Initialize empty slide info
            slide_paths = []
            slide_timestamps = []
            slide_analyses = []
            segments = []
            
            # Process slides if requested
            if process_slides:
                # Download video (use cached if available)
                video_path = self.video_downloader.download_video(video_url, base_folder, force=force)
                if not video_path:
                    raise Exception("Failed to download video")
                
                # Clean slides folder if requested
                if force_slides:
                    self._clean_slides_folder(base_folder)
                
                # Process video for slides
                print("Processing video for slides...")
                slides_dir = os.path.join(base_folder, 'slides')
                slide_paths, slide_timestamps, slide_analyses = self.slide_extractor.process_video(
                    video_path,
                    slides_dir,
                    metadata,
                    threshold=0.99,
                    duration_limit=duration_limit,
                    samples_per_minute=samples_per_minute
                )
                
                # Process transcript with slides
                print("Processing transcript with slides...")
                segments = self.slide_extractor.process_transcript_with_slides(
                    metadata.captions,
                    slide_paths,
                    slide_timestamps,
                    slide_analyses
                )
                
                # Clean up video file if it's not from cache
                print("Cleaning up...")
                if os.path.dirname(video_path) != self.video_downloader.cache_dir:
                    if os.path.exists(video_path):
                        os.remove(video_path)
            
            # Prepare slide info
            slide_info = [{
                'path': path,
                'timestamp': timestamp,
                'analysis': analysis
            } for path, timestamp, analysis in zip(slide_paths, slide_timestamps, slide_analyses)]
            
            # Save results
            print("Saving results...")
            result = self.results_processor.save_results(
                metadata,
                segments,
                slide_info,
                base_folder,
                process_slides=process_slides
            )
            
            # Cache result
            if not force_slides:  # Don't cache if only slides were reprocessed
                self._save_cached_result(metadata.video_id, result)
            
            return result
            
        except Exception as e:
            print(f"Error processing video: {e}")
            raise

    def process_playlist(
        self,
        playlist_url: str,
        force: bool = False,
        force_slides: bool = False,
        process_slides: bool = True
    ) -> List[ProcessingResult]:
        """Process entire playlist"""
        try:
            # Get playlist info
            playlist_name, video_urls = self._get_playlist_info(playlist_url)
            if not video_urls:
                raise Exception("No videos found in playlist")
            
            print(f"Found {len(video_urls)} videos in playlist: {playlist_name}")
            results = []
            
            # Process each video with its order in the playlist
            for idx, video_url in enumerate(video_urls, 1):
                try:
                    print(f"\nProcessing video {idx}/{len(video_urls)}")
                    print(f"URL: {video_url}")
                    
                    result = self.process_video(
                        video_url,
                        force=force,
                        force_slides=force_slides,
                        process_slides=process_slides,
                        video_order=idx,
                        playlist_name=playlist_name
                    )
                    results.append(result)
                    
                except Exception as e:
                    print(f"Error processing video {video_url}: {e}")
                    continue
            
            if not results:
                raise Exception("No videos were successfully processed")
            
            # Create merged content file
            self.results_processor.create_merged_content(results, playlist_name)
            
            return results
            
        except Exception as e:
            print(f"Error processing playlist: {e}")
            raise

    def cleanup_old_results(self, base_pattern: str):
        """Clean up old processing results"""
        try:
            # Find all directories matching the pattern
            base_dir = os.path.dirname(base_pattern)
            if os.path.exists(base_dir):
                for item in os.listdir(base_dir):
                    if os.path.isdir(os.path.join(base_dir, item)) and '_' in item:
                        folder_path = os.path.join(base_dir, item)
                        try:
                            shutil.rmtree(folder_path)
                            print(f"Removed {folder_path}")
                        except Exception as e:
                            print(f"Error removing {folder_path}: {e}")
        except Exception as e:
            print(f"Error during cleanup: {e}")

    def get_processing_stats(self, results: List[ProcessingResult]) -> dict:
        """Get statistics about processed videos"""
        try:
            total_duration = sum(r.metadata.length for r in results)
            total_slides = sum(len(r.slides) for r in results)
            total_segments = sum(len(r.content_analysis) for r in results)
            
            return {
                'total_videos': len(results),
                'total_duration': str(total_duration),
                'total_slides': total_slides,
                'total_segments': total_segments,
                'videos': [{
                    'title': r.metadata.title,
                    'duration': str(r.metadata.length),
                    'slides': len(r.slides),
                    'segments': len(r.content_analysis)
                } for r in results]
            }
        except Exception as e:
            print(f"Error getting processing stats: {e}")
            return {}
