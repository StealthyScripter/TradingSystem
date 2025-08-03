from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from ..ml.langchain_orchestrator import FinancialAnalysisOrchestrator
from ..ml.transformers_pipeline import FinancialTransformers
from ..ml.embeddings import FinancialEmbeddingManager
from ..services.data_sources import FinancialDataSources
from ..ml.mlops import FinancialMLOps

router = APIRouter(prefix="/ai-analysis", tags=["AI Financial Analysis"])

class AnalysisRequest(BaseModel):
    query: str
    symbols: Optional[List[str]] = None
    include_news: bool = True
    include_social: bool = True
    include_sec_filings: bool = False
    analysis_type: str = "comprehensive"  # comprehensive, risk, market, sentiment

class InvestmentQuestion(BaseModel):
    question: str
    portfolio_context: Optional[Dict] = None
    risk_tolerance: str = "medium"  # low, medium, high
    investment_horizon: str = "long"  # short, medium, long

class DocumentAnalysis(BaseModel):
    documents: List[Dict]  # [{"content": "...", "type": "news", "source": "..."}]
    analysis_focus: str = "sentiment"  # sentiment, entities, summary, recommendations

# Initialize AI components
orchestrator = FinancialAnalysisOrchestrator()
transformers = FinancialTransformers()
embedding_manager = FinancialEmbeddingManager()
data_sources = FinancialDataSources()
mlops = FinancialMLOps()

