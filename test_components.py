#!/usr/bin/env python3
"""
Test script for spaCy model installation and TfidfVectorizer
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_spacy():
    """Test spaCy model installation"""
    try:
        import spacy
        nlp = spacy.load('en_core_web_sm')
        doc = nlp("This is a test sentence with NASA and space technology.")
        print("✅ spaCy model loaded successfully!")
        print(f"   Found entities: {[(ent.text, ent.label_) for ent in doc.ents]}")
        return True
    except Exception as e:
        print(f"❌ spaCy model failed: {e}")
        return False

def test_tfidf():
    """Test TfidfVectorizer matrix operations"""
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        
        vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        texts = ["NASA space mission", "ESA satellite project", "space technology innovation"]
        
        # Test the matrix operations
        tfidf_matrix = vectorizer.fit_transform(texts)
        
        # Safe way to access matrix elements
        similarity1 = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2]).flatten()[0]
        similarity2 = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1:]).flatten()[0]
        
        print(f"✅ TfidfVectorizer working! Similarities: {similarity1:.3f}, {similarity2:.3f}")
        return True
    except Exception as e:
        print(f"❌ TfidfVectorizer failed: {e}")
        return False

def test_discovery_engine():
    """Test discovery engine initialization"""
    try:
        from enhanced_discovery_engine import EnhancedOpportunityDiscoverer
        discoverer = EnhancedOpportunityDiscoverer()
        
        print("✅ Discovery engine initialized successfully!")
        print(f"   spaCy available: {discoverer.nlp is not None}")
        print(f"   Sources count: {len(discoverer.opportunity_sources)}")
        return True
    except Exception as e:
        print(f"❌ Discovery engine failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Proposal AI components...")
    print("=" * 50)
    
    spacy_ok = test_spacy()
    tfidf_ok = test_tfidf()
    discovery_ok = test_discovery_engine()
    
    print("=" * 50)
    if all([spacy_ok, tfidf_ok, discovery_ok]):
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("⚠️ Some tests failed. Check the output above.")
        sys.exit(1)
