#!/usr/bin/env python3
import spacy

print("Testing spaCy model...")
try:
    nlp = spacy.load('en_core_web_sm')
    print("✅ spaCy model loaded successfully!")
    
    # Test basic functionality
    text = "NASA is developing space technology for future missions."
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    print(f"Found entities: {entities}")
    
except Exception as e:
    print(f"❌ spaCy error: {e}")
