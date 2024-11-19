from lecture_processor import LectureProcessor

def main():
    # Initialize processor
    processor = LectureProcessor()
    
    # Example usage
    try:
        # Process a single video
        video_url = "https://youtu.be/-UPfyvDJz9I?si=lyRoQf248d13q94p"
        print(f"\nProcessing video: {video_url}")
        result = processor.process_video(video_url)
        print(f"Successfully processed video: {result.metadata.title}")
        
        # Process a playlist
        playlist_url = "https://www.youtube.com/playlist?list=PLgQxZdQXdhkZlLQVU2laGeCwI63CRvONn"
        print(f"\nProcessing playlist: {playlist_url}")
        results = processor.process_playlist(playlist_url)
        print(f"Successfully processed {len(results)} videos from playlist")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
