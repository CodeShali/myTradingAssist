"""
AI-powered trade signal generation service.
"""
import asyncio
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any
from decimal import Decimal
import uuid
from loguru import logger

from config import settings, StrategyConfig
from core import get_db_context, redis_manager, CacheKeys
from core.models import TradeSignal, User, UserConfig, Watchlist
from services.market_data_service import MarketDataService
from services.news_sentiment_service import NewsSentimentService
from strategies.strategy_selector import StrategySelector


class SignalGenerator:
    """Service for generating AI-powered trade signals."""
    
    def __init__(self, market_data_service: MarketDataService):
        """Initialize signal generator."""
        self.market_data_service = market_data_service
        self.news_sentiment_service = NewsSentimentService()
        self.strategy_selector = StrategySelector()
        
        logger.info("Signal generator initialized")
    
    async def generate_signals(self):
        """Generate trade signals for all active users."""
        try:
            logger.info("Starting signal generation cycle...")
            
            # Get all active users
            with get_db_context() as db:
                users = db.query(User).filter(User.is_active == True).all()
            
            if not users:
                logger.debug("No active users found")
                return
            
            # Generate signals for each user
            for user in users:
                try:
                    await self._generate_signals_for_user(user.id)
                except Exception as e:
                    logger.error(f"Error generating signals for user {user.id}: {e}")
            
            logger.info("Signal generation cycle complete")
            
        except Exception as e:
            logger.error(f"Error in signal generation: {e}")
    
    async def _generate_signals_for_user(self, user_id: uuid.UUID):
        """Generate signals for a specific user."""
        try:
            with get_db_context() as db:
                # Get user config
                config = db.query(UserConfig).filter(
                    UserConfig.user_id == user_id
                ).order_by(UserConfig.version.desc()).first()
                
                if not config:
                    logger.warning(f"No config found for user {user_id}")
                    return
                
                # Get watchlist
                watchlist = db.query(Watchlist).filter(
                    Watchlist.user_id == user_id,
                    Watchlist.is_active == True
                ).all()
                
                if not watchlist:
                    logger.debug(f"No watchlist symbols for user {user_id}")
                    return
                
                # Check pending signals count
                pending_count = db.query(TradeSignal).filter(
                    TradeSignal.user_id == user_id,
                    TradeSignal.status == 'pending'
                ).count()
                
                max_concurrent = 10  # Maximum concurrent pending signals
                if pending_count >= max_concurrent:
                    logger.debug(f"User {user_id} has {pending_count} pending signals, skipping")
                    return
                
                # Check daily trade count
                today = date.today()
                today_trades = db.query(TradeSignal).filter(
                    TradeSignal.user_id == user_id,
                    TradeSignal.created_at >= datetime.combine(today, datetime.min.time()),
                    TradeSignal.status.in_(['confirmed', 'executed'])
                ).count()
                
                if today_trades >= config.max_daily_trades:
                    logger.debug(f"User {user_id} reached daily trade limit")
                    return
            
            # Analyze each symbol
            for watch_item in watchlist:
                try:
                    signal = await self._analyze_symbol(
                        user_id=user_id,
                        symbol=watch_item.symbol,
                        config=config
                    )
                    
                    if signal:
                        await self._create_signal(signal)
                        
                except Exception as e:
                    logger.error(f"Error analyzing {watch_item.symbol}: {e}")
            
        except Exception as e:
            logger.error(f"Error generating signals for user {user_id}: {e}")
    
    async def _analyze_symbol(
        self,
        user_id: uuid.UUID,
        symbol: str,
        config: UserConfig
    ) -> Optional[Dict[str, Any]]:
        """Analyze a symbol and generate signal if conditions are met."""
        try:
            logger.debug(f"Analyzing {symbol}...")
            
            # Get current stock price
            stock_price = await self.market_data_service.get_stock_price(symbol)
            if not stock_price:
                logger.warning(f"Could not fetch price for {symbol}")
                return None
            
            # Get options chain
            options_chain = await self.market_data_service.get_options_chain(symbol)
            if not options_chain:
                logger.warning(f"Could not fetch options chain for {symbol}")
                return None
            
            # Get news sentiment if enabled
            news_sentiment = None
            if config.news_sentiment_enabled:
                news_sentiment = await self.news_sentiment_service.get_news_sentiment_summary(symbol)
                
                # Check for news veto
                veto_check = await self.news_sentiment_service.check_news_veto(symbol)
                if veto_check['should_veto']:
                    logger.info(f"Trade vetoed for {symbol}: {veto_check['veto_reason']}")
                    return None
            
            # Get historical volatility
            hv = await self.market_data_service.get_historical_volatility(symbol)
            
            # Select best strategy
            strategy_result = await self.strategy_selector.select_strategy(
                symbol=symbol,
                stock_price=stock_price,
                options_chain=options_chain,
                historical_volatility=hv,
                news_sentiment=news_sentiment,
                user_config=config
            )
            
            if not strategy_result:
                logger.debug(f"No suitable strategy found for {symbol}")
                return None
            
            # Validate liquidity
            liquidity_valid = await self._validate_liquidity(
                strategy_result['option_symbol'],
                config
            )
            
            if not liquidity_valid:
                logger.debug(f"Liquidity check failed for {symbol}")
                return None
            
            # Build signal
            signal = {
                'user_id': user_id,
                'symbol': symbol,
                'strategy_type': strategy_result['strategy_type'],
                'signal_type': strategy_result['signal_type'],
                'option_symbol': strategy_result['option_symbol'],
                'strike_price': strategy_result['strike_price'],
                'expiration_date': strategy_result['expiration_date'],
                'option_type': strategy_result['option_type'],
                'quantity': strategy_result['quantity'],
                'limit_price': strategy_result['limit_price'],
                'max_spread_pct': config.max_bid_ask_spread_pct,
                'fallback_strikes': strategy_result.get('fallback_strikes', []),
                'confidence_score': strategy_result['confidence_score'],
                'reasoning': strategy_result['reasoning'],
                'market_conditions': {
                    'stock_price': stock_price,
                    'historical_volatility': hv,
                    'news_sentiment': news_sentiment['avg_sentiment'] if news_sentiment else None,
                    'timestamp': datetime.now().isoformat()
                },
                'expires_at': datetime.now() + timedelta(seconds=settings.signal_expiration_time)
            }
            
            logger.info(f"Generated signal for {symbol}: {strategy_result['strategy_type']}")
            
            return signal
            
        except Exception as e:
            logger.error(f"Error analyzing symbol {symbol}: {e}")
            return None
    
    async def _validate_liquidity(
        self,
        option_symbol: str,
        config: UserConfig
    ) -> bool:
        """Validate option liquidity meets requirements."""
        try:
            quote = await self.market_data_service.get_option_quote(option_symbol)
            
            if not quote:
                return False
            
            # Check spread
            if quote['spread_pct'] > config.max_bid_ask_spread_pct:
                logger.debug(f"Spread too wide: {quote['spread_pct']}%")
                return False
            
            # In production, also check volume and open interest
            # For now, we'll assume if we got a quote, it's liquid enough
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating liquidity for {option_symbol}: {e}")
            return False
    
    async def _create_signal(self, signal_data: Dict[str, Any]):
        """Create and store a trade signal."""
        try:
            with get_db_context() as db:
                signal = TradeSignal(
                    user_id=signal_data['user_id'],
                    symbol=signal_data['symbol'],
                    strategy_type=signal_data['strategy_type'],
                    signal_type=signal_data['signal_type'],
                    option_symbol=signal_data['option_symbol'],
                    strike_price=signal_data['strike_price'],
                    expiration_date=signal_data['expiration_date'],
                    option_type=signal_data['option_type'],
                    quantity=signal_data['quantity'],
                    limit_price=signal_data['limit_price'],
                    max_spread_pct=signal_data['max_spread_pct'],
                    fallback_strikes=signal_data['fallback_strikes'],
                    confidence_score=signal_data['confidence_score'],
                    reasoning=signal_data['reasoning'],
                    market_conditions=signal_data['market_conditions'],
                    status='pending',
                    expires_at=signal_data['expires_at']
                )
                
                db.add(signal)
                db.commit()
                db.refresh(signal)
                
                # Publish to Redis for real-time notifications
                await self._publish_signal(signal)
                
                logger.info(f"Created signal {signal.id} for {signal.symbol}")
                
        except Exception as e:
            logger.error(f"Error creating signal: {e}")
    
    async def _publish_signal(self, signal: TradeSignal):
        """Publish signal to Redis for notifications."""
        try:
            signal_data = {
                'id': str(signal.id),
                'user_id': str(signal.user_id),
                'symbol': signal.symbol,
                'strategy_type': signal.strategy_type,
                'signal_type': signal.signal_type,
                'option_symbol': signal.option_symbol,
                'strike_price': float(signal.strike_price),
                'expiration_date': signal.expiration_date.isoformat(),
                'option_type': signal.option_type,
                'quantity': signal.quantity,
                'limit_price': float(signal.limit_price) if signal.limit_price else None,
                'confidence_score': float(signal.confidence_score) if signal.confidence_score else None,
                'reasoning': signal.reasoning,
                'expires_at': signal.expires_at.isoformat(),
                'created_at': signal.created_at.isoformat()
            }
            
            # Publish to user-specific channel
            channel = f"signals:{signal.user_id}"
            redis_manager.publish(channel, signal_data)
            
            # Also publish to general signals channel
            redis_manager.publish("signals:all", signal_data)
            
        except Exception as e:
            logger.error(f"Error publishing signal: {e}")
    
    async def expire_old_signals(self):
        """Expire signals that have passed their expiration time."""
        try:
            with get_db_context() as db:
                expired_signals = db.query(TradeSignal).filter(
                    TradeSignal.status == 'pending',
                    TradeSignal.expires_at <= datetime.now()
                ).all()
                
                for signal in expired_signals:
                    signal.status = 'expired'
                    logger.info(f"Expired signal {signal.id} for {signal.symbol}")
                
                db.commit()
                
                if expired_signals:
                    logger.info(f"Expired {len(expired_signals)} signals")
                
        except Exception as e:
            logger.error(f"Error expiring signals: {e}")
