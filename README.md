# Knowledge Builder

![Python Tests](https://github.com/amgadabdelhafez/knowledge_builder/actions/workflows/python-tests.yml/badge.svg)

A Python-based tool for extracting, analyzing, and organizing educational content from video lectures. This tool processes video lectures to extract slides, transcripts, and technical content, making it easier to study and reference the material.

## Features

- **Video Processing**

  - Downloads and processes video lectures
  - Extracts video metadata and transcripts
  - Supports both individual videos and playlists

- **Slide Extraction**

  - Automatically detects and extracts slides from video
  - Removes duplicate frames
  - Maintains temporal alignment with video

- **Content Analysis**

  - Extracts keywords and technical terms
  - Classifies content into technical domains
  - Processes text from slides and transcripts
  - Detects diagrams and technical content

- **Organized Output**
  - Creates structured content folders
  - Aligns transcripts with slides
  - Generates comprehensive summaries
  - Saves results in easily accessible formats

## Project Structure

```
knowledge_builder/
├── video_downloader.py     # Video download and metadata extraction
├── image_processor.py      # Frame and slide processing
├── text_processor.py       # Text analysis and classification
├── slide_extractor.py      # Slide extraction and processing
├── content_segment.py      # Content segmentation and alignment
├── results_processor.py    # Results organization and storage
├── video_metadata.py       # Data structures for video metadata
├── main.py                # Main application entry point
└── tests/
    ├── test_video_extraction.py
    ├── test_frame_extraction.py
    ├── test_content_analysis.py
    └── test_integration.py
```

## Components

### Video Downloader

- Downloads videos using yt-dlp
- Extracts video metadata
- Retrieves video transcripts
- Handles both individual videos and playlists

### Image Processor

- Extracts frames from videos
- Detects and removes duplicate slides
- Performs OCR on slides
- Detects diagrams and technical content
- Classifies image content

### Text Processor

- Extracts keywords and technical terms
- Classifies content into technical domains
- Processes transcripts and slide text
- Generates text statistics

### Slide Extractor

- Processes video for slide extraction
- Aligns slides with transcript
- Analyzes slide content
- Maintains temporal information

### Content Segment

- Represents content segments
- Aligns transcript with slides
- Stores analysis results
- Provides timing information

### Results Processor

- Organizes processed content
- Creates folder structures
- Saves analysis results
- Generates summaries

## Installation

1. Clone the repository:

```bash
git clone https://github.com/amgadabdelhafez/knowledge_builder.git
cd knowledge_builder
```

2. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from lecture_processor import LectureProcessor

# Initialize processor
processor = LectureProcessor()

# Process single video
result = processor.process_video("https://www.youtube.com/watch?v=video_id")

# Process playlist
results = processor.process_playlist("https://www.youtube.com/playlist?list=playlist_id")
```

### Output Structure

```
output/
├── lecture_[video_id]/
│   ├── slides/
│   │   ├── slide_001.jpg
│   │   ├── slide_002.jpg
│   │   └── ...
│   ├── analysis/
│   │   ├── content_analysis.json
│   │   └── summary.json
│   ├── metadata/
│   │   └── video_metadata.json
│   └── transcripts/
│       └── transcript.json
```

## Development

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test category
python -m pytest test_video_extraction.py
python -m pytest test_frame_extraction.py
python -m pytest test_content_analysis.py
python -m pytest test_integration.py
```

### Adding New Features

1. Create new module in project root
2. Add corresponding test file in tests directory
3. Update documentation
4. Run tests to ensure everything works

## Requirements

- Python 3.8+
- OpenCV
- spaCy
- PyTesseract
- yt-dlp
- transformers
- torch
- Other dependencies in requirements.txt

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
