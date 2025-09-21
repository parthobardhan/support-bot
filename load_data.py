#!/usr/bin/env python3
"""
Simple script to load data into MongoDB Atlas
"""
import sys
import os
import logging
from datetime import datetime
from pymongo import MongoClient
import requests
import time
import random

# Configuration
MONGODB_URI = "mongodb+srv://psb:passw0rd@demo-cluster-1.o9q0k.mongodb.net/?retryWrites=true&w=majority&appName=Demo-Cluster-1"
DATABASE_NAME = "support_bot"
COLLECTION_NAME = "knowledge_base"
VOYAGE_API_KEY = "pa-TRb4Em9ehYAVf6JAkVYDFBHRh5Kf2AwxaJhvoKLVae8"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleDataLoader:
    def __init__(self):
        self.client = MongoClient(MONGODB_URI)
        self.db = self.client[DATABASE_NAME]
        self.collection = self.db[COLLECTION_NAME]
        
    def test_connection(self):
        try:
            self.client.admin.command('ping')
            logger.info("✅ Successfully connected to MongoDB Atlas")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            return False
    
    def get_embedding(self, text):
        """Get embedding from Voyage AI"""
        headers = {
            "Authorization": f"Bearer {VOYAGE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "input": [text],
            "model": "voyage-3-large"
        }
        
        try:
            response = requests.post("https://api.voyageai.com/v1/embeddings", 
                                   json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data['data'][0]['embedding']
        except Exception as e:
            logger.error(f"❌ Error getting embedding: {e}")
            return None
    
    def generate_mock_documents(self, count=1000):
        """Generate mock Adobe support documents"""
        logger.info(f"📝 Generating {count} mock documents...")
        
        adobe_products = [
            "Adobe Photoshop", "Adobe Illustrator", "Adobe InDesign", "Adobe Premiere Pro",
            "Adobe After Effects", "Adobe Lightroom", "Adobe XD", "Adobe Acrobat",
            "Adobe Creative Cloud", "Adobe Experience Manager", "Adobe Analytics",
            "Adobe Target", "Adobe Campaign", "Adobe Audience Manager"
        ]
        
        doc_types = ["jira", "documentation", "knowledge"]
        priorities = ["Highest", "High", "Medium", "Low", "Lowest"]
        categories = ["Bug Fix", "Feature Request", "User Guide", "API Reference", 
                     "Troubleshooting", "Best Practices", "How-to", "FAQ"]
        
        documents = []
        
        for i in range(count):
            doc_type = random.choice(doc_types)
            product = random.choice(adobe_products)
            priority = random.choice(priorities) if doc_type == "jira" else None
            category = random.choice(categories)
            
            if doc_type == "jira":
                title = f"{product} - {category}: Issues with performance and stability"
                content = f"""
                This {category.lower()} has been reported for {product} by multiple users.
                
                Description: Users are experiencing performance degradation and stability issues 
                when working with large files in {product}. The application becomes unresponsive 
                and may crash during intensive operations.
                
                Steps to Reproduce:
                1. Open {product}
                2. Load a large project or file (>500MB)
                3. Perform resource-intensive operations
                4. Observe performance degradation
                
                Expected Behavior: The application should maintain good performance and stability.
                Actual Behavior: The application slows down significantly and may crash.
                
                Environment: Windows 10/11, macOS Monterey/Ventura
                Priority: {priority}
                """
                
            elif doc_type == "documentation":
                title = f"{product} {category} - Official Documentation"
                content = f"""
                Comprehensive {category.lower()} for {product}.
                
                Overview:
                This document provides detailed information about using {product} effectively.
                
                Key Features:
                - Professional-grade tools and capabilities
                - Intuitive user interface design
                - Cross-platform compatibility
                - Cloud integration with Creative Cloud
                - Advanced workflow automation
                
                Getting Started:
                1. Download and install {product} from Adobe Creative Cloud
                2. Launch the application and complete setup
                3. Familiarize yourself with the interface
                4. Explore the main tools and features
                
                Advanced Features:
                {product} offers extensive professional features including advanced filters,
                automation capabilities, scripting support, and integration with other Adobe applications.
                """
                
            else:  # knowledge
                title = f"How to optimize {product} for better performance"
                content = f"""
                Knowledge base article for {product} performance optimization.
                
                Introduction:
                This article provides expert guidance on optimizing {product} performance.
                
                Performance Tips:
                - Close unnecessary applications to free up system resources
                - Increase RAM allocation in application preferences
                - Use optimized project settings for your workflow
                - Clear cache and temporary files regularly
                - Update to the latest version for performance improvements
                
                System Requirements:
                - Operating System: Windows 10 (64-bit) or macOS 10.15+
                - RAM: 16 GB minimum, 32 GB recommended
                - Graphics: GPU with DirectX 12 support
                - Storage: SSD recommended for better performance
                
                Troubleshooting Common Issues:
                If you experience performance issues, try updating graphics drivers,
                resetting preferences, or running the built-in repair tool.
                """
            
            doc = {
                "_id": f"{doc_type.upper()}-{i+1:05d}",
                "type": doc_type,
                "title": title,
                "content": content,
                "summary": f"Support document for {product} - {category}",
                "product": product,
                "category": category,
                "priority": priority,
                "status": random.choice(["Open", "In Progress", "Resolved"]) if doc_type == "jira" else None,
                "created_date": datetime.now(),
                "tags": [product.lower().replace(" ", "_"), category.lower(), doc_type]
            }
            
            documents.append(doc)
            
            if (i + 1) % 100 == 0:
                logger.info(f"Generated {i + 1}/{count} documents...")
        
        logger.info(f"✅ Generated {len(documents)} documents")
        return documents
    
    def add_embeddings_to_documents(self, documents, batch_size=5):
        """Add embeddings to documents"""
        logger.info(f"🔧 Adding embeddings to {len(documents)} documents...")
        
        for i, doc in enumerate(documents):
            try:
                # Create text for embedding
                text = f"{doc['title']} {doc['summary']} {doc['content'][:1000]}"
                
                # Get embedding
                embedding = self.get_embedding(text)
                if embedding:
                    doc['embeddings'] = embedding
                    doc['embedding_model'] = "voyage-3-large"
                    doc['embedding_dimensions'] = len(embedding)
                
                if (i + 1) % batch_size == 0:
                    logger.info(f"Added embeddings to {i + 1}/{len(documents)} documents...")
                    time.sleep(0.2)  # Rate limiting
                    
            except Exception as e:
                logger.error(f"Error adding embedding to document {i}: {e}")
                continue
        
        return documents
    
    def load_documents(self, documents):
        """Load documents into MongoDB"""
        logger.info(f"💾 Loading {len(documents)} documents into MongoDB...")
        
        try:
            # Clear existing data
            self.collection.delete_many({})
            logger.info("🗑️ Cleared existing data")
            
            # Insert new documents
            result = self.collection.insert_many(documents, ordered=False)
            logger.info(f"✅ Inserted {len(result.inserted_ids)} documents")
            
            return len(result.inserted_ids)
            
        except Exception as e:
            logger.error(f"❌ Error loading documents: {e}")
            return 0
    
    def get_stats(self):
        """Get collection statistics"""
        try:
            total = self.collection.count_documents({})
            
            # Get type distribution
            pipeline = [{"$group": {"_id": "$type", "count": {"$sum": 1}}}]
            type_counts = list(self.collection.aggregate(pipeline))
            
            return {
                "total_documents": total,
                "type_distribution": {item["_id"]: item["count"] for item in type_counts}
            }
        except Exception as e:
            logger.error(f"❌ Error getting stats: {e}")
            return {}

def main():
    """Main function"""
    logger.info("🚀 Starting data loading process...")
    
    loader = SimpleDataLoader()
    
    # Test connection
    if not loader.test_connection():
        logger.error("❌ Cannot connect to MongoDB Atlas")
        return False
    
    # Generate mock data
    documents = loader.generate_mock_documents(1000)
    
    # Add embeddings
    documents = loader.add_embeddings_to_documents(documents)
    
    # Load documents
    loaded_count = loader.load_documents(documents)
    
    # Get stats
    stats = loader.get_stats()
    
    logger.info("🎉 Data loading completed!")
    logger.info(f"📊 Statistics: {stats}")
    
    print("\n" + "="*60)
    print("DATA LOADING COMPLETE")
    print("="*60)
    print(f"✅ Loaded {loaded_count} documents into MongoDB Atlas")
    print(f"📊 Total documents: {stats.get('total_documents', 0)}")
    print(f"📊 Type distribution: {stats.get('type_distribution', {})}")
    print("="*60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
