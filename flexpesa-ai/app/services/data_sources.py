import yfinance as yf
import requests
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime, timedelta
import logging

class FinancialDataSources:
    """
    Integration with multiple financial data sources
    """
    
    def __init__(self):
        self.alpha_vantage_key = settings.ALPHA_VANTAGE_API_KEY
        self.polygon_key = settings.POLYGON_API_KEY
        self.news_api_key = settings.NEWS_API_KEY
        self.twitter_token = settings.TWITTER_BEARER_TOKEN
    
    async def get_sec_filings(self, cik: str, filing_type: str = "10-K") -> List[Dict]:
        """Fetch SEC filings for company analysis"""
        base_url = "https://data.sec.gov/submissions"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{base_url}/CIK{cik.zfill(10)}.json") as response:
                    data = await response.json()
                    
                    filings = []
                    recent_filings = data.get("filings", {}).get("recent", {})
                    
                    for i, form in enumerate(recent_filings.get("form", [])):
                        if form == filing_type:
                            filings.append({
                                "form": form,
                                "filing_date": recent_filings["filingDate"][i],
                                "accession_number": recent_filings["accessionNumber"][i],
                                "primary_document": recent_filings["primaryDocument"][i]
                            })
                    
                    return filings[:10]  # Return last 10 filings
            except Exception as e:
                logging.error(f"Error fetching SEC filings: {e}")
                return []
    
    async def get_earnings_reports(self, symbol: str) -> List[Dict]:
        """Fetch earnings reports and analyst notes"""
        try:
            stock = yf.Ticker(symbol)
            
            # Get earnings data
            earnings = stock.earnings_dates
            if earnings is not None:
                return [
                    {
                        "date": date.isoformat(),
                        "eps_estimate": row.get("EPS Estimate"),
                        "reported_eps": row.get("Reported EPS"),
                        "surprise_percent": row.get("Surprise(%)"),
                        "symbol": symbol
                    }
                    for date, row in earnings.head(10).iterrows()
                ]
            return []
        except Exception as e:
            logging.error(f"Error fetching earnings for {symbol}: {e}")
            return []
    
    async def get_financial_news(self, query: str, days_back: int = 7) -> List[Dict]:
        """Fetch financial news from multiple sources"""
        if not self.news_api_key:
            return []
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "domains": "reuters.com,bloomberg.com,cnbc.com,marketwatch.com",
            "from": start_date.isoformat(),
            "to": end_date.isoformat(),
            "sortBy": "relevancy",
            "apiKey": self.news_api_key
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params) as response:
                    data = await response.json()
                    
                    articles = []
                    for article in data.get("articles", [])[:20]:
                        articles.append({
                            "title": article["title"],
                            "description": article["description"],
                            "content": article["content"],
                            "url": article["url"],
                            "published_at": article["publishedAt"],
                            "source": article["source"]["name"]
                        })
                    
                    return articles
            except Exception as e:
                logging.error(f"Error fetching news: {e}")
                return []
    
    async def get_social_sentiment(self, symbol: str) -> List[Dict]:
        """Fetch social media sentiment data"""
        if not self.twitter_token:
            return []
        
        # Twitter API v2 search
        url = "https://api.twitter.com/2/tweets/search/recent"
        headers = {"Authorization": f"Bearer {self.twitter_token}"}
        params = {
            "query": f"${symbol} OR {symbol}",
            "max_results": 100,
            "tweet.fields": "created_at,public_metrics,context_annotations"
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers, params=params) as response:
                    data = await response.json()
                    
                    tweets = []
                    for tweet in data.get("data", []):
                        tweets.append({
                            "text": tweet["text"],
                            "created_at": tweet["created_at"],
                            "retweet_count": tweet["public_metrics"]["retweet_count"],
                            "like_count": tweet["public_metrics"]["like_count"],
                            "symbol": symbol
                        })
                    
                    return tweets
            except Exception as e:
                logging.error(f"Error fetching social sentiment: {e}")
                return []
    
    async def get_market_data(self, symbols: List[str], period: str = "1y") -> pd.DataFrame:
        """Fetch comprehensive market data"""
        try:
            data = yf.download(symbols, period=period, auto_adjust=True, group_by='ticker')
            return data
        except Exception as e:
            logging.error(f"Error fetching market data: {e}")
            return pd.DataFrame()
    
    async def get_economic_indicators(self) -> Dict:
        """Fetch key economic indicators"""
        indicators = {}
        
        try:
            # Fetch key indices
            indices = ["^GSPC", "^DJI", "^IXIC", "^TNX"]  # S&P500, Dow, NASDAQ, 10Y Treasury
            index_data = yf.download(indices, period="5d", auto_adjust=True)
            
            for index in indices:
                if index in index_data['Close'].columns:
                    current = index_data['Close'][index].iloc[-1]
                    previous = index_data['Close'][index].iloc[-2]
                    change = ((current - previous) / previous) * 100
                    
                    indicators[index] = {
                        "current_value": float(current),
                        "daily_change": float(change),
                        "symbol": index
                    }
        
        except Exception as e:
            logging.error(f"Error fetching economic indicators: {e}")
        
        return indicators