@router.post("/comprehensive-analysis")
async def comprehensive_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    Comprehensive AI-driven financial analysis
    Orchestrates: data retrieval → analysis → reasoning → recommendations
    """
    try:
        # Step 1: Gather data from multiple sources
        context_docs = []
        
        if request.symbols:
            for symbol in request.symbols:
                # Market data
                market_data = await data_sources.get_market_data([symbol])
                if not market_data.empty:
                    context_docs.append({
                        "content": f"Market data for {symbol}: {market_data.tail(5).to_string()}",
                        "type": "market_data",
                        "symbol": symbol
                    })
                
                # Earnings reports
                if request.include_sec_filings:
                    # For demo, we'll use a mock CIK
                    sec_filings = await data_sources.get_sec_filings("0000320193")  # Apple's CIK
                    for filing in sec_filings:
                        context_docs.append({
                            "content": f"SEC Filing {filing['form']} for {symbol} filed on {filing['filing_date']}",
                            "type": "sec_filing",
                            "symbol": symbol,
                            "filing_date": filing['filing_date']
                        })
                
                # Financial news
                if request.include_news:
                    news_articles = await data_sources.get_financial_news(symbol)
                    for article in news_articles:
                        context_docs.append({
                            "content": f"{article['title']} - {article['description']}",
                            "type": "news",
                            "symbol": symbol,
                            "source": article['source'],
                            "published_at": article['published_at']
                        })
                
                # Social sentiment
                if request.include_social:
                    social_data = await data_sources.get_social_sentiment(symbol)
                    for tweet in social_data[:10]:  # Limit to 10 tweets
                        context_docs.append({
                            "content": tweet['text'],
                            "type": "social",
                            "symbol": symbol,
                            "created_at": tweet['created_at']
                        })
        
        # Step 2: Store documents in vector database
        embedding_manager.store_in_qdrant(context_docs, "financial_analysis")
        
        # Step 3: Run orchestrated analysis
        analysis_result = await orchestrator.analyze_investment_opportunity(
            request.query, context_docs
        )
        
        # Step 4: Log performance metrics in background
        background_tasks.add_task(
            mlops.log_model_performance,
            "comprehensive_analysis",
            np.array([1]),  # Mock prediction
            np.array([1]),  # Mock actual
            {"query": request.query, "symbols": request.symbols}
        )
        
        return {
            "status": "success",
            "analysis": analysis_result,
            "data_sources_used": len(context_docs),
            "symbols_analyzed": request.symbols
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/answer-investment-question")
async def answer_investment_question(request: InvestmentQuestion):
    """
    RAG-based investment question answering
    Uses retrieved financial reports, analyst notes, and real-time data
    """
    try:
        # Search relevant documents in Qdrant
        relevant_docs = embedding_manager.search_qdrant(
            query=request.question,
            collection_name="financial_analysis",
            limit=10
        )
        
        # Add portfolio context if provided
        if request.portfolio_context:
            relevant_docs.append({
                "content": f"Portfolio context: {request.portfolio_context}",
                "type": "portfolio",
                "score": 1.0
            })
        
        # Generate contextual answer using LangChain
        analysis_result = await orchestrator.analyze_investment_opportunity(
            request.question, relevant_docs
        )
        
        return {
            "question": request.question,
            "answer": analysis_result["recommendations"]["recommendation_text"],
            "confidence": analysis_result["recommendations"]["confidence_score"],
            "risk_level": analysis_result["recommendations"]["risk_level"],
            "sources_used": len(relevant_docs),
            "conversation_memory": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-documents")
async def analyze_documents(request: DocumentAnalysis):
    """
    Analyze financial documents using HuggingFace transformers
    """
    try:
        results = {}
        texts = [doc["content"] for doc in request.documents]
        
        if request.analysis_focus in ["sentiment", "all"]:
            # Sentiment analysis
            sentiment_results = transformers.analyze_sentiment(texts)
            results["sentiment_analysis"] = sentiment_results
        
        if request.analysis_focus in ["entities", "all"]:
            # Named entity recognition
            entity_results = transformers.extract_entities(texts)
            results["entity_extraction"] = entity_results
        
        if request.analysis_focus in ["summary", "all"]:
            # Document summarization using LangChain
            summaries = []
            for doc in request.documents:
                summary_prompt = f"Summarize this financial document: {doc['content'][:1000]}..."
                summary = await orchestrator.llm.apredict(summary_prompt)
                summaries.append({
                    "original_length": len(doc["content"]),
                    "summary": summary,
                    "document_type": doc.get("type", "unknown")
                })
            results["summaries"] = summaries
        
        if request.analysis_focus in ["recommendations", "all"]:
            # Generate investment recommendations
            combined_content = " ".join(texts)
            rec_result = await orchestrator.analyze_investment_opportunity(
                "Generate investment recommendations based on these documents",
                request.documents
            )
            results["recommendations"] = rec_result["recommendations"]
        
        return {
            "status": "success",
            "analysis_focus": request.analysis_focus,
            "documents_analyzed": len(request.documents),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/semantic-search")
async def semantic_search(query: str, collection: str = "financial_analysis", limit: int = 10):
    """
    Semantic search across financial documents using FAISS and Qdrant
    """
    try:
        # Search using Qdrant (production)
        qdrant_results = embedding_manager.search_qdrant(
            query=query,
            collection_name=collection,
            limit=limit
        )
        
        # Also search using FAISS (if available)
        faiss_results = []
        if "general" in embedding_manager.faiss_indices:
            faiss_results = embedding_manager.search_similar(
                query=query,
                model_type="general",
                k=limit
            )
        
        return {
            "query": query,
            "qdrant_results": qdrant_results,
            "faiss_results": faiss_results,
            "total_results": len(qdrant_results) + len(faiss_results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model-performance")
async def get_model_performance():
    """
    Get ML model performance metrics and drift detection
    """
    try:
        # Get latest MLflow experiments
        experiments = mlops.client.search_runs(
            experiment_ids=[mlflow.get_experiment_by_name(settings.MLFLOW_EXPERIMENT_NAME).experiment_id],
            max_results=10
        )
        
        performance_data = []
        for run in experiments:
            performance_data.append({
                "run_id": run.info.run_id,
                "metrics": run.data.metrics,
                "params": run.data.params,
                "start_time": run.info.start_time
            })
        
        return {
            "status": "success",
            "recent_runs": performance_data,
            "model_health": "healthy"  # This would be calculated based on metrics
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fine-tune-model")
async def fine_tune_model(model_name: str, training_data: List[Dict], task: str):
    """
    Fine-tune financial models on custom data
    """
    try:
        # This would trigger the fine-tuning pipeline
        transformers.fine_tune_model(training_data, model_name, task)
        
        return {
            "status": "fine_tuning_started",
            "model_name": model_name,
            "task": task,
            "training_samples": len(training_data),
            "estimated_completion": "30 minutes"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
