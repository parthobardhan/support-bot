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
            # First try Atlas Search
            compound_clauses = [
                {
                    "text": {
                        "query": query,
                        "path": ["content", "summary", "tags"],
                        "score": {"boost": {"value": 1.0}}
                    }
                },
                {
                    "text": {
                        "query": query,
                        "path": "title",
                        "fuzzy": {"maxEdits": 1},
                        "score": {"boost": {"value": 2.0}}
                    }
                }
            ]
            
            # Add filter clauses if provided
            filter_clauses = []
            should_clauses_for_filters = []
            
            if filters:
                for field, value in filters.items():
                    if field in ["product", "category", "type", "priority", "status"]:
                        # Handle MongoDB query objects like {$in: [...]}
                        if isinstance(value, dict) and "$in" in value:
                            # For $in queries, create multiple equals filters with should logic
                            in_values = value["$in"]
                            if in_values:  # Only add if there are values
                                # Create individual equals filters for each value
                                for in_value in in_values:
                                    should_clauses_for_filters.append({
                                        "equals": {
                                            "path": field,
                                            "value": str(in_value)  # Ensure it's a string
                                        }
                                    })
                        else:
                            # Handle simple value filters
                            filter_clauses.append({
                                "equals": {
                                    "path": field,
                                    "value": str(value)  # Ensure it's a string
                                }
                            })
            
            search_stage = {
                "$search": {
                    "index": Config.SEARCH_INDEX_NAME,
                    "compound": {
                        "should": compound_clauses
                    }
                }
            }
            
            # Add $in-based should clauses to the main should array
            if should_clauses_for_filters:
                search_stage["$search"]["compound"]["should"].extend(should_clauses_for_filters)
            
            # Add simple filter clauses
            if filter_clauses:
                search_stage["$search"]["compound"]["filter"] = filter_clauses
            
            pipeline = [
                search_stage,
                {"$limit": limit},
                {
                    "$project": {
                        "title": 1,
                        "content": 1,
                        "type": 1,
                        "priority": 1,
                        "status": 1,
                        "summary": 1,
                        "tags": 1,
                        "product": 1,
                        "category": 1,
                        "created_date": 1,
                        "score": {"$meta": "searchScore"}
                    }
                }
            ]
            
            results = list(self.collection.aggregate(pipeline))
            if results:
                logger.info(f"✅ Atlas Search returned {len(results)} results")
                return results
            
        except Exception as e:
            logger.error(f"❌ Error in Atlas Search: {e}")

    
    def hybrid_search(self, query: str, query_vector: List[float], 
                     limit: int = 10, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Perform hybrid search by combining vector and text search results manually"""
        try:
            # Get vector search results
            vector_results = self.vector_search(query_vector, limit//2, filters)
            
            # Get text search results  
            text_results = self.text_search(query, limit//2, filters)
            
            # Combine and deduplicate results
            combined_results = []
            seen_ids = set()
            
            # Add vector results with boosted scores
            for result in vector_results:
                doc_id = str(result.get('_id'))
                if doc_id not in seen_ids:
                    seen_ids.add(doc_id)
                    # Boost vector search scores
                    result['score'] = result.get('score', 0) * 1.2
                    result['search_type'] = 'vector'
                    combined_results.append(result)
            
            # Add text results
            for result in text_results:
                doc_id = str(result.get('_id'))
                if doc_id not in seen_ids:
                    seen_ids.add(doc_id)
                    result['search_type'] = 'text'
                    combined_results.append(result)
                else:
                    # If document exists in both results, combine scores
                    for existing in combined_results:
                        if str(existing.get('_id')) == doc_id:
                            existing['score'] = existing.get('score', 0) + result.get('score', 0)
                            existing['search_type'] = 'hybrid'
                            break
            
            # Sort by combined score
            combined_results.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            # Limit final results
            final_results = combined_results[:limit]
            
            logger.info(f"✅ Manual hybrid search returned {len(final_results)} results")
            return final_results
            
        except Exception as e:
            logger.error(f"❌ Error in manual hybrid search: {e}")
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
