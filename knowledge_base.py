import json
from typing import Set, Dict, List

class KnowledgeBase:
    def __init__(self, file_path: str = 'knowledge_base.json'):
        self.file_path = file_path
        self.technical_indicators: Set[str] = set()
        self.technical_phrases: Set[str] = set()
        self.organizations: Set[str] = set()
        self.locations: Set[str] = set()
        self.common_words: Set[str] = set()
        self.load()

    def load(self):
        """Load knowledge base from JSON file"""
        try:
            with open(self.file_path, 'r') as f:
                kb = json.load(f)
                self.technical_indicators = set(kb['technical_indicators'])
                self.technical_phrases = set(kb['technical_phrases'])
                self.organizations = set(kb.get('organizations', []))
                self.locations = set(kb.get('locations', []))
                self.common_words = set(kb['common_words'])
        except FileNotFoundError:
            print(f"Warning: Knowledge base file {self.file_path} not found. Using empty sets.")

    def save(self):
        """Save knowledge base to JSON file"""
        kb = {
            'technical_indicators': sorted(list(self.technical_indicators)),
            'technical_phrases': sorted(list(self.technical_phrases)),
            'organizations': sorted(list(self.organizations)),
            'locations': sorted(list(self.locations)),
            'common_words': sorted(list(self.common_words))
        }
        with open(self.file_path, 'w') as f:
            json.dump(kb, f, indent=2)

    def add_technical_indicator(self, term: str):
        """Add a new technical indicator"""
        self.technical_indicators.add(term.lower())

    def add_technical_phrase(self, phrase: str):
        """Add a new technical phrase"""
        self.technical_phrases.add(phrase.lower())

    def add_organization(self, org: str):
        """Add a new organization"""
        self.organizations.add(org.lower())

    def add_location(self, loc: str):
        """Add a new location"""
        self.locations.add(loc.lower())

    def is_technical_indicator(self, term: str) -> bool:
        """Check if term is a known technical indicator"""
        return term.lower() in self.technical_indicators

    def is_technical_phrase(self, phrase: str) -> bool:
        """Check if phrase is a known technical phrase"""
        return phrase.lower() in self.technical_phrases

    def is_organization(self, term: str) -> bool:
        """Check if term is a known organization"""
        return term.lower() in self.organizations

    def is_location(self, term: str) -> bool:
        """Check if term is a known location"""
        return term.lower() in self.locations

    def is_common_word(self, word: str) -> bool:
        """Check if word is a common word"""
        return word.lower() in self.common_words

    def get_all_technical_terms(self) -> Set[str]:
        """Get all technical terms (indicators and phrases)"""
        return self.technical_indicators.union(self.technical_phrases)

    def update_from_text(self, text: str, new_terms: Dict[str, List[str]]):
        """Update knowledge base with new terms from text"""
        for term in new_terms.get('technical_indicators', []):
            self.add_technical_indicator(term)
        
        for phrase in new_terms.get('technical_phrases', []):
            self.add_technical_phrase(phrase)
        
        for org in new_terms.get('organizations', []):
            self.add_organization(org)
        
        for loc in new_terms.get('locations', []):
            self.add_location(loc)
        
        self.save()
