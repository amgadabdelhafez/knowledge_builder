# Knowledge Builder

A tool for extracting and processing slides from educational videos.

## Session Resume

To continue development from the current point, use this prompt:

```
Continue improving the slide extraction with these priorities:
1. Enhance OCR text extraction in image_processor.py:
   - Better preprocessing for text detection
   - Improved text similarity comparison
   - Smarter handling of slides with same diagrams but different text
2. Test the OCR-based filtering with:
   python main.py --clean-slides --video "https://www.youtube.com/watch?v=NGXZ-mYqyUo" --samples 1.0

Current status:
- OCR and text extraction added to image_processor.py
- Chapter-based naming implemented in slide_extractor.py
- Text similarity comparison added
- Need to improve text preprocessing and duplicate detection

Key files to focus on:
1. image_processor.py - OCR and text processing
2. slide_extractor.py - Chapter handling and slide organization
```

## Current Features

### Video Processing

- Downloads and caches videos to avoid reprocessing
- Extracts chapters from video metadata and descriptions
- Skips intro/outro chapters automatically
- Supports processing specific video segments

### Slide Extraction

- OCR-based slide detection and filtering
- Text similarity comparison to avoid duplicates
- Chapter-based slide organization and naming
- Intelligent frame sampling based on chapter duration
- Caches processed results for faster reuse

### Slide Analysis Logic

#### Content Segmentation

- Each slide is broken down into segments based on the transcript timing
- Segments represent distinct moments in the presentation where specific content is discussed
- Multiple segments can reference the same slide while having unique transcript content

#### Slide Content Analysis

1. Visual Analysis

   - OCR extracts text from slide images
   - Content type classification (text, diagram, mixed)
   - Diagram detection and component analysis
   - Visual similarity comparison between slides

2. Text Processing

   - Extracted text is processed to identify:
     - Main content
     - Keywords
     - Technical terms
     - Diagrams and their components

3. Segment Generation

   - Each segment combines:
     - Slide content (extracted text, content type)
     - Transcript text
     - Timing information (start/end)
     - Generated keywords and technical terms

4. Smart Content Deduplication

   - Slide-specific content (extracted text, content type) remains consistent for segments sharing a slide
   - Each segment gets unique keywords based on:
     - Common keywords (appearing in both slide and transcript)
     - Unique keywords from slide content
     - Unique keywords from transcript text
   - Technical terms are filtered to only include those that appear in the segment's transcript

5. Content Confidence
   - Each segment includes confidence scores for:
     - Content type classification
     - Text extraction accuracy
     - Keyword relevance
     - Technical term identification

### Slide Filtering

- Minimum text length requirements
- Text similarity detection
- Content-based filtering (text vs diagrams)
- Duplicate detection across frames

## Usage

### Basic Usage

```bash
# Process a video with default settings
python main.py --video "https://www.youtube.com/watch?v=VIDEO_ID"

# Process with specific samples per minute
python main.py --video "https://www.youtube.com/watch?v=VIDEO_ID" --samples 1.0

# Clean and reprocess everything
python main.py --clean --video "https://www.youtube.com/watch?v=VIDEO_ID"

# Only reprocess slides
python main.py --clean-slides --video "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Output Structure

```
processed_lecture_VIDEO_ID/
├── slides/              # Extracted slides named by chapter
│   ├── 01_ChapterName_01.jpg
│   ├── 01_ChapterName_02.jpg
│   └── ...
├── metadata/           # Video metadata
│   └── video_metadata.json
├── analysis/          # Content analysis
│   ├── content_analysis.json
│   └── summary.json
└── transcripts/       # Video transcripts
    └── transcript.json
```

#### Content Analysis Format

```json
{
  "start_time": 10.5,
  "end_time": 15.2,
  "duration": "0:00:04.700000",
  "slide_index": 2,
  "transcript_text": "Let's look at how this works in practice",
  "extracted_text": "Implementation Example",
  "keywords": ["implementation", "example", "practice", "works"],
  "technical_terms": ["implementation"],
  "content_type": "text",
  "confidence": 0.95
}
```

## Current Development Status

### Recently Added

- Chapter-based slide naming
- OCR-based slide filtering
- Text similarity detection
- Slide deduplication
- Video and result caching
- Smart content segmentation
- Unique keyword generation per segment
- Processed folder prefixing

### In Progress

- [ ] Improve OCR accuracy
- [ ] Better text similarity comparison
- [ ] Smarter duplicate detection
- [ ] Enhanced chapter detection

### Key Files

- `main.py` - Main entry point and CLI
- `lecture_processor.py` - Core video processing
- `image_processor.py` - Slide extraction and OCR
- `slide_extractor.py` - Chapter-based extraction and content analysis
- `video_downloader.py` - Video downloading and caching
- `content_segment.py` - Content segmentation and analysis
- `similarity_analyzer.py` - Text and visual similarity analysis
- `text_processor.py` - Text analysis and keyword extraction

## Development Notes

### Current Focus

- Improving OCR-based slide detection
- Better handling of duplicate slides
- Enhanced text similarity comparison
- Chapter-based organization
- Smart content segmentation

### Testing

```bash
# Test with sample video
python main.py --clean-slides --video "https://www.youtube.com/watch?v=NGXZ-mYqyUo" --samples 1.0
```

### Cache Locations

- Videos: `.cache/videos/`
- Results: `.cache/results/`

### Command Reference

```bash
# Full reprocessing
python main.py --clean --video "URL" --samples 1.0

# Slides only reprocessing
python main.py --clean-slides --video "URL" --samples 1.0

# Process specific duration
python main.py --video "URL" --duration 300 --samples 1.0
```

## Next Steps

1. Implement better OCR preprocessing
2. Add text-based slide grouping
3. Improve chapter name cleaning
4. Add slide content validation
5. Enhance duplicate detection logic
6. Improve keyword relevance scoring
7. Add support for more content types
8. Enhance technical term detection

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License - See LICENSE file for details
