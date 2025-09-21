import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Any
import re
import logging
from backend.embeddings_service import EmbeddingsService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embeddings_service = EmbeddingsService()
    
    def chunk_text(self, text: str, max_chunk_size: int = None) -> List[str]:
        """Split text into overlapping chunks"""
        if max_chunk_size is None:
            max_chunk_size = self.chunk_size
            
        if len(text) <= max_chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + max_chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings near the end
                for i in range(end, max(start + max_chunk_size//2, end - 100), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
                
                # If no sentence boundary found, break at word boundary
                if end == start + max_chunk_size:
                    for i in range(end, max(start + max_chunk_size//2, end - 50), -1):
                        if text[i] in ' \t\n':
                            end = i
                            break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            if start >= len(text):
                break
                
        return chunks
    
    def process_document(self, doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process a document and create chunks with embeddings"""
        processed_chunks = []
        
        # Combine title, summary, and content for chunking
        full_text = f"{doc.get('title', '')} {doc.get('summary', '')} {doc.get('content', '')}"
        
        # Clean the text
        cleaned_text = self._clean_text(full_text)
        
        # Create chunks
        chunks = self.chunk_text(cleaned_text)
        
        for i, chunk in enumerate(chunks):
            chunk_doc = doc.copy()
            chunk_doc['chunk_text'] = chunk
            chunk_doc['chunk_index'] = i
            chunk_doc['total_chunks'] = len(chunks)
            chunk_doc['original_id'] = doc.get('_id')
            chunk_doc['_id'] = f"{doc.get('_id')}_chunk_{i}"
            
            processed_chunks.append(chunk_doc)
        
        return processed_chunks
    
    def add_embeddings(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add embeddings to documents"""
        logger.info(f"Generating embeddings for {len(documents)} documents...")
        
        # Extract texts for embedding
        texts = []
        for doc in documents:
            # Use chunk_text if available, otherwise combine title and content
            text = doc.get('chunk_text', '')
            if not text:
                text = f"{doc.get('title', '')} {doc.get('summary', '')} {doc.get('content', '')}"
            texts.append(text)
        
        # Generate embeddings
        try:
            embeddings = self.embeddings_service.get_embeddings(texts)
            
            # Add embeddings to documents
            for i, doc in enumerate(documents):
                if i < len(embeddings):
                    doc['embeddings'] = embeddings[i]
                    doc['embedding_model'] = self.embeddings_service.model
                    doc['embedding_dimensions'] = len(embeddings[i])
            
            logger.info(f"✅ Successfully added embeddings to {len(documents)} documents")
            return documents
            
        except Exception as e:
            logger.error(f"❌ Error adding embeddings: {e}")
            return documents
    
    def process_batch(self, documents: List[Dict[str, Any]], 
                     add_embeddings: bool = True) -> List[Dict[str, Any]]:
        """Process a batch of documents"""
        processed_docs = []
        
        logger.info(f"Processing batch of {len(documents)} documents...")
        
        for doc in documents:
            chunks = self.process_document(doc)
            processed_docs.extend(chunks)
        
        logger.info(f"Created {len(processed_docs)} chunks from {len(documents)} documents")
        
        if add_embeddings:
            processed_docs = self.add_embeddings(processed_docs)
        
        return processed_docs
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might interfere with search
        text = re.sub(r'[^\w\s\.\,\!\?\:\;\-\(\)]+', '', text)
        
        # Normalize line breaks
        text = text.replace('\n', ' ').replace('\r', ' ')
        
        return text.strip()
    
    def validate_processed_data(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate processed documents"""
        validation_results = {
            "total_documents": len(documents),
            "documents_with_embeddings": 0,
            "documents_without_embeddings": 0,
            "average_chunk_size": 0,
            "embedding_dimensions": None,
            "validation_errors": []
        }
        
        chunk_sizes = []
        
        for doc in documents:
            # Check for embeddings
            if 'embeddings' in doc and doc['embeddings']:
                validation_results["documents_with_embeddings"] += 1
                if validation_results["embedding_dimensions"] is None:
                    validation_results["embedding_dimensions"] = len(doc['embeddings'])
            else:
                validation_results["documents_without_embeddings"] += 1
                validation_results["validation_errors"].append(f"Document {doc.get('_id')} missing embeddings")
            
            # Check chunk size
            chunk_text = doc.get('chunk_text', '')
            if chunk_text:
                chunk_sizes.append(len(chunk_text))
        
        if chunk_sizes:
            validation_results["average_chunk_size"] = sum(chunk_sizes) / len(chunk_sizes)
        
        return validation_results
