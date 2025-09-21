from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from typing import Dict, Any, List
from datetime import datetime

from config import Config
from database import DatabaseManager
from embeddings_service import EmbeddingsService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize services
try:
    Config.validate_config()
    db_manager = DatabaseManager()
    embeddings_service = EmbeddingsService()
    logger.info("✅ All services initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize services: {e}")
    exit(1)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": "connected",
            "embeddings": "available"
        }
    })

@app.route('/api/search', methods=['POST'])
def search():
    """Main search endpoint supporting multiple search types"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        search_type = data.get('type', 'hybrid')  # vector, text, or hybrid
        limit = min(data.get('limit', 10), 50)  # Max 50 results
        filters = data.get('filters', {})
        
        if not query:
            return jsonify({"error": "Query parameter is required"}), 400
        
        results = []
        
        if search_type == 'vector':
            # Generate embedding for query
            query_embedding = embeddings_service.get_single_embedding(query)
            results = db_manager.vector_search(query_embedding, limit, filters)
            
        elif search_type == 'text':
            results = db_manager.text_search(query, limit, filters)
            
        else:  # hybrid search
            query_embedding = embeddings_service.get_single_embedding(query)
            results = db_manager.hybrid_search(query, query_embedding, limit, filters)
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_result = {
                "id": str(result.get('_id', '')),
                "title": result.get('title', ''),
                "content": result.get('content', '')[:500] + '...' if len(result.get('content', '')) > 500 else result.get('content', ''),
                "type": result.get('type', ''),
                "summary": result.get('summary', ''),
                "score": result.get('score', 0),
                "metadata": {
                    "product": result.get('product', ''),
                    "category": result.get('category', ''),
                    "priority": result.get('priority', ''),
                    "status": result.get('status', ''),
                    "created_date": result.get('created_date', ''),
                    "tags": result.get('tags', [])
                }
            }
            formatted_results.append(formatted_result)
        
        return jsonify({
            "results": formatted_results,
            "total": len(formatted_results),
            "query": query,
            "search_type": search_type,
            "filters_applied": filters
        })
        
    except Exception as e:
        logger.error(f"❌ Search error: {e}")
        return jsonify({"error": "Internal search error"}), 500

@app.route('/api/document/<doc_id>', methods=['GET'])
def get_document(doc_id):
    """Get full document by ID"""
    try:
        document = db_manager.collection.find_one({"_id": doc_id})
        
        if not document:
            return jsonify({"error": "Document not found"}), 404
        
        # Remove embeddings from response for performance
        if 'embeddings' in document:
            del document['embeddings']
        
        # Convert ObjectId to string if present
        document['_id'] = str(document['_id'])
        
        return jsonify(document)
        
    except Exception as e:
        logger.error(f"❌ Error fetching document {doc_id}: {e}")
        return jsonify({"error": "Failed to fetch document"}), 500

@app.route('/api/filters', methods=['GET'])
def get_filter_options():
    """Get available filter options"""
    try:
        # Get unique values for key fields
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "types": {"$addToSet": "$type"},
                    "products": {"$addToSet": "$product"},
                    "categories": {"$addToSet": "$category"},
                    "priorities": {"$addToSet": "$priority"},
                    "statuses": {"$addToSet": "$status"}
                }
            }
        ]
        
        result = list(db_manager.collection.aggregate(pipeline))
        
        if result:
            filters = result[0]
            # Remove None values and sort
            for key in filters:
                if key != "_id":
                    filters[key] = sorted([x for x in filters[key] if x is not None])
        else:
            filters = {
                "types": [],
                "products": [],
                "categories": [],
                "priorities": [],
                "statuses": []
            }
        
        return jsonify(filters)
        
    except Exception as e:
        logger.error(f"❌ Error fetching filter options: {e}")
        return jsonify({"error": "Failed to fetch filter options"}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get collection statistics"""
    try:
        stats = db_manager.get_collection_stats()
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"❌ Error fetching stats: {e}")
        return jsonify({"error": "Failed to fetch statistics"}), 500

@app.route('/api/similar/<doc_id>', methods=['GET'])
def get_similar_documents(doc_id):
    """Find similar documents to a given document"""
    try:
        # Get the source document
        source_doc = db_manager.collection.find_one({"_id": doc_id})
        
        if not source_doc or 'embeddings' not in source_doc:
            return jsonify({"error": "Document not found or no embeddings available"}), 404
        
        # Find similar documents
        limit = min(int(request.args.get('limit', 5)), 20)
        similar_docs = db_manager.vector_search(
            source_doc['embeddings'], 
            limit + 1,  # +1 because the source doc will be in results
            filters={"_id": {"$ne": doc_id}}  # Exclude source document
        )
        
        # Format results
        formatted_results = []
        for doc in similar_docs:
            if str(doc.get('_id')) != doc_id:  # Double check to exclude source
                formatted_result = {
                    "id": str(doc.get('_id', '')),
                    "title": doc.get('title', ''),
                    "type": doc.get('type', ''),
                    "summary": doc.get('summary', ''),
                    "score": doc.get('score', 0),
                    "metadata": {
                        "product": doc.get('product', ''),
                        "category": doc.get('category', ''),
                        "created_date": doc.get('created_date', '')
                    }
                }
                formatted_results.append(formatted_result)
        
        return jsonify({
            "similar_documents": formatted_results[:limit],
            "source_document_id": doc_id,
            "total": len(formatted_results)
        })
        
    except Exception as e:
        logger.error(f"❌ Error finding similar documents: {e}")
        return jsonify({"error": "Failed to find similar documents"}), 500

if __name__ == '__main__':
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.DEBUG
    )
