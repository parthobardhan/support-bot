# Adobe Support Bot - RAG Application

A comprehensive customer support RAG (Retrieval-Augmented Generation) application that uses MongoDB Atlas, MongoDB Atlas Search, and Vector Search to help support associates access mock Jira tickets, knowledge articles, and public documentation for Adobe products.

## 🚀 Features

- **AI-Powered Search**: Semantic search using Voyage AI embeddings
- **Hybrid Search**: Combines vector search and traditional text search
- **Rich Content**: 1000+ mock documents including Jira tickets, documentation, and knowledge articles
- **Advanced Filtering**: Filter by content type, Adobe product, priority, and more
- **Similar Documents**: Find related content using vector similarity
- **Real-time Stats**: Monitor collection statistics and performance
- **Responsive UI**: Modern Bootstrap-based interface

## 🛠 Technology Stack

- **Backend**: Flask (Python)
- **Database**: MongoDB Atlas
- **Search**: MongoDB Atlas Vector Search & Atlas Search
- **Embeddings**: Voyage AI (voyage-3-large model)
- **Frontend**: HTML5, Bootstrap 5, JavaScript
- **Data Processing**: Python with chunking and embedding generation

## 📋 Prerequisites

- Python 3.8 or higher
- MongoDB Atlas account with cluster access
- Voyage AI API access

## 🔧 Setup Instructions

### 1. Environment Configuration

**IMPORTANT**: This application uses environment variables for secure configuration. You must set up your environment variables before running the application.

```bash
# Copy the environment template
cp env.template .env

# Edit .env file and add your actual credentials
# Required variables:
# - MONGODB_URI: Your MongoDB Atlas connection string
# - ATLAS_PUBLIC_KEY: MongoDB Atlas API public key
# - ATLAS_PRIVATE_KEY: MongoDB Atlas API private key
# - VOYAGE_API_KEY: Your Voyage AI API key
```

**Where to get the required credentials:**
- **MongoDB Atlas URI**: From your Atlas cluster's "Connect" button
- **Atlas API Keys**: From Atlas → Organization Settings → API Keys → Create API Key
- **Voyage AI Key**: From your [Voyage AI account](https://www.voyageai.com/)

### 2. Clone and Setup

```bash
# Navigate to your project directory
cd /Users/partho/Documents/demos/support-bot

# Run the automated setup
chmod +x setup.sh
./setup.sh
```

### 3. Create Vector Search Index

You can create the vector search index using the provided script:

```bash
# Run the Atlas index creation script
python create_atlas_index.py
```

Alternatively, create it manually:
1. Go to your MongoDB Atlas dashboard
2. Navigate to your cluster
3. Click on the "Search" tab
4. Click "Create Index"
5. Use "vector_index" as the index name and configure for the "embeddings" field

### 4. Start the Application

```bash
# Start the backend server
./start_backend.sh

# Open frontend/index.html in your browser
```

## 🗂 Project Structure

```
support-bot/
├── backend/
│   ├── app.py                 # Flask application
│   ├── config.py             # Configuration settings
│   ├── database.py           # MongoDB operations
│   ├── embeddings_service.py # Voyage AI integration
│   └── requirements.txt      # Python dependencies
├── data_generation/
│   ├── mock_data_generator.py # Generate mock data
│   └── data_processor.py     # Process and chunk data
├── frontend/
│   ├── index.html           # Main UI
│   └── app.js              # Frontend JavaScript
├── scripts/
│   ├── setup_database.py    # Database setup script
│   └── create_vector_index.json # Vector index configuration
├── setup.sh                # Main setup script
├── start_backend.sh        # Backend startup script
└── README.md              # This file
```

## 🔍 Search Types

1. **Hybrid Search** (Recommended): Combines AI semantic search with traditional text search
2. **AI Semantic Search**: Uses vector embeddings for meaning-based search
3. **Text Search**: Traditional keyword-based search

## 📊 Mock Data

The application generates 1000 mock documents:
- **~333 Jira Tickets**: Bug reports, feature requests, and tasks
- **~333 Documentation**: API references, user guides, installation guides
- **~334 Knowledge Articles**: How-tos, FAQs, troubleshooting guides

All data covers popular Adobe products including:
- Adobe Photoshop, Illustrator, InDesign
- Adobe Premiere Pro, After Effects, Lightroom
- Adobe XD, Acrobat, Creative Cloud
- Adobe Experience Manager, Analytics, Target

## 🔧 API Endpoints

- `GET /health` - Health check
- `POST /api/search` - Main search endpoint
- `GET /api/document/{id}` - Get document details
- `GET /api/similar/{id}` - Find similar documents
- `GET /api/filters` - Get filter options
- `GET /api/stats` - Collection statistics

## 📝 Example Queries

Try these sample searches:
- "Adobe Photoshop crashes when opening large files"
- "How to integrate Creative Cloud API"
- "Performance optimization tips"
- "Installation troubleshooting"

## 🎯 Key Features

### Advanced Search Capabilities
- Semantic understanding of queries
- Real-time results with relevance scoring
- Support for complex filtering

### Rich Document Management
- Automatic text chunking for large documents
- Embedding generation with Voyage AI
- Metadata-rich search results

### User-Friendly Interface
- Intuitive search interface
- Detailed document viewer
- Similar document discovery
- Real-time statistics

## 🔒 Configuration

Key configuration in `backend/config.py`:
- MongoDB Atlas connection string
- Voyage AI API key
- Search parameters and limits
- Index names and settings

## 🚨 Troubleshooting

1. **Connection Issues**: Verify MongoDB Atlas connection string and IP whitelist
2. **Embedding Errors**: Check Voyage AI API key and rate limits
3. **Search Not Working**: Ensure vector search index is created in MongoDB Atlas
4. **No Results**: Verify data was loaded successfully using the stats endpoint

## 📈 Performance Notes

- Vector search index required for semantic search
- Embeddings generated using voyage-3-large (1024 dimensions)
- Chunking optimized for 1000 characters with 200 character overlap
- Results cached for improved performance

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section
2. Verify all prerequisites are met
3. Review the setup logs for errors
4. Ensure all API keys and connections are valid

## 📄 License

This is a demo application for educational and testing purposes.

---

**Built with ❤️ for Adobe Support Teams**
