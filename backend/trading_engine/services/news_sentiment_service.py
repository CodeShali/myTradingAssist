"""
News sentiment analysis service.
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import aiohttp
from loguru import logger
from transformers import pipeline

from config import settings
from core import get_db_context, redis_manager, CacheKeys
from core.models import NewsSentiment


class NewsSentimentService:
    """Service for fetching and analyzing news sentiment."""
    
    def __init__(self):
        """Initialize news sentiment service."""
        self.news_api_key = settings.news_api_key
        self.news_api_url = "https://newsapi.org/v2/everything"
        
        # Initialize sentiment analyzer (FinBERT would be ideal, using a simpler model for now)
        try:
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="ProsusAI/finbert",
                tokenizer="ProsusAI/finbert"
            )
            logger.info("FinBERT sentiment analyzer loaded")
        except Exception as e:
            logger.warning(f"Failed to load FinBERT, using default model: {e}")
            self.sentiment_analyzer = pipeline("sentiment-analysis")
        
        self.last_news_request = datetime.now()
        
        logger.info("News sentiment service initialized")
    
    async def fetch_news(
        self,
        symbol: str,
        hours_back: int = 12
    ) -> List[Dict[str, Any]]:
        """
        Fetch news articles for a symbol.
        
        Args:
            symbol: Stock symbol
            hours_back: How many hours back to fetch news
            
        Returns:
            List of news articles
        """
        try:
            # Check cache first
            cache_key = CacheKeys.news_sentiment(symbol)
            cached_news = redis_manager.get(cache_key)
            
            if cached_news:
                return cached_news
            
            # Rate limiting
            await self._rate_limit()
            
            # Fetch from NewsAPI
            from_date = datetime.now() - timedelta(hours=hours_back)
            
            params = {
                'apiKey': self.news_api_key,
                'q': symbol,
                'from': from_date.isoformat(),
                'sortBy': 'publishedAt',
                'language': 'en',
                'pageSize': 20
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.news_api_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        articles = data.get('articles', [])
                        
                        # Process articles
                        processed_articles = []
                        for article in articles:
                            processed = {
                                'headline': article.get('title', ''),
                                'source': article.get('source', {}).get('name', ''),
                                'url': article.get('url', ''),
                                'published_at': article.get('publishedAt', ''),
                                'description': article.get('description', ''),
                                'content': article.get('content', '')
                            }
                            processed_articles.append(processed)
                        
                        # Cache for 15 minutes
                        redis_manager.set(cache_key, processed_articles, expiration=900)
                        
                        return processed_articles
                    else:
                        logger.error(f"NewsAPI error: {response.status}")
                        return []
            
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            return []
    
    async def analyze_sentiment(
        self,
        text: str
    ) -> Dict[str, Any]:
        """
        Analyze sentiment of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment analysis results
        """
        try:
            if not text or len(text.strip()) == 0:
                return {
                    'score': 0.0,
                    'label': 'neutral',
                    'confidence': 0.0
                }
            
            # Truncate text to model's max length
            text = text[:512]
            
            # Run sentiment analysis
            result = self.sentiment_analyzer(text)[0]
            
            # Map FinBERT labels to our schema
            label_map = {
                'positive': 'positive',
                'negative': 'negative',
                'neutral': 'neutral'
            }
            
            # Convert to score (-1 to 1)
            score_map = {
                'positive': 1.0,
                'negative': -1.0,
                'neutral': 0.0
            }
            
            label = result['label'].lower()
            confidence = result['score']
            
            # Adjust score based on confidence
            base_score = score_map.get(label, 0.0)
            adjusted_score = base_score * confidence
            
            return {
                'score': round(adjusted_score, 2),
                'label': label_map.get(label, 'neutral'),
                'confidence': round(confidence, 2)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {
                'score': 0.0,
                'label': 'neutral',
                'confidence': 0.0
            }
    
    async def get_news_sentiment_summary(
        self,
        symbol: str
    ) -> Dict[str, Any]:
        """
        Get news sentiment summary for a symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Sentiment summary
        """
        try:
            # Fetch recent news
            articles = await self.fetch_news(symbol, hours_back=12)
            
            if not articles:
                return {
                    'symbol': symbol,
                    'article_count': 0,
                    'avg_sentiment': 0.0,
                    'sentiment_label': 'neutral',
                    'top_headlines': [],
                    'high_impact_news': []
                }
            
            # Analyze sentiment for each article
            sentiments = []
            analyzed_articles = []
            
            for article in articles[:10]:  # Analyze top 10
                text = f"{article['headline']} {article.get('description', '')}"
                sentiment = await self.analyze_sentiment(text)
                
                analyzed_articles.append({
                    'headline': article['headline'],
                    'source': article['source'],
                    'url': article['url'],
                    'published_at': article['published_at'],
                    'sentiment_score': sentiment['score'],
                    'sentiment_label': sentiment['label']
                })
                
                sentiments.append(sentiment['score'])
            
            # Calculate average sentiment
            avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0
            
            # Determine overall label
            if avg_sentiment > 0.3:
                overall_label = 'positive'
            elif avg_sentiment < -0.3:
                overall_label = 'negative'
            else:
                overall_label = 'neutral'
            
            # Identify high impact news (very positive or very negative)
            high_impact = [
                a for a in analyzed_articles
                if abs(a['sentiment_score']) > 0.6
            ]
            
            # Store in database
            await self._store_news_sentiment(symbol, analyzed_articles)
            
            return {
                'symbol': symbol,
                'article_count': len(articles),
                'avg_sentiment': round(avg_sentiment, 2),
                'sentiment_label': overall_label,
                'top_headlines': analyzed_articles[:3],
                'high_impact_news': high_impact
            }
            
        except Exception as e:
            logger.error(f"Error getting news sentiment summary for {symbol}: {e}")
            return {
                'symbol': symbol,
                'article_count': 0,
                'avg_sentiment': 0.0,
                'sentiment_label': 'neutral',
                'top_headlines': [],
                'high_impact_news': []
            }
    
    async def check_news_veto(
        self,
        symbol: str
    ) -> Dict[str, Any]:
        """
        Check if news should veto a trade signal.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Veto decision and reasoning
        """
        try:
            summary = await self.get_news_sentiment_summary(symbol)
            
            # Veto conditions
            should_veto = False
            veto_reason = None
            
            # Very negative sentiment
            if summary['avg_sentiment'] < -0.6:
                should_veto = True
                veto_reason = "Very negative news sentiment detected"
            
            # High impact negative news
            high_impact_negative = [
                n for n in summary['high_impact_news']
                if n['sentiment_score'] < -0.6
            ]
            
            if len(high_impact_negative) >= 2:
                should_veto = True
                veto_reason = "Multiple high-impact negative news articles"
            
            # Check for specific keywords that indicate high risk
            risk_keywords = ['bankruptcy', 'fraud', 'lawsuit', 'investigation', 'recall', 'fda rejection']
            for article in summary['top_headlines']:
                headline_lower = article['headline'].lower()
                if any(keyword in headline_lower for keyword in risk_keywords):
                    should_veto = True
                    veto_reason = f"High-risk news detected: {article['headline'][:50]}..."
                    break
            
            return {
                'should_veto': should_veto,
                'veto_reason': veto_reason,
                'sentiment_summary': summary
            }
            
        except Exception as e:
            logger.error(f"Error checking news veto for {symbol}: {e}")
            return {
                'should_veto': False,
                'veto_reason': None,
                'sentiment_summary': None
            }
    
    async def _store_news_sentiment(
        self,
        symbol: str,
        articles: List[Dict[str, Any]]
    ):
        """Store news sentiment in database."""
        try:
            with get_db_context() as db:
                for article in articles:
                    # Check if already exists
                    existing = db.query(NewsSentiment).filter(
                        NewsSentiment.symbol == symbol,
                        NewsSentiment.url == article['url']
                    ).first()
                    
                    if not existing:
                        # Categorize news
                        category = self._categorize_news(article['headline'])
                        
                        # Determine impact level
                        impact_level = 'high' if abs(article['sentiment_score']) > 0.6 else \
                                      'medium' if abs(article['sentiment_score']) > 0.3 else 'low'
                        
                        # Map sentiment score to label
                        if article['sentiment_score'] > 0.6:
                            sentiment_label = 'very_positive'
                        elif article['sentiment_score'] > 0.2:
                            sentiment_label = 'positive'
                        elif article['sentiment_score'] < -0.6:
                            sentiment_label = 'very_negative'
                        elif article['sentiment_score'] < -0.2:
                            sentiment_label = 'negative'
                        else:
                            sentiment_label = 'neutral'
                        
                        news = NewsSentiment(
                            symbol=symbol,
                            headline=article['headline'],
                            source=article['source'],
                            url=article['url'],
                            published_at=datetime.fromisoformat(article['published_at'].replace('Z', '+00:00')),
                            sentiment_score=article['sentiment_score'],
                            sentiment_label=sentiment_label,
                            impact_level=impact_level,
                            news_category=category,
                            processed=True
                        )
                        
                        db.add(news)
                
                db.commit()
                
        except Exception as e:
            logger.error(f"Error storing news sentiment: {e}")
    
    def _categorize_news(self, headline: str) -> str:
        """Categorize news based on headline."""
        headline_lower = headline.lower()
        
        if any(word in headline_lower for word in ['earnings', 'revenue', 'profit', 'eps']):
            return 'earnings'
        elif any(word in headline_lower for word in ['fda', 'approval', 'drug', 'trial']):
            return 'fda'
        elif any(word in headline_lower for word in ['upgrade', 'downgrade', 'rating', 'target']):
            return 'analyst_rating'
        elif any(word in headline_lower for word in ['merger', 'acquisition', 'buyout']):
            return 'ma'
        elif any(word in headline_lower for word in ['lawsuit', 'investigation', 'fraud']):
            return 'legal'
        else:
            return 'general'
    
    async def _rate_limit(self):
        """Enforce NewsAPI rate limiting."""
        elapsed = (datetime.now() - self.last_news_request).total_seconds()
        min_interval = 86400 / settings.news_api_rate_limit  # Daily limit
        
        if elapsed < min_interval:
            await asyncio.sleep(min_interval - elapsed)
        
        self.last_news_request = datetime.now()
