import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database import DatabaseManager
import logging

@pytest.fixture
def mock_config():
    with patch('database.Config') as mock:
        mock.MONGODB_URI = "mongodb://test"
        mock.DATABASE_NAME = "test_db"
        mock.COLLECTION_NAME = "test_collection"
        mock.VECTOR_INDEX_NAME = "test_vector_index"
        mock.SEARCH_INDEX_NAME = "test_search_index"
        yield mock

@pytest.fixture
def mock_mongo_client():
    with patch('database.MongoClient') as mock:
        client = MagicMock()
        mock.return_value = client
        client.admin.command.return_value = True
        
        mock_db = MagicMock()
        mock_collection = MagicMock()
        client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection
        
        yield client

@pytest.fixture
def db_manager(mock_config, mock_mongo_client):
    with patch.object(DatabaseManager, 'create_indexes'):
        manager = DatabaseManager()
        manager.collection = MagicMock()
        return manager

class TestDatabaseManager:
    def test_text_search_with_compound_operator(self, db_manager):
        mock_results = [
            {"_id": "1", "title": "Test", "content": "Content", "score": 0.9},
            {"_id": "2", "title": "Another", "content": "More content", "score": 0.8}
        ]
        db_manager.collection.aggregate.return_value = mock_results
        
        results = db_manager.text_search("test query", limit=10)
        
        db_manager.collection.aggregate.assert_called_once()
        call_args = db_manager.collection.aggregate.call_args[0][0]
        
        assert "$search" in call_args[0]
        assert "compound" in call_args[0]["$search"]
        assert "should" in call_args[0]["$search"]["compound"]
        
        should_clauses = call_args[0]["$search"]["compound"]["should"]
        title_clause = next((c for c in should_clauses if c["text"]["path"] == "title"), None)
        assert title_clause is not None
        assert "fuzzy" in title_clause["text"]
        assert title_clause["text"]["fuzzy"]["maxEdits"] == 1
        
        assert len(results) == 2
        assert results[0]["title"] == "Test"

    def test_text_search_with_filters(self, db_manager):
        mock_results = [{"_id": "1", "title": "Test", "product": "Adobe Photoshop"}]
        db_manager.collection.aggregate.return_value = mock_results
        
        filters = {"product": "Adobe Photoshop", "category": "Bug"}
        results = db_manager.text_search("test", filters=filters)
        
        call_args = db_manager.collection.aggregate.call_args[0][0]
        search_stage = call_args[0]["$search"]
        
        assert "filter" in search_stage["compound"]
        filter_clauses = search_stage["compound"]["filter"]
        assert len(filter_clauses) == 2
        
        product_filter = next((f for f in filter_clauses if f["equals"]["path"] == "product"), None)
        assert product_filter["equals"]["value"] == "Adobe Photoshop"

    def test_hybrid_search_with_rank_fusion(self, db_manager):
        mock_results = [
            {"_id": "1", "title": "Hybrid Result", "score": 0.95},
            {"_id": "2", "title": "Another Result", "score": 0.85}
        ]
        db_manager.collection.aggregate.return_value = mock_results
        
        query_vector = [0.1] * 1024
        results = db_manager.hybrid_search("test query", query_vector, limit=5)
        
        call_args = db_manager.collection.aggregate.call_args[0][0]
        
        assert "$rankFusion" in call_args[0]
        rank_fusion = call_args[0]["$rankFusion"]
        assert "input" in rank_fusion
        assert "pipelines" in rank_fusion["input"]
        assert "vector" in rank_fusion["input"]["pipelines"]
        assert "text" in rank_fusion["input"]["pipelines"]
        
        vector_pipeline = rank_fusion["input"]["pipelines"]["vector"]
        assert "$vectorSearch" in vector_pipeline[0]
        
        text_pipeline = rank_fusion["input"]["pipelines"]["text"]
        assert "$search" in text_pipeline[0]
        assert "compound" in text_pipeline[0]["$search"]
        
        assert len(results) == 2

    def test_hybrid_search_with_filters(self, db_manager):
        mock_results = [{"_id": "1", "title": "Filtered Result"}]
        db_manager.collection.aggregate.return_value = mock_results
        
        query_vector = [0.1] * 1024
        filters = {"type": "jira", "priority": "High"}
        results = db_manager.hybrid_search("test", query_vector, filters=filters)
        
        call_args = db_manager.collection.aggregate.call_args[0][0]
        rank_fusion = call_args[0]["$rankFusion"]
        
        vector_pipeline = rank_fusion["input"]["pipelines"]["vector"]
        text_pipeline = rank_fusion["input"]["pipelines"]["text"]
        
        assert "$match" in vector_pipeline[1]
        
        match_stage = next((stage for stage in text_pipeline if "$match" in stage), None)
        assert match_stage is not None

    def test_error_handling_text_search(self, db_manager):
        db_manager.collection.aggregate.side_effect = Exception("Database error")
        
        results = db_manager.text_search("test query")
        
        assert results == []

    def test_error_handling_hybrid_search(self, db_manager):
        db_manager.collection.aggregate.side_effect = Exception("Database error")
        
        query_vector = [0.1] * 1024
        results = db_manager.hybrid_search("test", query_vector)
        
        assert results == []

    def test_text_search_no_filters(self, db_manager):
        mock_results = [{"_id": "1", "title": "No Filter Test"}]
        db_manager.collection.aggregate.return_value = mock_results
        
        results = db_manager.text_search("test query")
        
        call_args = db_manager.collection.aggregate.call_args[0][0]
        search_stage = call_args[0]["$search"]
        
        assert "filter" not in search_stage["compound"]
        assert len(results) == 1

    def test_hybrid_search_no_filters(self, db_manager):
        mock_results = [{"_id": "1", "title": "No Filter Hybrid"}]
        db_manager.collection.aggregate.return_value = mock_results
        
        query_vector = [0.1] * 1024
        results = db_manager.hybrid_search("test", query_vector)
        
        call_args = db_manager.collection.aggregate.call_args[0][0]
        rank_fusion = call_args[0]["$rankFusion"]
        
        vector_pipeline = rank_fusion["input"]["pipelines"]["vector"]
        text_pipeline = rank_fusion["input"]["pipelines"]["text"]
        
        assert len(vector_pipeline) == 1
        assert "$vectorSearch" in vector_pipeline[0]
        
        assert len(text_pipeline) == 2
        assert "$search" in text_pipeline[0]
        assert "$limit" in text_pipeline[1]
        
        assert len(results) == 1
