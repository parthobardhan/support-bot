#!/usr/bin/env python3
"""
Script to set up the MongoDB collection, generate mock data, and load it with embeddings
"""
import sys
import os

# Add the parent directory to the path so we can import from other modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import Config
from backend.database import DatabaseManager
from backend.embeddings_service import EmbeddingsService
from data_generation.mock_data_generator import MockDataGenerator
from data_generation.data_processor import DataProcessor

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main setup function"""
    try:
        logger.info("🚀 Starting database setup process...")
        
        # Initialize services
        logger.info("📋 Initializing services...")
        Config.validate_config()
        db_manager = DatabaseManager()
        embeddings_service = EmbeddingsService()
        data_generator = MockDataGenerator()
        data_processor = DataProcessor()
        
        # Test connections
        logger.info("🧪 Testing connections...")
        if not embeddings_service.test_connection():
            raise Exception("Failed to connect to Voyage AI API")
        
        # Generate mock data
        logger.info("📝 Generating mock data...")
        mock_data = data_generator.generate_all_data(1000)
        logger.info(f"✅ Generated {len(mock_data)} mock documents")
        
        # Process data (chunk and add embeddings)
        logger.info("⚙️ Processing data and generating embeddings...")
        processed_data = data_processor.process_batch(mock_data, add_embeddings=True)
        logger.info(f"✅ Processed {len(processed_data)} document chunks")
        
        # Validate processed data
        logger.info("🔍 Validating processed data...")
        validation = data_processor.validate_processed_data(processed_data)
        logger.info(f"📊 Validation results: {validation}")
        
        if validation["documents_without_embeddings"] > 0:
            logger.warning(f"⚠️ {validation['documents_without_embeddings']} documents missing embeddings")
        
        # Insert into MongoDB
        logger.info("💾 Inserting data into MongoDB...")
        inserted_count = db_manager.insert_documents(processed_data)
        logger.info(f"✅ Inserted {inserted_count} documents into MongoDB")
        
        # Get collection stats
        logger.info("📈 Getting collection statistics...")
        stats = db_manager.get_collection_stats()
        logger.info(f"📊 Collection stats: {stats}")
        
        # Test vector search
        logger.info("🔍 Testing vector search...")
        test_query = "How to fix Adobe Photoshop performance issues"
        test_embedding = embeddings_service.get_single_embedding(test_query)
        search_results = db_manager.vector_search(test_embedding, limit=5)
        
        logger.info(f"🎯 Vector search test returned {len(search_results)} results")
        for i, result in enumerate(search_results[:3]):
            logger.info(f"  {i+1}. {result.get('title', 'No title')} (Score: {result.get('score', 0):.3f})")
        
        logger.info("🎉 Database setup completed successfully!")
        
        print("\n" + "="*80)
        print("SETUP COMPLETE")
        print("="*80)
        print(f"✅ Generated and inserted {inserted_count} documents")
        print(f"✅ Collection: {Config.DATABASE_NAME}.{Config.COLLECTION_NAME}")
        print(f"✅ Total documents: {stats.get('total_documents', 0)}")
        print(f"✅ Vector search index: {Config.VECTOR_INDEX_NAME}")
        print(f"✅ Text search index: {Config.SEARCH_INDEX_NAME}")
        print("\nNext steps:")
        print("1. Create vector search index in MongoDB Atlas")
        print("2. Start the backend server: python backend/app.py")
        print("3. Open the frontend application")
        print("="*80)
        
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
