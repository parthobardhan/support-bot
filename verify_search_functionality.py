#!/usr/bin/env python3
"""
Simple verification script to test search functionality without external dependencies
"""
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from database import DatabaseManager
    from config import Config
    print("✅ Successfully imported DatabaseManager and Config")
    
    db_manager = DatabaseManager.__new__(DatabaseManager)  # Create instance without calling __init__
    
    import inspect
    text_search_sig = inspect.signature(DatabaseManager.text_search)
    expected_params = ['self', 'query', 'limit', 'filters']
    actual_params = list(text_search_sig.parameters.keys())
    assert actual_params == expected_params, f"text_search signature mismatch: {actual_params}"
    print("✅ text_search method has correct signature")
    
    hybrid_search_sig = inspect.signature(DatabaseManager.hybrid_search)
    expected_params = ['self', 'query', 'query_vector', 'limit', 'filters']
    actual_params = list(hybrid_search_sig.parameters.keys())
    assert actual_params == expected_params, f"hybrid_search signature mismatch: {actual_params}"
    print("✅ hybrid_search method has correct signature")
    
    required_attrs = ['SEARCH_INDEX_NAME', 'VECTOR_INDEX_NAME', 'DATABASE_NAME', 'COLLECTION_NAME']
    for attr in required_attrs:
        assert hasattr(Config, attr), f"Config missing required attribute: {attr}"
    print("✅ Config has all required attributes")
    
    print("🎉 All verification checks passed!")
    
except Exception as e:
    print(f"❌ Verification failed: {e}")
    sys.exit(1)
