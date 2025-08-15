"""
Requirements parser module for extracting testable requirements from natural language text.
"""

import re
from typing import List, Dict


class RequirementsParser:
    """Parser to extract testable requirements from natural language text"""
    
    def __init__(self):
        # Keywords that typically indicate requirements
        self.requirement_keywords = [
            'should', 'must', 'shall', 'will', 'needs to', 'required to',
            'has to', 'ought to', 'is required', 'is expected', 'validates',
            'ensures', 'verifies', 'checks', 'prevents', 'allows', 'enables'
        ]
    
    def extract_requirements(self, text: str) -> List[Dict[str, str]]:
        """Extract requirements from natural language text"""
        requirements = []
        sentences = re.split(r'[.!?]+', text)
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Check if sentence contains requirement keywords
            if any(keyword in sentence.lower() for keyword in self.requirement_keywords):
                # Clean up the sentence
                clean_sentence = self._clean_requirement(sentence)
                if clean_sentence:
                    requirements.append({
                        'id': f'REQ_{i+1:03d}',
                        'text': clean_sentence,
                        'category': self._categorize_requirement(clean_sentence),
                        'checked': False
                    })
        
        return requirements
    
    def _clean_requirement(self, sentence: str) -> str:
        """Clean and format requirement sentence"""
        # Remove extra whitespace
        sentence = ' '.join(sentence.split())
        
        # Ensure sentence starts with capital letter
        if sentence:
            sentence = sentence[0].upper() + sentence[1:]
        
        # Ensure sentence ends with period
        if sentence and not sentence.endswith('.'):
            sentence += '.'
        
        return sentence
    
    def _categorize_requirement(self, sentence: str) -> str:
        """Categorize requirement based on content"""
        sentence_lower = sentence.lower()
        
        if any(word in sentence_lower for word in ['validate', 'check', 'verify', 'ensure']):
            return 'Validation'
        elif any(word in sentence_lower for word in ['input', 'enter', 'provide']):
            return 'Input'
        elif any(word in sentence_lower for word in ['output', 'display', 'show', 'return']):
            return 'Output'
        elif any(word in sentence_lower for word in ['security', 'authenticate', 'authorize']):
            return 'Security'
        elif any(word in sentence_lower for word in ['performance', 'speed', 'fast', 'time']):
            return 'Performance'
        else:
            return 'Functional' 