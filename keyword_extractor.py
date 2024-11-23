from typing import List, Dict, Tuple, Set, Any
from collections import Counter
import spacy
from knowledge_base import KnowledgeBase
from text_cleaner import TextCleaner

class KeywordExtractor:
    def __init__(self, knowledge_base: KnowledgeBase, text_cleaner: TextCleaner):
        self.nlp = spacy.load("en_core_web_lg")
        self.knowledge_base = knowledge_base
        self.text_cleaner = text_cleaner
        
        # Minimum word length for keywords
        self.min_word_length = 3
        # Minimum phrase length (in words) for compound terms
        self.min_phrase_length = 2
        # Maximum phrase length (in words) for compound terms
        self.max_phrase_length = 5

    def extract_keywords(self, text: str, min_freq: int = 2, min_relevance: float = 0.3) -> List[Dict[str, float]]:
        """Extract keywords with relevance scores"""
        # Clean text
        text = self.text_cleaner.clean_text(text)
        doc = self.nlp(text)
        
        # Extract candidate phrases
        candidates = self._extract_candidates(doc)
        
        # Count frequencies
        freq_dist = Counter(candidates)
        
        # Score candidates
        scored_keywords = []
        for candidate, freq in freq_dist.items():
            if freq >= min_freq:
                relevance = self._calculate_relevance(candidate, doc)
                if relevance >= min_relevance:
                    scored_keywords.append({
                        'keyword': candidate,
                        'relevance': relevance,
                        'frequency': freq
                    })
        
        # Sort by relevance
        return sorted(scored_keywords, key=lambda x: x['relevance'], reverse=True)

    def _extract_candidates(self, doc) -> List[str]:
        """Extract candidate keywords and phrases"""
        candidates = []
        
        # Add noun phrases
        for chunk in doc.noun_chunks:
            if self._is_valid_phrase(chunk):
                clean_phrase = self.text_cleaner.clean_text(chunk.text)
                candidates.append(clean_phrase)
        
        # Add named entities
        for ent in doc.ents:
            if self._is_valid_entity(ent):
                clean_ent = self.text_cleaner.clean_text(ent.text)
                candidates.append(clean_ent)
        
        # Add technical terms
        candidates.extend(self._extract_technical_terms(doc))
        
        return candidates

    def _is_valid_phrase(self, chunk) -> bool:
        """Check if noun phrase is valid"""
        # Must contain at least one meaningful word
        has_meaningful_word = any(
            token.pos_ in ['NOUN', 'PROPN'] and 
            not token.is_stop and 
            len(token.text) >= self.min_word_length
            for token in chunk
        )
        
        # Check length constraints
        word_count = len(chunk.text.split())
        valid_length = self.min_phrase_length <= word_count <= self.max_phrase_length
        
        return has_meaningful_word and valid_length

    def _is_valid_entity(self, ent) -> bool:
        """Check if named entity is valid"""
        valid_labels = {'ORG', 'PRODUCT', 'GPE', 'TECH', 'EVENT'}
        return (
            ent.label_ in valid_labels and
            len(ent.text) >= self.min_word_length and
            not self.knowledge_base.is_common_word(ent.text)
        )

    def _extract_technical_terms(self, doc) -> List[str]:
        """Extract technical terms from text"""
        technical_terms = []
        
        # Add known technical phrases
        text = doc.text.lower()
        for phrase in self.knowledge_base.technical_phrases:
            if phrase in text:
                technical_terms.append(phrase)
        
        # Add terms with technical indicators
        for token in doc:
            if (len(token.text) >= self.min_word_length and
                not token.is_stop and
                self.knowledge_base.is_technical_indicator(token.text)):
                technical_terms.append(token.text.lower())
        
        return technical_terms

    def _calculate_relevance(self, term: str, doc) -> float:
        """Calculate relevance score for a term"""
        # Base score
        score = 0.0
        term = term.lower()
        
        # Known technical phrase bonus
        if self.knowledge_base.is_technical_phrase(term):
            score += 0.5
        
        # Technical indicator bonus
        if any(self.knowledge_base.is_technical_indicator(word) 
               for word in term.split()):
            score += 0.3
        
        # Organization bonus
        if self.knowledge_base.is_organization(term):
            score += 0.2
        
        # Multi-word bonus
        if len(term.split()) > 1:
            score += 0.2
        
        # Named entity bonus
        if any(ent.text.lower() == term for ent in doc.ents):
            score += 0.2
        
        # Vector similarity if available
        term_doc = self.nlp(term)
        if term_doc.has_vector and doc.has_vector:
            score += term_doc.similarity(doc) * 0.3
        
        return min(score, 1.0)  # Cap at 1.0

    def extract_key_phrases(self, text: str, top_n: int = 10) -> List[Dict[str, Any]]:
        """Extract key phrases with context"""
        doc = self.nlp(text)
        phrases = []
        
        for sent in doc.sents:
            # Skip short sentences
            if len(sent.text.split()) < 3:
                continue
            
            # Look for sentences containing technical terms
            tech_terms = set()
            for token in sent:
                if self.knowledge_base.is_technical_indicator(token.text):
                    tech_terms.add(token.text.lower())
            
            if tech_terms:
                phrases.append({
                    'text': sent.text,
                    'technical_terms': list(tech_terms),
                    'relevance': len(tech_terms) / len(sent.text.split())
                })
        
        # Sort by relevance and return top N
        return sorted(phrases, key=lambda x: x['relevance'], reverse=True)[:top_n]

    def extract_context(self, keyword: str, text: str, window_size: int = 50) -> List[str]:
        """Extract context windows around keyword occurrences"""
        text = self.text_cleaner.clean_text(text)
        keyword = keyword.lower()
        
        contexts = []
        start = 0
        while True:
            # Find next occurrence
            pos = text.find(keyword, start)
            if pos == -1:
                break
                
            # Extract context window
            context_start = max(0, pos - window_size)
            context_end = min(len(text), pos + len(keyword) + window_size)
            context = text[context_start:context_end]
            
            contexts.append(context)
            start = pos + 1
            
        return contexts

    def get_keyword_statistics(self, keywords: List[Dict[str, float]]) -> Dict[str, Any]:
        """Calculate statistics about extracted keywords"""
        return {
            'total_keywords': len(keywords),
            'avg_relevance': sum(k['relevance'] for k in keywords) / len(keywords) if keywords else 0,
            'avg_frequency': sum(k['frequency'] for k in keywords) / len(keywords) if keywords else 0,
            'technical_term_ratio': sum(1 for k in keywords 
                                     if self.knowledge_base.is_technical_indicator(k['keyword'])) / len(keywords)
                                     if keywords else 0
        }
