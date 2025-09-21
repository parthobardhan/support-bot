import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    # MongoDB Atlas Configuration
    MONGODB_URI = os.getenv('MONGODB_URI', '')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'support_bot')
    COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'knowledge_base')
    
    # MongoDB Atlas API Configuration  
    ATLAS_PUBLIC_KEY = os.getenv('ATLAS_PUBLIC_KEY', '')
    ATLAS_PRIVATE_KEY = os.getenv('ATLAS_PRIVATE_KEY', '')
    ATLAS_BASE_URL = os.getenv('ATLAS_BASE_URL', 'https://cloud.mongodb.com/api/atlas/v1.0')
    
    # Voyage AI Configuration
    VOYAGE_API_KEY = os.getenv('VOYAGE_API_KEY', '')
    VOYAGE_MODEL = os.getenv('VOYAGE_MODEL', 'voyage-3-large')
    
    # Application Configuration
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', '5001'))
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Vector Search Configuration
    VECTOR_INDEX_NAME = os.getenv('VECTOR_INDEX_NAME', 'vector_index')
    SEARCH_INDEX_NAME = os.getenv('SEARCH_INDEX_NAME', 'search_index')
    
    # Chunking Configuration
    CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '1000'))
    CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', '200'))
    
    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present"""
        required_vars = [
            'MONGODB_URI', 'VOYAGE_API_KEY', 'ATLAS_PUBLIC_KEY', 'ATLAS_PRIVATE_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            value = getattr(cls, var)
            if not value or value.strip() == '':
                missing_vars.append(var)
        
        if missing_vars:
            env_vars_msg = ", ".join([f"{var}" for var in missing_vars])
            raise ValueError(
                f"❌ Required environment variables are missing or empty: {env_vars_msg}\n"
                f"Please set these environment variables or create a .env file with the required values."
            )
        
        print("✅ Configuration validated successfully")
        return True
