#!/bin/bash

# Proposal AI Runner Script
# This script sets up the environment and runs the application

echo "🚀 Starting Proposal AI..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Download spaCy model if not exists
echo "🧠 Checking spaCy language model..."
if ! python -c "import spacy; spacy.load('en_core_web_sm')" 2>/dev/null; then
    echo "📥 Downloading spaCy language model..."
    python -m spacy download en_core_web_sm
    
    # Verify the download worked
    if ! python -c "import spacy; spacy.load('en_core_web_sm')" 2>/dev/null; then
        echo "⚠️ spaCy model download failed. Trying alternative method..."
        pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
        
        # Final verification
        if ! python -c "import spacy; spacy.load('en_core_web_sm')" 2>/dev/null; then
            echo "❌ Failed to install spaCy model automatically."
            echo "Please run one of these commands manually:"
            echo "   python -m spacy download en_core_web_sm"
            echo "   OR"
            echo "   pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl"
            echo ""
            echo "Press Enter to continue (app may have limited NLP functionality)..."
            read
        else
            echo "✅ spaCy model successfully installed!"
        fi
    else
        echo "✅ spaCy model successfully installed!"
    fi
else
    echo "✅ spaCy model already available"
fi

# Create database if not exists
echo "🗄️ Setting up database..."
cd src
python -c "from database import setup_database; setup_database()"

# Create sample data if database is empty
echo "📋 Adding sample data..."
python sample_data.py

# Run the main application
echo "✨ Launching Proposal AI GUI..."
python main.py

echo "👋 Proposal AI closed."
