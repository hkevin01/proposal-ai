#!/usr/bin/env python3
"""
Quick test that writes results to a file to avoid terminal issues
"""
import datetime
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    results = []
    results.append(f"Test started at: {datetime.datetime.now()}")
    
    # Test spaCy
    try:
        import spacy
        nlp = spacy.load('en_core_web_sm')
        results.append("✅ spaCy model loaded successfully")
        
        # Test NLP
        doc = nlp("NASA space technology")
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        results.append(f"Found entities: {entities}")
        
    except Exception as e:
        results.append(f"❌ spaCy failed: {e}")
    
    # Test discovery engine
    try:
        from enhanced_discovery_engine import EnhancedOpportunityDiscoverer
        discoverer = EnhancedOpportunityDiscoverer()
        results.append(f"✅ Discovery engine loaded (spaCy available: {discoverer.nlp is not None})")
    except Exception as e:
        results.append(f"❌ Discovery engine failed: {e}")
    
    # Write results to file
    with open('test_results.txt', 'w') as f:
        for result in results:
            f.write(result + '\n')
            print(result)  # Also try to print
    
    print("Results written to test_results.txt")

if __name__ == "__main__":
    main()
