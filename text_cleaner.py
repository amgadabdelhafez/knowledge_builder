import re
from typing import List

class TextCleaner:
    def __init__(self):
        # Regex patterns for cleaning
        self.space_pattern = re.compile(r'\s+')
        self.special_char_pattern = re.compile(r'[^\w\s-]|(?<=[^a-zA-Z0-9])-|-(?=[^a-zA-Z0-9])')
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        self.email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
        self.number_pattern = re.compile(r'\b\d+\b')

    def clean_text(self, text: str, keep_case: bool = False) -> str:
        """Clean and normalize text"""
        # Remove URLs
        text = self.url_pattern.sub('', text)
        
        # Remove email addresses
        text = self.email_pattern.sub('', text)
        
        # Normalize whitespace
        text = self.space_pattern.sub(' ', text)
        
        # Remove special characters except hyphens in compound words
        text = self.special_char_pattern.sub('', text)
        
        # Convert to lowercase if specified
        if not keep_case:
            text = text.lower()
        
        return text.strip()

    def clean_technical_term(self, term: str) -> str:
        """Clean a technical term while preserving important characters"""
        # Keep case for technical terms
        term = self.space_pattern.sub(' ', term)
        # Remove special characters except those common in technical terms
        term = re.sub(r'[^\w\s\-./]', '', term)
        return term.strip()

    def split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting - can be improved with more sophisticated rules
        text = self.clean_text(text, keep_case=True)
        sentences = re.split(r'[.!?]+\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def extract_numbers(self, text: str) -> List[str]:
        """Extract numbers from text"""
        return self.number_pattern.findall(text)

    def normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace in text"""
        return self.space_pattern.sub(' ', text).strip()

    def remove_punctuation(self, text: str) -> str:
        """Remove punctuation from text"""
        return re.sub(r'[^\w\s]', '', text)

    def clean_filename(self, text: str, max_length: int = 200) -> str:
        """Clean text for use as filename"""
        # Remove invalid filename characters
        text = re.sub(r'[<>:"/\\|?*]', '', text)
        # Replace spaces with underscores
        text = text.replace(' ', '_')
        # Remove any remaining invalid characters
        text = re.sub(r'[^\w\-]', '', text)
        # Truncate if too long
        return text[:max_length]

    def clean_html(self, text: str) -> str:
        """Remove HTML tags from text"""
        return re.sub(r'<[^>]+>', '', text)

    def clean_markdown(self, text: str) -> str:
        """Remove Markdown formatting from text"""
        # Remove headers
        text = re.sub(r'#+\s+', '', text)
        # Remove bold/italic
        text = re.sub(r'[*_]{1,2}([^*_]+)[*_]{1,2}', r'\1', text)
        # Remove links
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        # Remove code blocks
        text = re.sub(r'`[^`]+`', '', text)
        return text.strip()

    def normalize_technical_terms(self, terms: List[str]) -> List[str]:
        """Normalize a list of technical terms"""
        normalized = []
        for term in terms:
            # Clean the term
            term = self.clean_technical_term(term)
            # Skip empty terms
            if not term:
                continue
            # Add normalized term
            normalized.append(term)
        return list(set(normalized))  # Remove duplicates

    def extract_code_blocks(self, text: str) -> List[str]:
        """Extract code blocks from text"""
        # Find text between backticks or indented blocks
        code_blocks = []
        # Backtick blocks
        backtick_blocks = re.findall(r'```[^\n]*\n(.*?)```', text, re.DOTALL)
        code_blocks.extend(backtick_blocks)
        # Indented blocks
        lines = text.split('\n')
        current_block = []
        for line in lines:
            if line.startswith('    ') or line.startswith('\t'):
                current_block.append(line.lstrip())
            elif current_block:
                code_blocks.append('\n'.join(current_block))
                current_block = []
        if current_block:
            code_blocks.append('\n'.join(current_block))
        return code_blocks

    def clean_code(self, code: str) -> str:
        """Clean code while preserving syntax"""
        # Remove comments
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)  # Python comments
        code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)  # C-style comments
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)  # Multi-line C-style comments
        # Normalize whitespace
        code = self.normalize_whitespace(code)
        return code.strip()
