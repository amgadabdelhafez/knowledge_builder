import spacy
import re
from transformers import pipeline
from typing import List, Set

class TextProcessor:
    def __init__(self):
        # Initialize NLP components
        self.nlp = spacy.load("en_core_web_lg")
        
        # Initialize zero-shot classifier for technical content
        self.classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )
        
        # Domain-specific keywords
        self.domain_keywords = {
            'programming': {
                'def', 'class', 'function', 'return', 'import', 'variable',
                'method', 'parameter', 'argument', 'loop', 'condition',
                'exception', 'module', 'package', 'library'
            },
            'machine_learning': {
                'neural', 'network', 'layer', 'training', 'model', 'activation',
                'neuron', 'weights', 'bias', 'gradient', 'epoch', 'batch',
                'learning rate', 'relu', 'softmax', 'classification'
            },
            'database_systems': {
                'database', 'schema', 'table', 'query', 'index', 'primary key',
                'foreign key', 'join', 'select', 'insert', 'update', 'delete',
                'transaction', 'constraint', 'column', 'row'
            },
            'networking': {
                'protocol', 'tcp', 'ip', 'http', 'router', 'packet',
                'network', 'bandwidth', 'latency', 'dns', 'server',
                'client', 'socket', 'port', 'firewall'
            }
        }

    def extract_keywords(self, text: str) -> List[str]:
        """Extract technical keywords and phrases from text"""
        doc = self.nlp(text)
        keywords = set()
        
        # Extract noun phrases as compound terms
        for chunk in doc.noun_chunks:
            if any(token.pos_ in ['NOUN', 'PROPN'] for token in chunk):
                # Add both the full noun phrase and individual nouns
                keywords.add(chunk.text.lower())
                # Also add individual words for flexibility
                for token in chunk:
                    if token.pos_ in ['NOUN', 'PROPN']:
                        keywords.add(token.text.lower())
        
        # Add named entities
        for ent in doc.ents:
            keywords.add(ent.text.lower())
            # Also add individual words from multi-word entities
            if len(ent.text.split()) > 1:
                keywords.update(word.lower() for word in ent.text.split())
        
        # Filter out short keywords and sort
        return sorted([k for k in keywords if len(k) > 2])

    def detect_technical_terms(self, text: str) -> List[str]:
        """Detect domain-specific technical terms"""
        doc = self.nlp(text)
        technical_terms = set()
        
        # Custom patterns for technical terms
        patterns = [
            r'\b[A-Z]+[a-z]*[A-Z][a-z]*\b',  # CamelCase
            r'\b[a-z]+_[a-z]+\b',            # snake_case
            r'\b[A-Z][A-Z0-9_]+\b',          # CONSTANT_CASE
            r'\b\d+\.\d+\.\d+\b',            # Versions
            r'\b[a-zA-Z]+://[^\s]*\b',       # URLs
            r'\b[A-Za-z]+\([^)]*\)\b'        # Function calls
        ]
        
        # Find pattern matches
        for pattern in patterns:
            technical_terms.update(re.findall(pattern, text))
        
        # Add named entities that look like technical terms
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'GPE']:
                technical_terms.add(ent.text)
        
        # Add tokens that look like technical terms
        for token in doc:
            if token.text.isupper() and len(token.text) >= 2:
                technical_terms.add(token.text)
        
        return sorted(list(technical_terms))

    def classify_domain(self, text: str) -> str:
        """Classify text into technical domains"""
        # Count domain-specific keywords
        text = text.lower()
        domain_scores = {}
        
        for domain, keywords in self.domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword.lower() in text)
            domain_scores[domain] = score
        
        # Use zero-shot classification as backup
        if max(domain_scores.values(), default=0) == 0:
            result = self.classifier(
                text,
                candidate_labels=list(self.domain_keywords.keys()),
                multi_label=False
            )
            return result['labels'][0]
        
        # Return domain with highest keyword match
        return max(domain_scores.items(), key=lambda x: x[1])[0]

    def get_text_statistics(self, text: str) -> dict:
        """Get statistical information about the text"""
        doc = self.nlp(text)
        
        return {
            'word_count': len([token for token in doc if not token.is_punct]),
            'sentence_count': len(list(doc.sents)),
            'technical_term_count': len(self.detect_technical_terms(text)),
            'keyword_count': len(self.extract_keywords(text)),
            'named_entity_count': len(doc.ents)
        }

    def get_safe_filename(self, text: str, max_length: int = 200) -> str:
        """Generate a safe filename from text"""
        # Remove invalid filename characters
        safe = re.sub(r'[<>:"/\\|?*]', '', text)
        # Replace spaces with underscores
        safe = safe.replace(' ', '_')
        # Truncate if too long
        return safe[:max_length]
