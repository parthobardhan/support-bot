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
            if filters:
                for field, value in filters.items():
                    if field in ["product", "category", "type", "priority", "status"]:
                        filter_clauses.append({
                            "equals": {
                                "path": field,
                                "value": value
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
            logger.info(f"✅ Atlas Search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error in Atlas Search: {e}")
            return []
    
    def hybrid_search(self, query: str, query_vector: List[float], 
                     limit: int = 10, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Perform hybrid search using $rankFusion"""
        try:
            filter_stage = {}
            if filters:
                filter_conditions = []
                for field, value in filters.items():
                    if field in ["product", "category", "type", "priority", "status"]:
                        filter_conditions.append({field: value})
                if filter_conditions:
                    filter_stage = {"$match": {"$and": filter_conditions}}
            
            vector_pipeline = [
                {
                    "$vectorSearch": {
                        "index": Config.VECTOR_INDEX_NAME,
                        "path": "embeddings",
                        "queryVector": query_vector,
                        "numCandidates": limit * 5,
                        "limit": limit * 2
                    }
                }
            ]
            
            text_pipeline = [
                {
                    "$search": {
                        "index": Config.SEARCH_INDEX_NAME,
                        "compound": {
                            "should": [
                                {
                                    "text": {
                                        "query": query,
                                        "path": ["content", "summary", "tags"]
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
                        }
                    }
                },
                {"$limit": limit * 2}
            ]
            
            # Add filter stage to both pipelines if needed
            if filter_stage:
                vector_pipeline.insert(1, filter_stage)
                text_pipeline.append(filter_stage)
            
            fusion_pipeline = [
                {
                    "$rankFusion": {
                        "input": {
                            "pipelines": {
                                "vector": vector_pipeline,
                                "text": text_pipeline
                            }
                        },
                        "output": {
                            "limit": limit
                        }
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
                        "product": 1,
                        "category": 1,
                        "created_date": 1,
                        "score": {"$meta": "rankFusionScore"}
                    }
                }
            ]
            
            results = list(self.collection.aggregate(fusion_pipeline))
            logger.info(f"✅ Hybrid search with rank fusion returned {len(results)} results")
            return results
            
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
