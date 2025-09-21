import requests
import logging
from typing import List, Dict, Any
from config import Config
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingsService:
    def __init__(self):
        self.api_key = Config.VOYAGE_API_KEY
        self.model = Config.VOYAGE_MODEL
        self.base_url = "https://api.voyageai.com/v1/embeddings"
        
    def get_embeddings(self, texts: List[str], batch_size: int = 10) -> List[List[float]]:
        """Generate embeddings for a list of texts using Voyage AI"""
        all_embeddings = []
        
        try:
            # Process texts in batches
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                logger.info(f"Processing batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
                
                embeddings = self._get_batch_embeddings(batch)
                all_embeddings.extend(embeddings)
                
                # Add small delay to respect rate limits
                time.sleep(0.1)
            
            logger.info(f"✅ Generated embeddings for {len(texts)} texts")
            return all_embeddings
            
        except Exception as e:
            logger.error(f"❌ Error generating embeddings: {e}")
            raise
    
    def _get_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for a batch of texts"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "input": texts,
            "model": self.model
        }
        
        try:
            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            embeddings = [item['embedding'] for item in data['data']]
            
            return embeddings
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ API request failed: {e}")
            raise
        except KeyError as e:
            logger.error(f"❌ Unexpected API response format: {e}")
            raise
    
    def get_single_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text"""
        embeddings = self.get_embeddings([text])
        return embeddings[0] if embeddings else []
    
    def test_connection(self) -> bool:
        """Test connection to Voyage AI API"""
        try:
            test_embedding = self.get_single_embedding("test")
            if test_embedding and len(test_embedding) > 0:
                logger.info("✅ Voyage AI API connection successful")
                return True
            else:
                logger.error("❌ Voyage AI API returned empty embedding")
                return False
                
        except Exception as e:
            logger.error(f"❌ Voyage AI API connection failed: {e}")
            return False
