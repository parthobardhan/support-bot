#!/bin/bash

echo "🚀 Setting up Adobe Support Bot RAG Application..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📋 Installing Python dependencies..."
pip install -r backend/requirements.txt

# Test connections
echo "🧪 Testing API connections..."

python3 -c "
import sys
sys.path.append('backend')
from config import Config
from embeddings_service import EmbeddingsService

try:
    Config.validate_config()
    embeddings = EmbeddingsService()
    if embeddings.test_connection():
        print('✅ Voyage AI connection successful')
    else:
        print('❌ Voyage AI connection failed')
        exit(1)
except Exception as e:
    print(f'❌ Configuration error: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Setup failed. Please check your API keys and configuration."
    exit 1
fi

# Run database setup
echo "💾 Setting up database and generating mock data..."
python3 scripts/setup_database.py

if [ $? -ne 0 ]; then
    echo "❌ Database setup failed."
    exit 1
fi

# Make scripts executable
chmod +x start_backend.sh

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Create a Vector Search index in MongoDB Atlas:"
echo "   - Go to your cluster in MongoDB Atlas"
echo "   - Click 'Search' tab"
echo "   - Create index using scripts/create_vector_index.json"
echo ""
echo "2. Start the backend server:"
echo "   ./start_backend.sh"
echo ""
echo "3. Open frontend/index.html in your browser"
echo ""
echo "🎉 Your Adobe Support Bot is ready!"
