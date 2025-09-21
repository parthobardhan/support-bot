from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from typing import List, Dict, Any, Optional
import logging
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self.connect()
    
    def connect(self):
        """Connect to MongoDB Atlas"""
        try:
            self.client = MongoClient(Config.MONGODB_URI)
            
            # Test the connection
            self.client.admin.command('ping')
            logger.info("✅ Successfully connected to MongoDB Atlas")
            
            self.db = self.client[Config.DATABASE_NAME]
            self.collection = self.db[Config.COLLECTION_NAME]
            
            # Create indexes if they don't exist
            self.create_indexes()
            
        except ConnectionFailure as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    def create_indexes(self):
        """Create necessary indexes for the collection"""
        try:
            # Create text search index
            text_index = {
                "title": "text",
                "content": "text", 
                "summary": "text",
                "tags": "text"
            }
            self.collection.create_index([
                ("title", "text"),
                ("content", "text"),
                ("summary", "text"),
                ("tags", "text")
            ], name="text_search_index")
            
            # Create indexes for filtering
            self.collection.create_index("type")
            self.collection.create_index("priority") 
            self.collection.create_index("status")
            self.collection.create_index("created_date")
            self.collection.create_index("chunk_id")
            
            logger.info("✅ Indexes created successfully")
            
        except Exception as e:
            logger.error(f"❌ Error creating indexes: {e}")
    
    def insert_documents(self, documents: List[Dict[str, Any]]) -> int:
        """Insert multiple documents into the collection"""
        try:
            if not documents:
                return 0
                
            result = self.collection.insert_many(documents, ordered=False)
            logger.info(f"✅ Inserted {len(result.inserted_ids)} documents")
            return len(result.inserted_ids)
            
        except DuplicateKeyError as e:
            logger.warning(f"⚠️ Some documents already exist: {e}")
            return 0
        except Exception as e:
            logger.error(f"❌ Error inserting documents: {e}")
            raise
    
    def vector_search(self, query_vector: List[float], limit: int = 10, 
                     filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Perform vector search using MongoDB Atlas Vector Search"""
        try:
            pipeline = [
                {
                    "$vectorSearch": {
                        "index": Config.VECTOR_INDEX_NAME,
                        "path": "embeddings",
                        "queryVector": query_vector,
                        "numCandidates": limit * 5,
                        "limit": limit
                    }
                },
                {
                    "$project": {
                        "title": 1,
                        "content": 1,
                        "type": 1,
                        "priority": 1,
                        "status": 1,
                        "summary": 1,
                        "tags": 1,
                        "created_date": 1,
                        "score": {"$meta": "vectorSearchScore"}
                    }
                }
            ]
            
            # Add filters if provided
            if filters:
                match_stage = {"$match": filters}
                pipeline.insert(1, match_stage)
            
            results = list(self.collection.aggregate(pipeline))
            logger.info(f"✅ Vector search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error in vector search: {e}")
            return []
    
    def text_search(self, query: str, limit: int = 10, 
                   filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Perform text search using MongoDB Atlas Search"""
        try:
            search_query = {
                "$text": {"$search": query}
            }
            
            if filters:
                search_query.update(filters)
            
            results = list(
                self.collection.find(
                    search_query,
                    {"score": {"$meta": "textScore"}}
                ).sort([("score", {"$meta": "textScore"})]).limit(limit)
            )
            
            logger.info(f"✅ Text search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error in text search: {e}")
            return []
    
    def hybrid_search(self, query: str, query_vector: List[float], 
                     limit: int = 10, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Perform hybrid search combining text and vector search"""
        try:
            # Get vector search results
            vector_results = self.vector_search(query_vector, limit//2, filters)
            
            # Get text search results  
            text_results = self.text_search(query, limit//2, filters)
            
            # Combine and deduplicate results
            combined_results = []
            seen_ids = set()
            
            for result in vector_results + text_results:
                doc_id = str(result.get('_id'))
                if doc_id not in seen_ids:
                    seen_ids.add(doc_id)
                    combined_results.append(result)
            
            # Sort by relevance score
            combined_results.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            logger.info(f"✅ Hybrid search returned {len(combined_results[:limit])} results")
            return combined_results[:limit]
            
        except Exception as e:
            logger.error(f"❌ Error in hybrid search: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        try:
            stats = self.db.command("collStats", Config.COLLECTION_NAME)
            doc_count = self.collection.count_documents({})
            
            type_counts = list(self.collection.aggregate([
                {"$group": {"_id": "$type", "count": {"$sum": 1}}}
            ]))
            
            return {
                "total_documents": doc_count,
                "collection_size": stats.get("size", 0),
                "average_document_size": stats.get("avgObjSize", 0),
                "type_distribution": {item["_id"]: item["count"] for item in type_counts},
                "indexes": len(stats.get("indexSizes", {}))
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting collection stats: {e}")
            return {}
    
    def close_connection(self):
        """Close the database connection"""
        if self.client:
            self.client.close()
            logger.info("✅ Database connection closed")
