import pandas as pd
import numpy as np
import requests
import logging  
from typing import Dict, List
from datetime import datetime, timedelta

class SimpleAIService:
    """Basic AI analysis without complex ML infrastructure"""

    def __init__(self, news_api_key: str = None):
        self.news_api_key = news_api_key

    def analyze_portfolio(self, accounts_data: List[Dict]) -> Dict:
        """Simple portfolio analysis"""
        total_value = sum(account['balance'] for account in accounts_data)

        # Simple risk calculation based on portfolio diversity
        num_assets = sum(len(account.get('assets', [])) for account in accounts_data)
        diversity_score = min(num_assets / 10, 1.0)  # More assets = less risk

        # Basic recommendation logic
        if diversity_score < 0.3:
            recommendation = "DIVERSIFY"
            confidence = 0.8
        elif total_value < 50000:
            recommendation = "ACCUMULATE"
            confidence = 0.7
        else:
            recommendation = "HOLD"
            confidence = 0.6

        return {
            "total_value": total_value,
            "diversity_score": diversity_score,
            "risk_score": (1 - diversity_score) * 10,
            "recommendation": recommendation,
            "confidence": confidence,
            "insights": [
                f"Portfolio spans {len(accounts_data)} accounts",
                f"Total of {num_assets} different assets",
                f"Diversity score: {diversity_score:.1%}"
            ]
        }

    def get_basic_sentiment(self, symbol: str) -> Dict:
        """Basic sentiment analysis using news (if API key available)"""
        if not self.news_api_key:
            # Return mock sentiment for MVP
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "sources": ["Mock data - Add NEWS_API_KEY for real sentiment"]
            }

        try:
            # Simple news sentiment
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": symbol,
                "sortBy": "relevancy",
                "pageSize": 10,
                "apiKey": self.news_api_key,
                "from": (datetime.now() - timedelta(days=7)).isoformat()
            }

            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                articles = response.json().get("articles", [])

                # Simple sentiment scoring
                positive_words = ["buy", "bull", "up", "gain", "profit", "growth", "strong"]
                negative_words = ["sell", "bear", "down", "loss", "decline", "weak", "fall"]

                sentiment_score = 0
                for article in articles:
                    text = (article.get("title", "") + " " + article.get("description", "")).lower()
                    sentiment_score += sum(1 for word in positive_words if word in text)
                    sentiment_score -= sum(1 for word in negative_words if word in text)

                if sentiment_score > 0:
                    sentiment = "bullish"
                elif sentiment_score < 0:
                    sentiment = "bearish"
                else:
                    sentiment = "neutral"

                return {
                    "sentiment": sentiment,
                    "confidence": min(abs(sentiment_score) / 10, 1.0),
                    "sources": [f"{len(articles)} recent news articles"]
                }
        except Exception as e:
            logging.error(f"Sentiment analysis error: {e}")

        return {"sentiment": "neutral", "confidence": 0.5, "sources": ["Error fetching news"]}