from typing import List, Dict, Any
from knowledge_base import KnowledgeBase
from text_cleaner import TextCleaner
from keyword_extractor import KeywordExtractor
from technical_analyzer import TechnicalAnalyzer
import spacy

class TextProcessor:
    def __init__(self, knowledge_base_path: str = 'knowledge_base.json'):
        # Initialize components
        self.knowledge_base = KnowledgeBase(knowledge_base_path)
        self.text_cleaner = TextCleaner()
        self.keyword_extractor = KeywordExtractor(self.knowledge_base, self.text_cleaner)
        self.technical_analyzer = TechnicalAnalyzer(self.knowledge_base, self.text_cleaner)
        
        # Initialize spaCy model
        try:
            self.nlp = spacy.load("en_core_web_lg")
        except OSError:
            # If model not found, download and load it
            spacy.cli.download("en_core_web_lg")
            self.nlp = spacy.load("en_core_web_lg")

    def extract_keywords(self, text: str, min_freq: int = 2, min_relevance: float = 0.3) -> List[Dict[str, float]]:
        """Extract keywords from text using the keyword extractor"""
        return self.keyword_extractor.extract_keywords(text, min_freq, min_relevance)

    def detect_technical_terms(self, text: str) -> List[str]:
        """Detect technical terms in text using the technical analyzer"""
        return self.technical_analyzer.detect_technical_terms(text)

    def analyze_content(self, title: str, description: str, content: str) -> Dict[str, Any]:
        """Analyze content with context from title and description"""
        # Clean inputs
        title = self.text_cleaner.clean_text(title)
        description = self.text_cleaner.clean_text(description)
        content = self.text_cleaner.clean_text(content)
        
        # Extract context keywords from title and description
        context_keywords = self._extract_context_keywords(title, description)
        
        # Perform technical analysis
        technical_analysis = self.technical_analyzer.analyze_technical_content(content)
        
        # Extract keywords with context influence
        keywords = self._extract_keywords_with_context(content, context_keywords)
        
        # Classify content domain
        domain_classification = self.technical_analyzer.classify_domain(content)
        
        # Generate comprehensive analysis
        return {
            'metadata': {
                'title': title,
                'description': description,
                'word_count': len(content.split())
            },
            'context': {
                'keywords': context_keywords,
                'primary_topic': self._determine_primary_topic(context_keywords)
            },
            'content_analysis': {
                'keywords': keywords,
                'technical_terms': technical_analysis['technical_terms'],
                'domain_classification': domain_classification,
                'statistics': technical_analysis['statistics']
            },
            'key_phrases': self.keyword_extractor.extract_key_phrases(content),
            'technical_elements': self.technical_analyzer.extract_code_elements(content)
        }

    def _extract_context_keywords(self, title: str, description: str) -> List[Dict[str, float]]:
        """Extract keywords from title and description with higher relevance threshold"""
        # Combine title and description with title having more weight
        context_text = f"{title} {title} {description}"
        return self.keyword_extractor.extract_keywords(
            context_text,
            min_freq=1,  # Lower frequency requirement for context
            min_relevance=0.4  # Higher relevance threshold for context
        )

    def _extract_keywords_with_context(self, content: str, context_keywords: List[Dict[str, float]]) -> List[Dict[str, float]]:
        """Extract keywords from content, influenced by context keywords"""
        # Extract initial keywords
        keywords = self.keyword_extractor.extract_keywords(content)
        
        # Boost relevance of keywords that appear in context
        context_terms = {kw['keyword'].lower() for kw in context_keywords}
        for keyword in keywords:
            if keyword['keyword'].lower() in context_terms:
                keyword['relevance'] = min(1.0, keyword['relevance'] * 1.5)
        
        # Sort by updated relevance
        return sorted(keywords, key=lambda x: x['relevance'], reverse=True)

    def _determine_primary_topic(self, context_keywords: List[Dict[str, float]]) -> str:
        """Determine primary topic from context keywords"""
        if not context_keywords:
            return "unknown"
        return context_keywords[0]['keyword']

    def analyze_transcript(self, transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze transcript segments"""
        analyzed_segments = []
        
        for segment in transcript:
            text = segment.get('text', '')
            if not text:
                continue
            
            # Clean text
            text = self.text_cleaner.clean_text(text)
            
            # Analyze segment
            analysis = {
                'start_time': segment.get('start', 0),
                'end_time': segment.get('start', 0) + segment.get('duration', 0),
                'text': text,
                'keywords': self.keyword_extractor.extract_keywords(text, min_freq=1),
                'technical_terms': self.technical_analyzer.detect_technical_terms(text),
                'domain': self.technical_analyzer.classify_domain(text)
            }
            
            analyzed_segments.append(analysis)
        
        return {
            'segments': analyzed_segments,
            'statistics': self._calculate_transcript_statistics(analyzed_segments)
        }

    def _calculate_transcript_statistics(self, segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics across transcript segments"""
        if not segments:
            return {}
        
        total_keywords = sum(len(seg['keywords']) for seg in segments)
        total_terms = sum(len(seg['technical_terms']) for seg in segments)
        
        # Aggregate domain scores
        domain_scores = {}
        for segment in segments:
            for domain, score in segment['domain'].items():
                domain_scores[domain] = domain_scores.get(domain, 0) + score
        
        # Normalize domain scores
        total_segments = len(segments)
        domain_scores = {k: v/total_segments for k, v in domain_scores.items()}
        
        return {
            'total_segments': total_segments,
            'avg_keywords_per_segment': total_keywords / total_segments,
            'avg_technical_terms_per_segment': total_terms / total_segments,
            'domain_distribution': domain_scores,
            'primary_domain': max(domain_scores.items(), key=lambda x: x[1])[0]
        }

    def get_safe_filename(self, text: str, max_length: int = 200) -> str:
        """Generate a safe filename from text"""
        return self.text_cleaner.clean_filename(text, max_length)
