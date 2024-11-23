from typing import List, Dict, Set, Any
import re
from transformers import pipeline
from knowledge_base import KnowledgeBase
from text_cleaner import TextCleaner

class TechnicalAnalyzer:
    def __init__(self, knowledge_base: KnowledgeBase, text_cleaner: TextCleaner):
        self.knowledge_base = knowledge_base
        self.text_cleaner = text_cleaner
        
        # Initialize zero-shot classifier for domain classification
        self.classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )
        
        # Technical patterns
        self.patterns = {
            'file_extension': r'\b[A-Z][A-Za-z0-9]+(\.js|\.py|\.java)\b',
            'acronym': r'\b[A-Z][A-Z0-9]{2,}\b',
            'version': r'\b\d+\.\d+\.\d+\b',
            'camel_case': r'\b[a-z]+[A-Z][a-zA-Z]*\b'
        }
        
        # Domain definitions
        self.domains = {
            'cloud_infrastructure': {
                'cloud', 'kubernetes', 'docker', 'container', 'instance', 'compute',
                'storage', 'network', 'vpc', 'server', 'cluster', 'scaling'
            },
            'data_analytics': {
                'analytics', 'bigquery', 'warehouse', 'database', 'sql', 'query',
                'etl', 'pipeline', 'processing', 'visualization', 'metrics'
            },
            'machine_learning': {
                'model', 'training', 'inference', 'neural', 'gpu', 'tensor',
                'dataset', 'prediction', 'classification', 'learning'
            },
            'development_tools': {
                'git', 'ci/cd', 'testing', 'monitoring', 'logging', 'deployment',
                'version', 'repository', 'code', 'build', 'release'
            }
        }

    def detect_technical_terms(self, text: str) -> List[Dict[str, Any]]:
        """Detect technical terms with metadata"""
        # Clean text
        text = self.text_cleaner.clean_text(text, keep_case=True)  # Keep case for pattern matching
        
        technical_terms = []
        
        # Find pattern matches
        for pattern_name, pattern in self.patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                term = match.group()
                if self._validate_technical_term(term):
                    technical_terms.append({
                        'term': term,
                        'type': pattern_name,
                        'context': self._get_context(text, match.start(), match.end())
                    })
        
        # Add known technical terms
        text_lower = text.lower()
        for term in self.knowledge_base.get_all_technical_terms():
            if term in text_lower:
                technical_terms.append({
                    'term': term,
                    'type': 'known_term',
                    'context': self._get_context(text_lower, text_lower.find(term), 
                                              text_lower.find(term) + len(term))
                })
        
        return technical_terms

    def _validate_technical_term(self, term: str) -> bool:
        """Validate if a term is truly technical"""
        term_lower = term.lower()
        
        # Skip common words and short terms
        if len(term) < 3 or self.knowledge_base.is_common_word(term_lower):
            return False
        
        # Check if it's a known technical term
        if (self.knowledge_base.is_technical_indicator(term_lower) or 
            self.knowledge_base.is_technical_phrase(term_lower)):
            return True
        
        return True  # If it matches a pattern and isn't common, consider it technical

    def _get_context(self, text: str, start: int, end: int, window: int = 50) -> str:
        """Get context window around a term"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end]

    def classify_domain(self, text: str) -> Dict[str, float]:
        """Classify text into technical domains with confidence scores"""
        text = self.text_cleaner.clean_text(text)
        
        # Score each domain based on keyword presence
        scores = {}
        for domain, indicators in self.domains.items():
            score = sum(2 if indicator in text else 0 for indicator in indicators)
            scores[domain] = score
        
        # Normalize scores
        max_score = max(scores.values()) if scores else 0
        if max_score > 0:
            scores = {k: v/max_score for k, v in scores.items()}
        
        # Use classifier as backup for low-confidence cases
        if max_score == 0:
            result = self.classifier(
                text,
                candidate_labels=list(self.domains.keys()),
                multi_label=True
            )
            scores = dict(zip(result['labels'], result['scores']))
        
        return scores

    def analyze_technical_content(self, text: str) -> Dict[str, Any]:
        """Perform comprehensive technical analysis"""
        # Clean text
        text = self.text_cleaner.clean_text(text)
        
        # Detect technical terms
        technical_terms = self.detect_technical_terms(text)
        
        # Classify domains
        domain_scores = self.classify_domain(text)
        
        # Group terms by type
        terms_by_type = {}
        for term in technical_terms:
            term_type = term['type']
            if term_type not in terms_by_type:
                terms_by_type[term_type] = []
            terms_by_type[term_type].append(term)
        
        # Calculate statistics
        total_terms = len(technical_terms)
        word_count = len(text.split())
        
        return {
            'technical_terms': technical_terms,
            'terms_by_type': terms_by_type,
            'domain_classification': domain_scores,
            'statistics': {
                'total_terms': total_terms,
                'unique_terms': len(set(t['term'].lower() for t in technical_terms)),
                'technical_density': total_terms / word_count if word_count > 0 else 0,
                'primary_domain': max(domain_scores.items(), key=lambda x: x[1])[0]
            }
        }

    def extract_code_elements(self, text: str) -> Dict[str, List[str]]:
        """Extract code-related elements"""
        # Clean text while preserving case
        text = self.text_cleaner.clean_text(text, keep_case=True)
        
        elements = {
            'functions': re.findall(r'\b\w+\s*\([^)]*\)', text),
            'variables': re.findall(r'\b[a-z_]\w*\b', text),
            'classes': re.findall(r'\b[A-Z]\w*\b', text),
            'imports': re.findall(r'(?:import|from)\s+[\w.]+', text),
            'urls': re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', text)
        }
        
        # Clean and filter elements
        for key in elements:
            elements[key] = [
                e for e in set(elements[key])  # Remove duplicates
                if len(e) > 2 and not self.knowledge_base.is_common_word(e.lower())
            ]
        
        return elements

    def analyze_code_complexity(self, text: str) -> Dict[str, Any]:
        """Analyze complexity of technical/code content"""
        # Clean text
        text = self.text_cleaner.clean_text(text)
        
        # Count various complexity indicators
        analysis = {
            'line_count': len(text.splitlines()),
            'word_count': len(text.split()),
            'technical_term_count': len(self.detect_technical_terms(text)),
            'nested_structures': len(re.findall(r'[{(\[]', text)),
            'conditional_statements': len(re.findall(r'\b(if|else|switch|case)\b', text)),
            'loops': len(re.findall(r'\b(for|while|do)\b', text)),
            'function_calls': len(re.findall(r'\b\w+\(', text))
        }
        
        # Calculate complexity score (simple heuristic)
        analysis['complexity_score'] = (
            analysis['nested_structures'] * 0.2 +
            analysis['conditional_statements'] * 0.3 +
            analysis['loops'] * 0.3 +
            analysis['function_calls'] * 0.2
        ) / analysis['line_count'] if analysis['line_count'] > 0 else 0
        
        return analysis
