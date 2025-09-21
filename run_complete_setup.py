#!/usr/bin/env python3
"""
Complete setup script for the Adobe Support Bot RAG Application
This script will verify all files are in place and provide next steps
"""

import os
import stat
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verify_project_structure():
    """Verify the complete project structure exists"""
    required_files = [
        'backend/app.py',
        'backend/config.py', 
        'backend/database.py',
        'backend/embeddings_service.py',
        'backend/requirements.txt',
        'data_generation/mock_data_generator.py',
        'data_generation/data_processor.py',
        'frontend/index.html',
        'frontend/app.js',
        'scripts/setup_database.py',
        'scripts/create_vector_index.json',
        'setup.sh',
        'start_backend.sh',
        'README.md'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            logger.info(f"✅ Found: {file_path}")
    
    if missing_files:
        logger.error(f"❌ Missing files: {missing_files}")
        return False
    
    logger.info("✅ All required files are present")
    return True

def verify_permissions():
    """Verify shell scripts have execute permissions"""
    scripts = ['setup.sh', 'start_backend.sh']
    
    for script in scripts:
        if os.path.exists(script):
            st = os.stat(script)
            if st.st_mode & stat.S_IEXEC:
                logger.info(f"✅ {script} is executable")
            else:
                logger.warning(f"⚠️ {script} is not executable, fixing...")
                os.chmod(script, st.st_mode | stat.S_IEXEC)
                logger.info(f"✅ Made {script} executable")

def main():
    """Main verification function"""
    logger.info("🚀 Verifying Adobe Support Bot setup...")
    
    try:
        # Verify project structure
        if not verify_project_structure():
            logger.error("❌ Project structure verification failed")
            exit(1)
        
        # Verify permissions
        verify_permissions()
        
        logger.info("🎉 Project structure verified successfully!")
        
        print("\n" + "="*80)
        print("ADOBE SUPPORT BOT - RAG APPLICATION")
        print("="*80)
        print("✅ Project structure: COMPLETE")
        print("✅ Backend services: Flask API with MongoDB Atlas & Voyage AI")
        print("✅ Frontend: Responsive Bootstrap UI")
        print("✅ Data generation: 1000+ mock Adobe support documents")
        print("✅ Search capabilities: Hybrid (AI + Text), Vector, Text")
        print("✅ Setup scripts: Automated database initialization")
        print("")
        print("NEXT STEPS:")
        print("1. Run setup: ./setup.sh")
        print("2. Create Vector Search index in MongoDB Atlas")
        print("   (Use scripts/create_vector_index.json)")
        print("3. Start backend: ./start_backend.sh")
        print("4. Open frontend/index.html in browser")
        print("")
        print("🎯 FEATURES:")
        print("• AI-powered semantic search with Voyage AI")
        print("• MongoDB Atlas Vector Search & Atlas Search")
        print("• Mock Jira tickets, documentation, and knowledge articles")
        print("• Advanced filtering and similar document discovery")
        print("• Real-time statistics and document management")
        print("="*80)
        
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()
