import pandas as pd
import numpy as np
import requests
import logging
import asyncio
import aiohttp
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import re
from dataclasses import dataclass

@dataclass
class TechnicalIndicators:
    """Lightweight technical indicators"""
    rsi: float
    sma_20: float
    sma_50: float
    volatility: float
    momentum: float
    price_change_5d: float
    price_change_20d: float

@dataclass
class SentimentData:
    """Lightweight sentiment analysis"""
    sentiment_score: float  # -1 to 1
    confidence: float
    news_count: int
    keyword_score: float

class LightweightAIService:
    """Fast, minimal-dependency AI service for portfolio analysis"""

    def __init__(self, news_api_key: Optional[str] = None):
        self.news_api_key = news_api_key
        self.logger = logging.getLogger(__name__)

        # Lightweight sentiment keywords (no NLTK needed)
        self.bullish_patterns = [
            r'\b(surge|rally|breakout|bullish|upgrade|beat|outperform|strong|growth|positive|gains|soar|climb|rise)\b',
            r'\b(buy.{0,20}rating|price.{0,10}target.{0,10}raised|earnings.{0,10}beat|revenue.{0,10}growth)\b'
        ]

        self.bearish_patterns = [
            r'\b(plunge|crash|bearish|downgrade|miss|underperform|weak|decline|negative|losses|fall|drop|slide)\b',
            r'\b(sell.{0,20}rating|price.{0,10}target.{0,10}cut|earnings.{0,10}miss|revenue.{0,10}decline)\b'
        ]

        # Compile patterns for speed
        self.bullish_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.bullish_patterns]
        self.bearish_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.bearish_patterns]

    async def analyze_portfolio_fast(self, accounts_data: List[Dict]) -> Dict:
        """Fast portfolio analysis with essential metrics only"""
        try:
            # Extract portfolio data quickly
            all_symbols = []
            total_value = 0
            asset_values = {}

            for account in accounts_data:
                total_value += account.get('balance', 0)
                for asset in account.get('assets', []):
                    symbol = asset.get('symbol', '')
                    if symbol and symbol != 'UNKNOWN':
                        all_symbols.append(symbol)
                        asset_values[symbol] = asset.get('value', 0)

            if not all_symbols:
                return self._get_basic_analysis(accounts_data, total_value)

            # Run only essential analysis (parallel but limited)
            unique_symbols = list(set(all_symbols))[:10]  # Limit to top 10 for speed

            tasks = [
                self._get_basic_technical_batch(unique_symbols),
                self._get_basic_sentiment_batch(unique_symbols[:5]) if self.news_api_key else None
            ]

            # Filter out None tasks
            tasks = [task for task in tasks if task is not None]

            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                technical_data = results[0] if len(results) > 0 else {}
                sentiment_data = results[1] if len(results) > 1 else {}
            else:
                technical_data = {}
                sentiment_data = {}

            # Fast analysis compilation
            analysis = self._compile_fast_analysis(
                accounts_data, unique_symbols, asset_values, total_value,
                technical_data, sentiment_data
            )

            return analysis

        except Exception as e:
            self.logger.error(f"Fast analysis error: {e}")
            return self._get_basic_analysis(accounts_data, total_value)

    async def _get_basic_technical_batch(self, symbols: List[str]) -> Dict[str, TechnicalIndicators]:
        """Get basic technical indicators using only pandas/numpy"""
        technical_data = {}

        # Use yfinance (already in dependencies) for price data
        import yfinance as yf

        for symbol in symbols:
            try:
                # Get minimal data needed (faster)
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="3mo", interval="1d")  # Reduced period for speed

                if hist.empty or len(hist) < 20:
                    technical_data[symbol] = self._get_default_technical()
                    continue

                close_prices = hist['Close']

                # Calculate only essential indicators (fast operations)
                # RSI (simplified calculation)
                rsi = self._calculate_simple_rsi(close_prices, period=14)

                # Moving averages
                sma_20 = close_prices.tail(20).mean() if len(close_prices) >= 20 else close_prices.mean()
                sma_50 = close_prices.tail(50).mean() if len(close_prices) >= 50 else close_prices.mean()

                # Volatility (simplified)
                returns = close_prices.pct_change().dropna()
                volatility = returns.std() * np.sqrt(252) if len(returns) > 1 else 0.2

                # Momentum (price changes)
                current_price = close_prices.iloc[-1]
                momentum = ((current_price / close_prices.iloc[-10]) - 1) * 100 if len(close_prices) >= 10 else 0
                price_change_5d = ((current_price / close_prices.iloc[-5]) - 1) * 100 if len(close_prices) >= 5 else 0
                price_change_20d = ((current_price / close_prices.iloc[-20]) - 1) * 100 if len(close_prices) >= 20 else 0

                technical_data[symbol] = TechnicalIndicators(
                    rsi=rsi,
                    sma_20=sma_20,
                    sma_50=sma_50,
                    volatility=volatility,
                    momentum=momentum,
                    price_change_5d=price_change_5d,
                    price_change_20d=price_change_20d
                )

            except Exception as e:
                self.logger.warning(f"Technical analysis failed for {symbol}: {e}")
                technical_data[symbol] = self._get_default_technical()

        return technical_data

    def _calculate_simple_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Fast RSI calculation without external libraries"""
        if len(prices) < period + 1:
            return 50.0

        delta = prices.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.tail(period).mean()
        avg_loss = loss.tail(period).mean()

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    async def _get_basic_sentiment_batch(self, symbols: List[str]) -> Dict[str, SentimentData]:
        """Fast sentiment analysis using regex patterns"""
        if not self.news_api_key:
            return {}

        sentiment_data = {}

        # Use asyncio for concurrent requests but limit to avoid rate limits
        semaphore = asyncio.Semaphore(3)  # Max 3 concurrent requests

        async def analyze_symbol(symbol):
            async with semaphore:
                return await self._get_fast_sentiment(symbol)

        tasks = [analyze_symbol(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for symbol, result in zip(symbols, results):
            if isinstance(result, Exception):
                sentiment_data[symbol] = self._get_neutral_sentiment()
            else:
                sentiment_data[symbol] = result

        return sentiment_data

    async def _get_fast_sentiment(self, symbol: str) -> SentimentData:
        """Fast sentiment using regex pattern matching"""
        try:
            # Get recent news (limited for speed)
            articles = await self._fetch_news_fast(symbol, max_articles=10)

            if not articles:
                return self._get_neutral_sentiment()

            # Fast regex-based sentiment analysis
            total_bullish = 0
            total_bearish = 0

            for article in articles:
                title = article.get('title', '').lower()
                description = article.get('description', '').lower()
                content = f"{title} {description}"

                # Count pattern matches (fast)
                bullish_matches = sum(len(pattern.findall(content)) for pattern in self.bullish_regex)
                bearish_matches = sum(len(pattern.findall(content)) for pattern in self.bearish_regex)

                total_bullish += bullish_matches
                total_bearish += bearish_matches

            # Calculate sentiment score
            total_signals = total_bullish + total_bearish
            if total_signals == 0:
                sentiment_score = 0.0
                keyword_score = 0.0
            else:
                sentiment_score = (total_bullish - total_bearish) / total_signals
                keyword_score = total_signals / len(articles)

            # Confidence based on signal strength and article count
            confidence = min(0.9, (len(articles) / 20) + (keyword_score / 5))

            return SentimentData(
                sentiment_score=sentiment_score,
                confidence=confidence,
                news_count=len(articles),
                keyword_score=keyword_score
            )

        except Exception as e:
            self.logger.error(f"Fast sentiment analysis error for {symbol}: {e}")
            return self._get_neutral_sentiment()

    async def _fetch_news_fast(self, symbol: str, max_articles: int = 10) -> List[Dict]:
        """Fast, minimal news fetching"""
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": f'"{symbol}"',  # Exact symbol match for relevance
                "sortBy": "publishedAt",  # Latest first
                "pageSize": max_articles,
                "apiKey": self.news_api_key,
                "from": (datetime.now() - timedelta(days=3)).isoformat(),  # Only last 3 days
                "language": "en"
            }

            timeout = aiohttp.ClientTimeout(total=5)  # Fast timeout

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("articles", [])[:max_articles]
                    else:
                        return []

        except Exception as e:
            self.logger.warning(f"Fast news fetch failed for {symbol}: {e}")
            return []

    def _compile_fast_analysis(self, accounts_data: List[Dict], symbols: List[str],
                             asset_values: Dict[str, float], total_value: float,
                             technical_data: Dict, sentiment_data: Dict) -> Dict:
        """Compile analysis quickly with minimal computation"""

        # Basic metrics
        num_assets = len(symbols)
        num_accounts = len(accounts_data)
        diversity_score = min(num_assets / 10, 1.0)

        # Technical summary (fast aggregation)
        if technical_data:
            rsi_values = [t.rsi for t in technical_data.values() if hasattr(t, 'rsi')]
            momentum_values = [t.momentum for t in technical_data.values() if hasattr(t, 'momentum')]

            avg_rsi = np.mean(rsi_values) if rsi_values else 50.0
            avg_momentum = np.mean(momentum_values) if momentum_values else 0.0

            # Simple technical score
            technical_score = 0.0
            if avg_rsi < 30:
                technical_score += 0.5  # Oversold (bullish)
            elif avg_rsi > 70:
                technical_score -= 0.5  # Overbought (bearish)

            if avg_momentum > 5:
                technical_score += 0.5  # Positive momentum
            elif avg_momentum < -5:
                technical_score -= 0.5  # Negative momentum
        else:
            technical_score = 0.0
            avg_rsi = 50.0
            avg_momentum = 0.0

        # Sentiment summary
        if sentiment_data:
            sentiment_scores = [s.sentiment_score for s in sentiment_data.values()]
            avg_sentiment = np.mean(sentiment_scores) if sentiment_scores else 0.0
            sentiment_confidence = np.mean([s.confidence for s in sentiment_data.values()])
        else:
            avg_sentiment = 0.0
            sentiment_confidence = 0.3

        # Fast recommendation logic
        combined_score = (technical_score + avg_sentiment) / 2

        if combined_score > 0.3:
            recommendation = "ACCUMULATE"
        elif combined_score < -0.3:
            recommendation = "REDUCE_RISK"
        elif diversity_score < 0.4:
            recommendation = "DIVERSIFY"
        else:
            recommendation = "HOLD"

        # Simple risk score (no complex calculations)
        risk_score = (1 - diversity_score) * 5 + abs(avg_sentiment) * 5

        # Fast insights generation
        insights = self._generate_fast_insights(
            num_accounts, num_assets, total_value, avg_rsi,
            avg_momentum, avg_sentiment, technical_data
        )

        return {
            "total_value": total_value,
            "diversity_score": diversity_score,
            "risk_score": risk_score,
            "sentiment_score": avg_sentiment,
            "technical_score": technical_score,
            "recommendation": recommendation,
            "confidence": min(0.9, (sentiment_confidence + diversity_score) / 2),
            "insights": insights,
            "analysis_type": "lightweight",
            "symbols_analyzed": len(symbols),
            "performance": {
                "avg_rsi": avg_rsi,
                "avg_momentum": avg_momentum,
                "technical_signals": len([t for t in technical_data.values() if t.rsi < 30 or t.rsi > 70]),
                "news_coverage": sum([s.news_count for s in sentiment_data.values()]) if sentiment_data else 0
            }
        }

    def _generate_fast_insights(self, num_accounts: int, num_assets: int, total_value: float,
                              avg_rsi: float, avg_momentum: float, avg_sentiment: float,
                              technical_data: Dict) -> List[str]:
        """Generate insights quickly"""
        insights = []

        # Portfolio structure
        insights.append(f"Portfolio: {num_accounts} accounts, {num_assets} assets, ${total_value:,.0f}")

        # Technical insights
        if avg_rsi < 30:
            insights.append("Portfolio shows oversold conditions (potential buying opportunity)")
        elif avg_rsi > 70:
            insights.append("Portfolio shows overbought conditions (consider taking profits)")

        if avg_momentum > 10:
            insights.append(f"Strong positive momentum ({avg_momentum:.1f}%)")
        elif avg_momentum < -10:
            insights.append(f"Negative momentum detected ({avg_momentum:.1f}%)")

        # Sentiment insights
        if avg_sentiment > 0.3:
            insights.append("Positive news sentiment across holdings")
        elif avg_sentiment < -0.3:
            insights.append("Negative news sentiment - monitor closely")

        # Diversity insights
        if num_assets < 5:
            insights.append("Consider increasing diversification (< 5 assets)")
        elif num_assets > 20:
            insights.append("Well-diversified portfolio (20+ assets)")

        # Technical signals summary
        if technical_data:
            oversold_count = sum(1 for t in technical_data.values() if t.rsi < 30)
            if oversold_count > 0:
                insights.append(f"{oversold_count} assets potentially oversold")

        return insights[:5]  # Limit for performance

    # Helper methods (lightweight versions)
    def _get_basic_analysis(self, accounts_data: List[Dict], total_value: float) -> Dict:
        """Minimal fallback analysis"""
        num_assets = sum(len(account.get('assets', [])) for account in accounts_data)
        diversity_score = min(num_assets / 10, 1.0)

        return {
            "total_value": total_value,
            "diversity_score": diversity_score,
            "risk_score": (1 - diversity_score) * 5,
            "sentiment_score": 0.0,
            "technical_score": 0.0,
            "recommendation": "HOLD" if diversity_score > 0.5 else "DIVERSIFY",
            "confidence": 0.6,
            "insights": [
                f"Portfolio: {len(accounts_data)} accounts, {num_assets} assets",
                f"Diversity score: {diversity_score:.1%}",
                "Basic analysis - upgrade for enhanced features"
            ],
            "analysis_type": "basic"
        }

    def _get_default_technical(self) -> TechnicalIndicators:
        """Default technical values"""
        return TechnicalIndicators(
            rsi=50.0, sma_20=0.0, sma_50=0.0, volatility=0.2,
            momentum=0.0, price_change_5d=0.0, price_change_20d=0.0
        )

    def _get_neutral_sentiment(self) -> SentimentData:
        """Default neutral sentiment"""
        return SentimentData(
            sentiment_score=0.0, confidence=0.3,
            news_count=0, keyword_score=0.0
        )

    # Fast asset analysis method
    async def analyze_asset_fast(self, symbol: str) -> Dict:
        """Fast analysis for single asset"""
        try:
            # Run technical and sentiment in parallel
            tasks = [
                self._get_basic_technical_batch([symbol]),
                self._get_fast_sentiment(symbol) if self.news_api_key else None
            ]

            tasks = [task for task in tasks if task is not None]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            technical_data = results[0].get(symbol) if len(results) > 0 and not isinstance(results[0], Exception) else self._get_default_technical()
            sentiment_data = results[1] if len(results) > 1 and not isinstance(results[1], Exception) else self._get_neutral_sentiment()

            # Generate recommendation
            recommendation = self._get_fast_recommendation(technical_data, sentiment_data)

            return {
                "symbol": symbol,
                "recommendation": recommendation,
                "technical": {
                    "rsi": technical_data.rsi,
                    "rsi_signal": "OVERSOLD" if technical_data.rsi < 30 else "OVERBOUGHT" if technical_data.rsi > 70 else "NEUTRAL",
                    "momentum": technical_data.momentum,
                    "volatility": technical_data.volatility,
                    "trend": "BULLISH" if technical_data.sma_20 > technical_data.sma_50 else "BEARISH"
                },
                "sentiment": {
                    "score": sentiment_data.sentiment_score,
                    "signal": "BULLISH" if sentiment_data.sentiment_score > 0.2 else "BEARISH" if sentiment_data.sentiment_score < -0.2 else "NEUTRAL",
                    "confidence": sentiment_data.confidence,
                    "news_count": sentiment_data.news_count
                },
                "analysis_type": "fast"
            }

        except Exception as e:
            self.logger.error(f"Fast asset analysis failed for {symbol}: {e}")
            return {"symbol": symbol, "error": "Analysis failed", "recommendation": "HOLD"}

    def _get_fast_recommendation(self, technical: TechnicalIndicators, sentiment: SentimentData) -> str:
        """Quick recommendation logic"""
        score = 0

        # Technical signals
        if technical.rsi < 30:
            score += 1
        elif technical.rsi > 70:
            score -= 1

        if technical.momentum > 5:
            score += 1
        elif technical.momentum < -5:
            score -= 1

        # Sentiment signals
        if sentiment.sentiment_score > 0.3:
            score += 1
        elif sentiment.sentiment_score < -0.3:
            score -= 1

        # Return recommendation
        if score >= 2:
            return "BUY"
        elif score <= -2:
            return "SELL"
        else:
            return "HOLD"
