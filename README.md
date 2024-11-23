# Knowledge Builder

A tool for extracting and processing slides from educational videos.

## Text Processing System

The text processing system has been modularized into focused components:

### Components

1. **Knowledge Base** (knowledge_base.py)

   - Manages technical terms, phrases, organizations, and locations
   - Learns and updates from processed content
   - Persists learned terms in knowledge_base.json
   - Categories:
     - Technical indicators (single terms)
     - Technical phrases (compound terms)
     - Organizations
     - Locations
     - Common words (for filtering)

2. **Text Cleaner** (text_cleaner.py)

   - Text preprocessing and normalization
   - Specialized cleaning for:
     - Technical terms
     - Code blocks
     - HTML content
     - Markdown formatting
   - Filename sanitization
   - Whitespace normalization

3. **Keyword Extractor** (keyword_extractor.py)

   - Context-aware keyword extraction
   - Relevance scoring
   - Key phrase extraction
   - Frequency analysis
   - Context window extraction
   - Keyword statistics

4. **Technical Analyzer** (technical_analyzer.py)

   - Technical term detection
   - Domain classification
   - Code element extraction
   - Complexity analysis
   - Pattern matching for:
     - File extensions
     - Acronyms
     - Version numbers
     - CamelCase identifiers

5. **Text Processor** (text_processor.py)
   - Main orchestrator
   - Context-aware analysis using title and description
   - Transcript segment analysis
   - Comprehensive content statistics

### Usage

```python
from text_processor import TextProcessor

# Initialize processor
processor = TextProcessor()

# Analyze content with context
analysis = processor.analyze_content(
    title="Video Title",
    description="Video Description",
    content="Main Content"
)

# Analyze transcript
transcript_analysis = processor.analyze_transcript(transcript_segments)
```

### Analysis Output

The content analysis provides:

```python
{
    'metadata': {
        'title': str,
        'description': str,
        'word_count': int
    },
    'context': {
        'keywords': [
            {
                'keyword': str,
                'relevance': float,
                'frequency': int
            }
        ],
        'primary_topic': str
    },
    'content_analysis': {
        'keywords': [...],
        'technical_terms': [
            {
                'term': str,
                'type': str,
                'context': str
            }
        ],
        'domain_classification': {
            'domain': float  # confidence score
        },
        'statistics': {
            'total_terms': int,
            'unique_terms': int,
            'technical_density': float,
            'primary_domain': str
        }
    },
    'key_phrases': [
        {
            'text': str,
            'technical_terms': [str],
            'relevance': float
        }
    ],
    'technical_elements': {
        'functions': [str],
        'variables': [str],
        'classes': [str],
        'imports': [str],
        'urls': [str]
    }
}
```

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

   - Context-aware keyword extraction
   - Technical term detection
   - Domain classification
   - Code element extraction
   - Comprehensive statistics

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

### Content Analysis Format

```json
{
  "metadata": {
    "title": "Video Title",
    "description": "Video Description",
    "word_count": 1000
  },
  "context": {
    "keywords": [
      {
        "keyword": "machine learning",
        "relevance": 0.85,
        "frequency": 5
      }
    ],
    "primary_topic": "machine learning"
  },
  "content_analysis": {
    "keywords": [...],
    "technical_terms": [
      {
        "term": "neural network",
        "type": "known_term",
        "context": "...using a neural network for classification..."
      }
    ],
    "domain_classification": {
      "machine_learning": 0.8,
      "data_analytics": 0.4
    },
    "statistics": {
      "total_terms": 50,
      "unique_terms": 30,
      "technical_density": 0.15,
      "primary_domain": "machine_learning"
    }
  }
}
```

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

1. Improve OCR preprocessing
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
