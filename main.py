from lecture_processor import LectureProcessor
import argparse
import os
import shutil

def setup_cache_directories():
    """Create cache directories if they don't exist"""
    cache_dirs = [
        os.path.join(os.getcwd(), '.cache'),
        os.path.join(os.getcwd(), '.cache', 'videos'),
        os.path.join(os.getcwd(), '.cache', 'results')
    ]
    for directory in cache_dirs:
        os.makedirs(directory, exist_ok=True)

def clean_slides_folder(title: str, video_order: int = 1, playlist_name: str = "km"):
    """Clean only the slides folder for a specific video"""
    processor = LectureProcessor()
    results_processor = processor.results_processor
    safe_title = results_processor._sanitize_filename(title)
    safe_playlist = results_processor._sanitize_filename(playlist_name)
    slides_dir = os.path.join(os.getcwd(), f"{safe_playlist}_{video_order:02d}_{safe_title}", 'slides')
    if os.path.exists(slides_dir):
        print(f"\nCleaning slides folder: {slides_dir}")
        shutil.rmtree(slides_dir)
        print("Slides cleanup completed")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Knowledge Builder - Video Lecture Processor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Output Structure (using playlist name and video order):
  python_basics_01_introduction/        # First video in 'Python Basics' playlist
  ├── slides/                          # Extracted slides (if not using --transcript-only)
  ├── metadata/           
  │   └── metadata.json
  ├── analysis/          
  │   ├── content_analysis.json        # Slide analysis (if not using --transcript-only)
  │   └── summary.json
  └── transcripts/       
      ├── transcript_raw.json          # Full transcript with timestamps
      └── transcript_clean.txt         # Clean transcript grouped by chapters

  python_basics_02_variables/          # Second video
  ├── ...

  python_basics_merged_content.md      # Combined content from all videos

For playlists:
- Folders are prefixed with sanitized playlist name
- Videos are numbered in playlist order
- A merged content file is created with all video content

For single videos:
- Default playlist name is 'km'
- Number defaults to 01
        """
    )
    
    # Add cleanup arguments
    cleanup_group = parser.add_mutually_exclusive_group()
    cleanup_group.add_argument('--clean', action='store_true', 
                             help='Clean all output folders and ignore cache')
    cleanup_group.add_argument('--clean-slides', action='store_true',
                             help='Clean only slides folder and reprocess slides')
    
    # Add mutually exclusive group for video or playlist URL
    url_group = parser.add_mutually_exclusive_group(required=True)
    url_group.add_argument('--video', type=str, help='URL of the video to process')
    url_group.add_argument('--playlist', type=str, help='URL of the playlist to process')
    
    # Add duration limit argument
    parser.add_argument('--duration', type=int, 
                       help='Number of seconds of video to process (default: entire video)')
    
    # Add samples per minute argument
    parser.add_argument('--samples', type=float, default=2.0,
                       help='Number of samples to extract per minute of video (default: 2.0)')
    
    # Add transcript-only argument
    parser.add_argument('--transcript-only', action='store_true',
                       help='Only process transcript without extracting slides')
    
    args = parser.parse_args()
    
    # Create cache directories
    setup_cache_directories()
    
    # Initialize processor
    processor = LectureProcessor()
    
    try:
        if args.clean:
            # Clean all output folders
            print("\nCleaning all output folders...")
            processor.cleanup_old_results(os.path.join(os.getcwd(), ""))
            print("Cleanup completed")
        elif args.clean_slides and args.video and not args.transcript_only:
            # Get video title first
            metadata = processor.video_downloader.extract_metadata(args.video)
            clean_slides_folder(metadata.title)
        
        # Process based on provided URL
        if args.video:
            print(f"\nProcessing video: {args.video}")
            if args.transcript_only:
                print("Processing transcript only (skipping slide extraction)")
            result = processor.process_video(
                args.video,
                duration_limit=args.duration,
                samples_per_minute=args.samples,
                force=args.clean,  # Force reprocessing if clean flag is set
                force_slides=args.clean_slides,  # Force slides reprocessing if clean-slides flag is set
                process_slides=not args.transcript_only  # Skip slide processing if transcript-only
            )
            print(f"Successfully processed video: {result.metadata.title}")
            
            # Get safe title for display
            safe_title = processor.results_processor._sanitize_filename(result.metadata.title)
            folder_name = f"km_01_{safe_title}"
            print("\nOutput files:")
            print(f"Folder: {folder_name}/")
            print("  - transcripts/transcript_raw.json (Full transcript with timestamps)")
            print("  - transcripts/transcript_clean.txt (Clean transcript grouped by chapters)")
            if not args.transcript_only:
                print("  - slides/ (Extracted slides)")
                print("  - analysis/content_analysis.json (Slide analysis)")
            print("  - analysis/summary.json (Video summary)")
            print("  - metadata/metadata.json (Video metadata)")
            print(f"Merged content: km_merged_content.md")
        else:
            print(f"\nProcessing playlist: {args.playlist}")
            if args.transcript_only:
                print("Processing transcripts only (skipping slide extraction)")
            results = processor.process_playlist(
                args.playlist,
                force=args.clean,  # Force reprocessing if clean flag is set
                force_slides=args.clean_slides,  # Force slides reprocessing if clean-slides flag is set
                process_slides=not args.transcript_only  # Skip slide processing if transcript-only
            )
            print(f"Successfully processed {len(results)} videos from playlist")
            
            # Get playlist name for display
            playlist_name = processor.results_processor._sanitize_filename(
                processor.video_downloader.get_playlist_info(args.playlist).get('title', 'km')
            )
            print("\nOutput folders:")
            for i, result in enumerate(results, 1):
                safe_title = processor.results_processor._sanitize_filename(result.metadata.title)
                print(f"{playlist_name}_{i:02d}_{safe_title}/")
            print(f"\nMerged content: {playlist_name}_merged_content.md")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
