#!/bin/bash

echo "🚀 Starting Adobe Support Bot Backend..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📋 Installing dependencies..."
pip install -r backend/requirements.txt

# Check if MongoDB is accessible
echo "🔍 Testing MongoDB connection..."
python3 -c "
import sys
sys.path.append('backend')
from config import Config
from database import DatabaseManager
try:
    Config.validate_config()
    db = DatabaseManager()
    print('✅ MongoDB connection successful')
except Exception as e:
    print(f'❌ MongoDB connection failed: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Please ensure MongoDB Atlas is accessible and credentials are correct."
    exit 1
fi

# Start the backend server
echo "🌟 Starting Flask backend server..."
cd backend
export FLASK_ENV=development
python3 app.py
