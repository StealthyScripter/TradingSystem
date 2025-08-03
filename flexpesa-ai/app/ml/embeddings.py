import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple, Optional
import pickle
import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import hashlib

class FinancialEmbeddingManager:
    """
    Multi-model embedding strategy for financial documents
    Supports both FAISS and Qdrant for different use cases
    """
    
    def __init__(self):
        self.models = {
            "general": SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2"),
            "financial": SentenceTransformer("sentence-transformers/all-mpnet-base-v2"),
            "news": SentenceTransformer("sentence-transformers/paraphrase-MiniLM-L6-v2")
        }
        
        # FAISS indices for fast similarity search
        self.faiss_indices = {}
        self.document_store = {}
        
        # Qdrant client for production vector search
        self.qdrant_client = QdrantClient(url=settings.QDRANT_URL)
        self._initialize_collections()
    
    def _initialize_collections(self):
        """Initialize Qdrant collections for different document types"""
        collections = [
            "financial_reports", "news_articles", "social_sentiment", 
            "market_analysis", "company_profiles"
        ]
        
        for collection_name in collections:
            try:
                self.qdrant_client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                )
            except Exception:
                pass  # Collection already exists
    
    def create_embeddings(self, texts: List[str], model_type: str = "general") -> np.ndarray:
        """Create embeddings using specified model"""
        model = self.models[model_type]
        return model.encode(texts)
    
    def build_faiss_index(self, documents: List[Dict], model_type: str = "general"):
        """Build FAISS index for fast similarity search"""
        texts = [doc["text"] for doc in documents]
        embeddings = self.create_embeddings(texts, model_type)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        index.add(embeddings.astype('float32'))
        
        self.faiss_indices[model_type] = index
        self.document_store[model_type] = documents
        
        return index
    
    def search_similar(self, query: str, model_type: str = "general", k: int = 5) -> List[Dict]:
        """Find similar documents using FAISS"""
        query_embedding = self.create_embeddings([query], model_type)
        faiss.normalize_L2(query_embedding)
        
        index = self.faiss_indices[model_type]
        scores, indices = index.search(query_embedding.astype('float32'), k)
        
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx != -1:  # Valid result
                doc = self.document_store[model_type][idx].copy()
                doc["similarity_score"] = float(score)
                results.append(doc)
        
        return results
    
    def store_in_qdrant(self, documents: List[Dict], collection_name: str, model_type: str = "general"):
        """Store documents in Qdrant for production vector search"""
        texts = [doc["text"] for doc in documents]
        embeddings = self.create_embeddings(texts, model_type)
        
        points = []
        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            point_id = hashlib.md5(doc["text"].encode()).hexdigest()
            points.append(PointStruct(
                id=point_id,
                vector=embedding.tolist(),
                payload=doc
            ))
        
        self.qdrant_client.upsert(collection_name=collection_name, points=points)
    
    def search_qdrant(self, query: str, collection_name: str, model_type: str = "general", 
                     limit: int = 5, filters: Optional[Dict] = None) -> List[Dict]:
        """Search Qdrant for similar documents with filtering"""
        query_embedding = self.create_embeddings([query], model_type)[0]
        
        results = self.qdrant_client.search(
            collection_name=collection_name,
            query_vector=query_embedding.tolist(),
            limit=limit,
            query_filter=filters
        )
        
        return [{"score": result.score, **result.payload} for result in results]
