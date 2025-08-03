from langchain.chains import RetrievalQAWithSourcesChain, LLMChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain.llms import Ollama
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langsmith import Client
from typing import Dict, List, Any, Optional
import asyncio

class FinancialAnalysisOrchestrator:
    """
    LangChain orchestration for complex financial analysis workflows
    """
    
    def __init__(self):
        # Initialize Ollama LLM
        self.llm = Ollama(
            base_url=settings.OLLAMA_BASE_URL,
            model="llama3.1:8b"
        )
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.DEFAULT_EMBEDDING_MODEL
        )
        
        # Conversation memory for iterative discussions
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=10
        )
        
        # LangSmith for monitoring
        self.langsmith_client = Client()
        
        # Initialize vector store
        self.vector_store = None
        
        # Initialize analysis chains
        self._setup_analysis_chains()
    
    def _setup_analysis_chains(self):
        """Setup different analysis chains for various tasks"""
        
        # Risk Assessment Chain
        risk_prompt = PromptTemplate(
            input_variables=["portfolio_data", "market_context"],
            template="""
            Analyze the risk profile of this investment portfolio:
            
            Portfolio Data: {portfolio_data}
            Market Context: {market_context}
            
            Provide a comprehensive risk assessment including:
            1. Overall risk level (Low/Medium/High)
            2. Key risk factors
            3. Diversification analysis
            4. Recommended risk mitigation strategies
            5. Risk-adjusted return expectations
            
            Risk Assessment:
            """
        )
        
        self.risk_chain = LLMChain(
            llm=self.llm,
            prompt=risk_prompt,
            memory=self.memory
        )
        
        # Market Analysis Chain
        market_prompt = PromptTemplate(
            input_variables=["market_data", "news_sentiment", "economic_indicators"],
            template="""
            Perform a comprehensive market analysis:
            
            Market Data: {market_data}
            News Sentiment: {news_sentiment}
            Economic Indicators: {economic_indicators}
            
            Provide analysis on:
            1. Current market trends and direction
            2. Sector-specific insights
            3. Impact of recent news and sentiment
            4. Economic indicator implications
            5. Investment opportunities and risks
            
            Market Analysis:
            """
        )
        
        self.market_chain = LLMChain(
            llm=self.llm,
            prompt=market_prompt,
            memory=self.memory
        )
        
        # Portfolio Optimization Chain
        optimization_prompt = PromptTemplate(
            input_variables=["current_portfolio", "risk_tolerance", "investment_goals", "market_outlook"],
            template="""
            Optimize this investment portfolio:
            
            Current Portfolio: {current_portfolio}
            Risk Tolerance: {risk_tolerance}
            Investment Goals: {investment_goals}
            Market Outlook: {market_outlook}
            
            Provide optimization recommendations:
            1. Asset allocation adjustments
            2. Individual security recommendations
            3. Timing considerations
            4. Risk management strategies
            5. Expected performance improvements
            
            Portfolio Optimization:
            """
        )
        
        self.optimization_chain = LLMChain(
            llm=self.llm,
            prompt=optimization_prompt,
            memory=self.memory
        )
    
    async def analyze_investment_opportunity(self, query: str, context_docs: List[Dict]) -> Dict:
        """
        Complex workflow: data retrieval → analysis → reasoning → recommendations
        """
        # Step 1: Retrieve relevant context
        retrieved_context = await self._retrieve_context(query, context_docs)
        
        # Step 2: Analyze sentiment and entities
        sentiment_analysis = await self._analyze_context_sentiment(retrieved_context)
        
        # Step 3: Perform financial analysis
        financial_analysis = await self._perform_financial_analysis(query, retrieved_context)
        
        # Step 4: Generate recommendations
        recommendations = await self._generate_recommendations(
            query, retrieved_context, sentiment_analysis, financial_analysis
        )
        
        # Log to LangSmith for monitoring
        self._log_to_langsmith("investment_analysis", {
            "query": query,
            "context_docs_count": len(context_docs),
            "recommendations": recommendations
        })
        
        return {
            "query": query,
            "retrieved_context": retrieved_context,
            "sentiment_analysis": sentiment_analysis,
            "financial_analysis": financial_analysis,
            "recommendations": recommendations,
            "conversation_id": self.memory.chat_memory.messages[-1].additional_kwargs.get("id")
        }
    
    async def _retrieve_context(self, query: str, docs: List[Dict]) -> List[Dict]:
        """Retrieve relevant documents using RAG"""
        if not self.vector_store:
            # Create vector store from documents
            texts = [doc["content"] for doc in docs]
            metadatas = [{k: v for k, v in doc.items() if k != "content"} for doc in docs]
            self.vector_store = FAISS.from_texts(texts, self.embeddings, metadatas=metadatas)
        
        # Retrieve similar documents
        similar_docs = self.vector_store.similarity_search_with_score(query, k=5)
        
        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "similarity_score": score
            }
            for doc, score in similar_docs
        ]
    
    async def _analyze_context_sentiment(self, context_docs: List[Dict]) -> Dict:
        """Analyze sentiment of retrieved context"""
        transformers = FinancialTransformers()
        texts = [doc["content"] for doc in context_docs]
        
        sentiment_results = transformers.analyze_sentiment(texts)
        entity_results = transformers.extract_entities(texts)
        
        # Aggregate sentiment
        sentiments = [r["sentiment"] for r in sentiment_results]
        bullish_count = sentiments.count("bullish")
        bearish_count = sentiments.count("bearish")
        neutral_count = sentiments.count("neutral")
        
        overall_sentiment = "neutral"
        if bullish_count > bearish_count:
            overall_sentiment = "bullish"
        elif bearish_count > bullish_count:
            overall_sentiment = "bearish"
        
        return {
            "overall_sentiment": overall_sentiment,
            "sentiment_breakdown": {
                "bullish": bullish_count,
                "bearish": bearish_count,
                "neutral": neutral_count
            },
            "detailed_results": sentiment_results,
            "entities": entity_results
        }
    
    async def _perform_financial_analysis(self, query: str, context: List[Dict]) -> Dict:
        """Perform detailed financial analysis"""
        # This would integrate with the risk calculator from earlier
        from ..services.risk_reward import RiskRewardAnalyzer
        
        # Extract financial metrics from context
        financial_data = self._extract_financial_metrics(context)
        
        # Perform risk-reward analysis if we have portfolio data
        risk_analysis = None
        if "portfolio" in query.lower():
            # Run portfolio analysis
            risk_analysis = await self._run_portfolio_analysis(financial_data)
        
        return {
            "financial_metrics": financial_data,
            "risk_analysis": risk_analysis,
            "market_indicators": self._extract_market_indicators(context)
        }
    
    async def _generate_recommendations(self, query: str, context: List[Dict], 
                                      sentiment: Dict, financial: Dict) -> Dict:
        """Generate final investment recommendations"""
        
        # Combine all analysis for comprehensive recommendation
        combined_context = {
            "query": query,
            "sentiment_analysis": sentiment,
            "financial_analysis": financial,
            "context_summary": self._summarize_context(context)
        }
        
        # Use appropriate chain based on query type
        if "risk" in query.lower():
            result = await self.risk_chain.arun(**combined_context)
        elif "market" in query.lower():
            result = await self.market_chain.arun(**combined_context)
        elif "portfolio" in query.lower() or "optimize" in query.lower():
            result = await self.optimization_chain.arun(**combined_context)
        else:
            # General investment analysis
            result = await self._general_analysis(combined_context)
        
        return {
            "recommendation_text": result,
            "confidence_score": self._calculate_confidence(sentiment, financial),
            "risk_level": self._assess_risk_level(financial),
            "action_items": self._extract_action_items(result)
        }
    
    def _log_to_langsmith(self, operation: str, data: Dict):
        """Log operation to LangSmith for monitoring"""
        try:
            self.langsmith_client.create_run(
                name=operation,
                inputs=data,
                run_type="chain"
            )
        except Exception as e:
            print(f"LangSmith logging failed: {e}")
