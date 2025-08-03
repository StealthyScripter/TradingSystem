from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    AutoModelForTokenClassification, pipeline
)
import torch
from typing import List, Dict, Any
import mlflow
import mlflow.transformers

class FinancialTransformers:
    """
    HuggingFace Transformers for financial NLP tasks
    """
    
    def __init__(self):
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="ProsusAI/finbert",
            tokenizer="ProsusAI/finbert"
        )
        
        self.ner_pipeline = pipeline(
            "ner",
            model="dbmdz/bert-large-cased-finetuned-conll03-english",
            aggregation_strategy="simple"
        )
        
        # Load custom fine-tuned models if available
        self._load_custom_models()
    
    def _load_custom_models(self):
        """Load custom fine-tuned models from MLflow"""
        try:
            # Load latest financial sentiment model
            self.custom_sentiment = mlflow.transformers.load_model(
                f"models:/{settings.MLFLOW_EXPERIMENT_NAME}_sentiment/latest"
            )
        except Exception:
            self.custom_sentiment = None
    
    def analyze_sentiment(self, texts: List[str]) -> List[Dict]:
        """Analyze sentiment of financial texts"""
        results = []
        
        for text in texts:
            # Use FinBERT for financial sentiment
            sentiment = self.sentiment_analyzer(text)[0]
            
            # Map FinBERT labels to standard format
            label_mapping = {"positive": "bullish", "negative": "bearish", "neutral": "neutral"}
            
            results.append({
                "text": text,
                "sentiment": label_mapping.get(sentiment["label"].lower(), sentiment["label"]),
                "confidence": sentiment["score"],
                "model": "finbert"
            })
        
        return results
    
    def extract_entities(self, texts: List[str]) -> List[Dict]:
        """Extract financial entities (companies, metrics, events)"""
        results = []
        
        for text in texts:
            entities = self.ner_pipeline(text)
            
            # Filter and categorize financial entities
            financial_entities = {
                "companies": [],
                "persons": [],
                "metrics": [],
                "locations": [],
                "dates": []
            }
            
            for entity in entities:
                entity_type = entity["entity_group"]
                if entity_type in ["ORG"]:
                    financial_entities["companies"].append({
                        "text": entity["word"],
                        "confidence": entity["score"]
                    })
                elif entity_type in ["PER"]:
                    financial_entities["persons"].append({
                        "text": entity["word"],
                        "confidence": entity["score"]
                    })
                elif entity_type in ["LOC"]:
                    financial_entities["locations"].append({
                        "text": entity["word"],
                        "confidence": entity["score"]
                    })
            
            results.append({
                "text": text,
                "entities": financial_entities
            })
        
        return results
    
    def fine_tune_model(self, training_data: List[Dict], model_name: str, task: str):
        """Fine-tune models on financial data"""
        # Implementation for fine-tuning on financial news, earnings calls, SEC filings
        with mlflow.start_run():
            mlflow.log_param("model_name", model_name)
            mlflow.log_param("task", task)
            mlflow.log_param("training_samples", len(training_data))
            
            # Fine-tuning logic here
            # Log model to MLflow for versioning
            mlflow.transformers.log_model(
                transformers_model=None,  # Your fine-tuned model
                artifact_path=f"financial_{task}_model"
            )
