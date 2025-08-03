import mlflow
import mlflow.sklearn
import mlflow.pytorch
from mlflow.tracking import MlflowClient
import bentoml
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from sklearn.metrics import accuracy_score, precision_score, recall_score
import joblib
from datetime import datetime
import logging

class FinancialMLOps:
    """
    MLOps pipeline for financial ML models
    """
    
    def __init__(self):
        mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
        mlflow.set_experiment(settings.MLFLOW_EXPERIMENT_NAME)
        self.client = MlflowClient()
    
    def log_model_performance(self, model_name: str, predictions: np.ndarray, 
                            actual: np.ndarray, metadata: Dict):
        """Log model performance metrics"""
        with mlflow.start_run(run_name=f"{model_name}_{datetime.now().strftime('%Y%m%d_%H%M')}"):
            # Calculate metrics
            accuracy = accuracy_score(actual, predictions)
            precision = precision_score(actual, predictions, average='weighted')
            recall = recall_score(actual, predictions, average='weighted')
            
            # Log metrics
            mlflow.log_metric("accuracy", accuracy)
            mlflow.log_metric("precision", precision)
            mlflow.log_metric("recall", recall)
            
            # Log parameters
            for key, value in metadata.items():
                mlflow.log_param(key, value)
            
            # Log additional financial metrics
            if "returns" in metadata:
                returns = metadata["returns"]
                mlflow.log_metric("sharpe_ratio", self._calculate_sharpe(returns))
                mlflow.log_metric("max_drawdown", self._calculate_max_drawdown(returns))
    
    def deploy_model_bentoml(self, model, model_name: str, model_type: str = "sklearn"):
        """Deploy model using BentoML"""
        
        @bentoml.service
        class FinancialPredictionService:
            def __init__(self):
                self.model = model
                self.model_name = model_name
            
            @bentoml.api
            def predict(self, input_data: Dict) -> Dict:
                """Make financial predictions"""
                try:
                    if model_type == "sklearn":
                        features = np.array(input_data["features"]).reshape(1, -1)
                        prediction = self.model.predict(features)[0]
                        probability = None
                        
                        if hasattr(self.model, "predict_proba"):
                            probability = self.model.predict_proba(features)[0].tolist()
                    
                    return {
                        "prediction": float(prediction),
                        "probability": probability,
                        "model_name": self.model_name,
                        "timestamp": datetime.now().isoformat()
                    }
                except Exception as e:
                    return {"error": str(e)}
            
            @bentoml.api
            def health_check(self) -> Dict:
                return {"status": "healthy", "model": self.model_name}
        
        # Save model to BentoML
        bentoml.sklearn.save_model(model_name, model)
        
        return FinancialPredictionService()
    
    def setup_ab_testing(self, model_a_name: str, model_b_name: str, traffic_split: float = 0.5):
        """Setup A/B testing for trading strategies"""
        
        class ABTestingService:
            def __init__(self):
                self.model_a = mlflow.sklearn.load_model(f"models:/{model_a_name}/latest")
                self.model_b = mlflow.sklearn.load_model(f"models:/{model_b_name}/latest")
                self.traffic_split = traffic_split
                self.test_results = {"model_a": [], "model_b": []}
            
            def predict(self, features: np.ndarray) -> Dict:
                """Route traffic between models for A/B testing"""
                import random
                
                use_model_a = random.random() < self.traffic_split
                
                if use_model_a:
                    prediction = self.model_a.predict(features)[0]
                    model_used = "model_a"
                else:
                    prediction = self.model_b.predict(features)[0]
                    model_used = "model_b"
                
                # Log for analysis
                self.test_results[model_used].append({
                    "prediction": prediction,
                    "timestamp": datetime.now().isoformat(),
                    "features": features.tolist()
                })
                
                return {
                    "prediction": float(prediction),
                    "model_used": model_used,
                    "test_id": len(self.test_results[model_used])
                }
            
            def get_test_results(self) -> Dict:
                """Get A/B test performance comparison"""
                return {
                    "model_a_predictions": len(self.test_results["model_a"]),
                    "model_b_predictions": len(self.test_results["model_b"]),
                    "traffic_split": self.traffic_split
                }
        
        return ABTestingService()
    
    def monitor_model_drift(self, model_name: str, new_data: pd.DataFrame, 
                          reference_data: pd.DataFrame) -> Dict:
        """Monitor for model drift"""
        from scipy import stats
        
        drift_results = {}
        
        for column in new_data.columns:
            if column in reference_data.columns:
                # Kolmogorov-Smirnov test for distribution drift
                ks_stat, p_value = stats.ks_2samp(reference_data[column], new_data[column])
                
                drift_results[column] = {
                    "ks_statistic": ks_stat,
                    "p_value": p_value,
                    "drift_detected": p_value < 0.05,
                    "drift_severity": "high" if ks_stat > 0.2 else "medium" if ks_stat > 0.1 else "low"
                }
        
        # Log drift metrics to MLflow
        with mlflow.start_run(run_name=f"drift_check_{model_name}_{datetime.now().strftime('%Y%m%d')}"):
            for column, metrics in drift_results.items():
                mlflow.log_metric(f"{column}_ks_stat", metrics["ks_statistic"])
                mlflow.log_metric(f"{column}_p_value", metrics["p_value"])
        
        return drift_results
    
    def automated_retraining_pipeline(self, model_name: str, trigger_threshold: float = 0.05):
        """Setup automated retraining when performance degrades"""
        
        def check_and_retrain():
            # Get latest model performance
            latest_run = self.client.search_runs(
                experiment_ids=[mlflow.get_experiment_by_name(settings.MLFLOW_EXPERIMENT_NAME).experiment_id],
                filter_string=f"tags.model_name = '{model_name}'",
                order_by=["start_time DESC"],
                max_results=1
            )[0]
            
            current_accuracy = latest_run.data.metrics.get("accuracy", 0)
            
            # Check if retraining is needed
            if current_accuracy < trigger_threshold:
                logging.info(f"Triggering retraining for {model_name} (accuracy: {current_accuracy})")
                # Trigger retraining workflow (e.g., via Airflow DAG)
                return True
            
            return False
        
        return check_and_retrain
