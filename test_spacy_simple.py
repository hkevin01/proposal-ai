#!/usr/bin/env python3
"""Simple test for spaCy model"""

try:
    import spacy
    print("✅ spaCy imported successfully")
    
    try:
        nlp = spacy.load('en_core_web_sm')
        print("✅ spaCy model loaded successfully")
        
        # Test basic functionality
        doc = nlp("NASA is developing space technology.")
        print(f"✅ NLP processing works: {[(ent.text, ent.label_) for ent in doc.ents]}")
        
    except OSError as e:
        print(f"❌ spaCy model not found: {e}")
        print("Running spaCy download...")
        import subprocess
        result = subprocess.run(['python', '-m', 'spacy', 'download', 'en_core_web_sm'], 
                              capture_output=True, text=True)
        print(f"Download result: {result.returncode}")
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            
except ImportError as e:
    print(f"❌ spaCy not installed: {e}")
