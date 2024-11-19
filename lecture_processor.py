import os
from typing import List, Optional
from video_metadata import VideoMetadata, ProcessingResult
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

    def process_video(self, video_url: str) -> ProcessingResult:
        """Process single video comprehensively"""
        try:
            # Extract metadata
            print("Extracting video metadata...")
            metadata = self.video_downloader.extract_metadata(video_url)
            
            # Create folder structure
            base_folder = self.results_processor.create_content_folder(metadata.video_id)
            
            # Download video
            print("Downloading video...")
            video_path = self.video_downloader.download_video(video_url, base_folder)
            if not video_path:
                raise Exception("Failed to download video")
            
            # Process video for slides
            print("Processing video for slides...")
            slide_paths, slide_timestamps, slide_analyses = self.slide_extractor.process_video(
                video_path,
                base_folder,
                metadata
            )
            
            # Process transcript with slides
            print("Processing transcript with slides...")
            segments = self.slide_extractor.process_transcript_with_slides(
                metadata.captions,
                slide_paths,
                slide_timestamps,
                slide_analyses
            )
            
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
                base_folder
            )
            
            # Clean up video file
            print("Cleaning up...")
            if os.path.exists(video_path):
                os.remove(video_path)
            
            return result
            
        except Exception as e:
            print(f"Error processing video: {e}")
            raise

    def process_playlist(self, playlist_url: str) -> List[ProcessingResult]:
        """Process entire playlist"""
        try:
            # Get list of video URLs from playlist
            video_urls = self.video_downloader.get_playlist_videos(playlist_url)
            if not video_urls:
                raise Exception("No videos found in playlist")
            
            print(f"Found {len(video_urls)} videos in playlist")
            results = []
            
            # Process each video
            for idx, video_url in enumerate(video_urls, 1):
                try:
                    print(f"\nProcessing video {idx}/{len(video_urls)}")
                    print(f"URL: {video_url}")
                    
                    result = self.process_video(video_url)
                    results.append(result)
                    
                except Exception as e:
                    print(f"Error processing video {video_url}: {e}")
                    continue
            
            if not results:
                raise Exception("No videos were successfully processed")
            
            return results
            
        except Exception as e:
            print(f"Error processing playlist: {e}")
            raise

    def cleanup_old_results(self, base_folder: str):
        """Clean up old processing results"""
        try:
            if os.path.exists(base_folder):
                import shutil
                shutil.rmtree(base_folder)
        except Exception as e:
            print(f"Error cleaning up {base_folder}: {e}")

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
