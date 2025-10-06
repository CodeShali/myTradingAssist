"""
OpenAI Service for Enhanced NLP Features
Provides natural language analysis, explanations, and insights
"""

import os
import logging
from typing import Optional, Dict, List
from openai import OpenAI

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for OpenAI-powered natural language features"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4')
        self.enabled = bool(self.api_key)
        
        if self.enabled:
            self.client = OpenAI(api_key=self.api_key)
            logger.info(f"OpenAI service initialized with model: {self.model}")
        else:
            logger.info("OpenAI service disabled (no API key)")
    
    def is_enabled(self) -> bool:
        """Check if OpenAI service is enabled"""
        return self.enabled
    
    async def generate_signal_explanation(
        self,
        symbol: str,
        signal_type: str,
        confidence: float,
        technical_data: Dict,
        sentiment_data: Dict
    ) -> Optional[str]:
        """
        Generate natural language explanation for a trading signal
        
        Args:
            symbol: Stock symbol
            signal_type: 'call' or 'put'
            confidence: Signal confidence score
            technical_data: Technical indicators
            sentiment_data: News sentiment data
            
        Returns:
            Natural language explanation or None if disabled
        """
        if not self.enabled:
            return None
        
        try:
            prompt = f"""
            Explain this options trading signal in a clear, professional manner:
            
            Symbol: {symbol}
            Type: {signal_type.upper()}
            Confidence: {confidence}%
            
            Technical Indicators:
            - RSI: {technical_data.get('rsi', 'N/A')}
            - MACD: {technical_data.get('macd', 'N/A')}
            - Moving Averages: {technical_data.get('ma_signal', 'N/A')}
            
            Sentiment Analysis:
            - Overall Sentiment: {sentiment_data.get('overall', 'neutral')}
            - News Count: {sentiment_data.get('news_count', 0)}
            
            Provide:
            1. Why this trade looks good (2-3 sentences)
            2. Key risk factors to consider (2-3 points)
            3. Overall assessment
            
            Keep it concise and actionable.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert options trader providing clear, actionable insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating signal explanation: {e}")
            return None
    
    async def generate_market_summary(
        self,
        market_data: Dict,
        signals_generated: int,
        positions_open: int
    ) -> Optional[str]:
        """
        Generate pre-market or end-of-day market summary
        
        Args:
            market_data: Current market conditions
            signals_generated: Number of signals generated
            positions_open: Number of open positions
            
        Returns:
            Natural language market summary
        """
        if not self.enabled:
            return None
        
        try:
            prompt = f"""
            Create a brief, professional market update for traders:
            
            Market Conditions:
            - S&P 500: {market_data.get('sp500_change', 'N/A')}
            - VIX: {market_data.get('vix', 'N/A')}
            - Market Sentiment: {market_data.get('sentiment', 'neutral')}
            
            Trading Activity:
            - Signals Generated: {signals_generated}
            - Open Positions: {positions_open}
            
            Provide:
            1. Brief market overview (2-3 sentences)
            2. Key opportunities or risks
            3. Trading recommendation for the day
            
            Use a friendly but professional tone. Include relevant emojis.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional trading analyst providing daily market updates."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=250,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating market summary: {e}")
            return None
    
    async def generate_position_update(
        self,
        symbol: str,
        entry_price: float,
        current_price: float,
        pnl_pct: float,
        greeks: Dict,
        days_held: int
    ) -> Optional[str]:
        """
        Generate natural language position update
        
        Args:
            symbol: Option symbol
            entry_price: Entry price
            current_price: Current price
            pnl_pct: P&L percentage
            greeks: Option Greeks
            days_held: Days position has been held
            
        Returns:
            Natural language position analysis
        """
        if not self.enabled:
            return None
        
        try:
            prompt = f"""
            Provide a brief position update for this options trade:
            
            Position: {symbol}
            Entry: ${entry_price:.2f}
            Current: ${current_price:.2f}
            P&L: {pnl_pct:+.1f}%
            Days Held: {days_held}
            
            Greeks:
            - Delta: {greeks.get('delta', 'N/A')}
            - Theta: {greeks.get('theta', 'N/A')}
            - IV: {greeks.get('iv', 'N/A')}
            
            Provide:
            1. Current status assessment (1-2 sentences)
            2. Recommendation (hold, take profits, or adjust)
            3. Key factor to watch
            
            Be concise and actionable.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an options trading advisor providing position updates."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating position update: {e}")
            return None
    
    async def analyze_news_sentiment(
        self,
        headlines: List[str],
        symbol: str
    ) -> Optional[Dict]:
        """
        Enhanced news sentiment analysis using OpenAI
        
        Args:
            headlines: List of news headlines
            symbol: Stock symbol
            
        Returns:
            Enhanced sentiment analysis with context
        """
        if not self.enabled:
            return None
        
        try:
            headlines_text = "\n".join([f"- {h}" for h in headlines[:10]])
            
            prompt = f"""
            Analyze these news headlines for {symbol} and provide trading insights:
            
            {headlines_text}
            
            Provide:
            1. Overall sentiment (bullish/bearish/neutral)
            2. Key themes (2-3 points)
            3. Trading implication (1 sentence)
            4. Confidence level (high/medium/low)
            
            Format as JSON.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial news analyst providing sentiment analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.5
            )
            
            # Parse response (simplified - add proper JSON parsing)
            content = response.choices[0].message.content.strip()
            
            return {
                "enhanced_analysis": content,
                "model_used": self.model
            }
            
        except Exception as e:
            logger.error(f"Error analyzing news sentiment: {e}")
            return None
    
    async def generate_daily_summary(
        self,
        trades_executed: int,
        win_rate: float,
        total_pnl: float,
        best_trade: Dict,
        market_conditions: Dict
    ) -> Optional[str]:
        """
        Generate end-of-day trading summary
        
        Args:
            trades_executed: Number of trades
            win_rate: Win rate percentage
            total_pnl: Total P&L
            best_trade: Best performing trade
            market_conditions: Market data
            
        Returns:
            Natural language daily summary
        """
        if not self.enabled:
            return None
        
        try:
            prompt = f"""
            Create an end-of-day trading summary:
            
            Performance:
            - Trades Executed: {trades_executed}
            - Win Rate: {win_rate:.1f}%
            - Total P&L: ${total_pnl:+,.2f}
            - Best Trade: {best_trade.get('symbol', 'N/A')} ({best_trade.get('pnl', 0):+.1f}%)
            
            Market Conditions:
            - Overall: {market_conditions.get('trend', 'mixed')}
            - Volatility: {market_conditions.get('volatility', 'moderate')}
            
            Provide:
            1. Performance summary (2-3 sentences)
            2. Key insights from today's trading
            3. Plan for tomorrow
            
            Use a friendly, encouraging tone with emojis.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a supportive trading coach providing daily summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.8
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating daily summary: {e}")
            return None
    
    async def answer_trading_question(
        self,
        question: str,
        context: Dict
    ) -> Optional[str]:
        """
        Answer user questions about trading, positions, or strategies
        
        Args:
            question: User's question
            context: Relevant context (positions, market data, etc.)
            
        Returns:
            Natural language answer
        """
        if not self.enabled:
            return None
        
        try:
            prompt = f"""
            Answer this trading question clearly and concisely:
            
            Question: {question}
            
            Context:
            {context}
            
            Provide a helpful, actionable answer in 2-3 sentences.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a knowledgeable options trading assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return None


# Singleton instance
_openai_service = None


def get_openai_service() -> OpenAIService:
    """Get or create OpenAI service instance"""
    global _openai_service
    if _openai_service is None:
        _openai_service = OpenAIService()
    return _openai_service
