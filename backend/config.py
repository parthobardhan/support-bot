import os
from typing import Optional

class Config:
    # MongoDB Atlas Configuration
    MONGODB_URI = "mongodb+srv://psb:passw0rd@demo-cluster-1.o9q0k.mongodb.net/?retryWrites=true&w=majority&appName=Demo-Cluster-1"
    DATABASE_NAME = "support_bot"
    COLLECTION_NAME = "knowledge_base"
    
    # MongoDB Atlas API Configuration  
    ATLAS_PUBLIC_KEY = "rbqfhhol"
    ATLAS_PRIVATE_KEY = "d380c0c0-f521-4193-b472-8b233cde15a4"
    ATLAS_BASE_URL = "https://cloud.mongodb.com/api/atlas/v1.0"
    
    # Voyage AI Configuration
    VOYAGE_API_KEY = "pa-TRb4Em9ehYAVf6JAkVYDFBHRh5Kf2AwxaJhvoKLVae8"
    VOYAGE_MODEL = "voyage-3-large"
    
    # Application Configuration
    FLASK_HOST = "0.0.0.0"
    FLASK_PORT = 5001  # Changed from 5000 to 5001
    DEBUG = True
    
    # Vector Search Configuration
    VECTOR_INDEX_NAME = "vector_index"
    SEARCH_INDEX_NAME = "search_index"
    
    # Chunking Configuration
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present"""
        required_vars = [
            'MONGODB_URI', 'VOYAGE_API_KEY', 'ATLAS_PUBLIC_KEY', 'ATLAS_PRIVATE_KEY'
        ]
        
        for var in required_vars:
            if not getattr(cls, var):
                raise ValueError(f"Required configuration {var} is missing")
        
        print("✅ Configuration validated successfully")
