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
if ! python -c "import spacy; spacy.load('en_core_web_sm')" 2>/dev/null; then
    echo "🧠 Downloading spaCy language model..."
    python -m spacy download en_core_web_sm
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
