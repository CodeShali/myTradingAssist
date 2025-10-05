"""
Market data service for fetching and caching market data from external APIs.
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import aiohttp
from loguru import logger
from alpaca.data.historical import StockHistoricalDataClient, OptionHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, StockLatestQuoteRequest
from alpaca.data.timeframe import TimeFrame
from polygon import RESTClient as PolygonClient

from config import settings, LiquidityThresholds
from core import redis_manager, CacheKeys, get_db_context
from core.models import MarketDataCache


class MarketDataService:
    """Service for fetching and managing market data."""
    
    def __init__(self):
        """Initialize market data service."""
        self.alpaca_stock_client = StockHistoricalDataClient(
            api_key=settings.alpaca_api_key,
            secret_key=settings.alpaca_secret_key
        )
        
        self.polygon_client = PolygonClient(settings.polygon_api_key)
        
        # Rate limiting
        self.last_alpaca_request = datetime.now()
        self.last_polygon_request = datetime.now()
        
        logger.info("Market data service initialized")
    
    async def get_stock_price(self, symbol: str) -> Optional[float]:
        """
        Get current stock price.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Current price or None
        """
        try:
            # Check cache first
            cache_key = CacheKeys.market_data(symbol, "price")
            cached_price = redis_manager.get(cache_key)
            
            if cached_price:
                return float(cached_price)
            
            # Fetch from Alpaca
            await self._rate_limit_alpaca()
            
            request = StockLatestQuoteRequest(symbol_or_symbols=symbol)
            quote = self.alpaca_stock_client.get_stock_latest_quote(request)
            
            if symbol in quote:
                price = float(quote[symbol].ask_price + quote[symbol].bid_price) / 2
                
                # Cache for 5 seconds
                redis_manager.set(cache_key, price, expiration=5)
                
                return price
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching stock price for {symbol}: {e}")
            return None
    
    async def get_options_chain(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get options chain for a symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Options chain data
        """
        try:
            # Check cache first
            cache_key = CacheKeys.options_chain(symbol)
            cached_chain = redis_manager.get(cache_key)
            
            if cached_chain:
                return cached_chain
            
            # Fetch from Polygon
            await self._rate_limit_polygon()
            
            # Get options contracts
            contracts = self.polygon_client.list_options_contracts(
                underlying_ticker=symbol,
                limit=1000
            )
            
            if not contracts:
                return None
            
            # Organize by expiration and strike
            chain = self._organize_options_chain(contracts)
            
            # Cache for 5 minutes
            redis_manager.set(cache_key, chain, expiration=300)
            
            return chain
            
        except Exception as e:
            logger.error(f"Error fetching options chain for {symbol}: {e}")
            return None
    
    async def get_option_quote(self, option_symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get quote for a specific option.
        
        Args:
            option_symbol: Option symbol
            
        Returns:
            Option quote data
        """
        try:
            await self._rate_limit_polygon()
            
            quote = self.polygon_client.get_last_quote(option_symbol)
            
            if quote:
                return {
                    'bid': quote.bid_price,
                    'ask': quote.ask_price,
                    'bid_size': quote.bid_size,
                    'ask_size': quote.ask_size,
                    'mid': (quote.bid_price + quote.ask_price) / 2,
                    'spread': quote.ask_price - quote.bid_price,
                    'spread_pct': ((quote.ask_price - quote.bid_price) / quote.ask_price) * 100 if quote.ask_price > 0 else 0,
                    'timestamp': quote.sip_timestamp
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching option quote for {option_symbol}: {e}")
            return None
    
    async def calculate_liquidity_score(
        self,
        volume: int,
        open_interest: int,
        bid_ask_spread_pct: float
    ) -> float:
        """
        Calculate liquidity score for an option.
        
        Args:
            volume: Daily volume
            open_interest: Open interest
            bid_ask_spread_pct: Bid-ask spread percentage
            
        Returns:
            Liquidity score (0-1)
        """
        # Volume score (0-1)
        volume_score = min(volume / LiquidityThresholds.EXCELLENT_VOLUME, 1.0)
        
        # Open interest score (0-1)
        oi_score = min(open_interest / LiquidityThresholds.EXCELLENT_OPEN_INTEREST, 1.0)
        
        # Spread score (0-1, inverted - lower spread is better)
        spread_score = max(0, 1 - (bid_ask_spread_pct / LiquidityThresholds.MAX_BID_ASK_SPREAD_PCT))
        
        # Weighted average
        liquidity_score = (
            volume_score * LiquidityThresholds.VOLUME_WEIGHT +
            oi_score * LiquidityThresholds.OPEN_INTEREST_WEIGHT +
            spread_score * LiquidityThresholds.SPREAD_WEIGHT
        )
        
        return round(liquidity_score, 2)
    
    async def get_historical_volatility(
        self,
        symbol: str,
        days: int = 252
    ) -> Optional[float]:
        """
        Calculate historical volatility.
        
        Args:
            symbol: Stock symbol
            days: Number of days for calculation
            
        Returns:
            Annualized volatility
        """
        try:
            # Check cache
            cache_key = CacheKeys.market_data(symbol, f"hv_{days}")
            cached_hv = redis_manager.get(cache_key)
            
            if cached_hv:
                return float(cached_hv)
            
            # Fetch historical data
            await self._rate_limit_alpaca()
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days + 10)  # Extra buffer
            
            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Day,
                start=start_date,
                end=end_date
            )
            
            bars = self.alpaca_stock_client.get_stock_bars(request)
            
            if symbol not in bars or len(bars[symbol]) < days:
                return None
            
            # Calculate returns
            prices = [bar.close for bar in bars[symbol]]
            returns = []
            
            for i in range(1, len(prices)):
                daily_return = (prices[i] - prices[i-1]) / prices[i-1]
                returns.append(daily_return)
            
            # Calculate standard deviation and annualize
            import numpy as np
            std_dev = np.std(returns)
            annualized_vol = std_dev * np.sqrt(252) * 100  # Annualize and convert to percentage
            
            # Cache for 1 hour
            redis_manager.set(cache_key, annualized_vol, expiration=3600)
            
            return round(annualized_vol, 2)
            
        except Exception as e:
            logger.error(f"Error calculating historical volatility for {symbol}: {e}")
            return None
    
    async def get_iv_percentile(
        self,
        symbol: str,
        current_iv: float,
        days: int = 252
    ) -> Optional[float]:
        """
        Calculate IV percentile.
        
        Args:
            symbol: Stock symbol
            current_iv: Current implied volatility
            days: Lookback period
            
        Returns:
            IV percentile (0-100)
        """
        try:
            # This is a simplified version - in production, you'd fetch historical IV data
            # For now, we'll use historical volatility as a proxy
            
            hv = await self.get_historical_volatility(symbol, days)
            
            if not hv:
                return None
            
            # Simple percentile calculation (current IV vs HV)
            # In production, use actual historical IV data
            if current_iv > hv * 1.5:
                return 90.0
            elif current_iv > hv * 1.2:
                return 75.0
            elif current_iv > hv:
                return 60.0
            elif current_iv > hv * 0.8:
                return 40.0
            else:
                return 25.0
            
        except Exception as e:
            logger.error(f"Error calculating IV percentile for {symbol}: {e}")
            return None
    
    async def update_market_data(self):
        """Update market data for all watched symbols."""
        try:
            # Get all active watchlist symbols from database
            with get_db_context() as db:
                from core.models import Watchlist
                watchlists = db.query(Watchlist).filter(Watchlist.is_active == True).all()
                symbols = list(set([w.symbol for w in watchlists]))
            
            if not symbols:
                logger.debug("No symbols in watchlist")
                return
            
            logger.info(f"Updating market data for {len(symbols)} symbols")
            
            # Update prices and options chains
            tasks = []
            for symbol in symbols:
                tasks.append(self.get_stock_price(symbol))
                tasks.append(self.get_options_chain(symbol))
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
            logger.info("Market data update complete")
            
        except Exception as e:
            logger.error(f"Error updating market data: {e}")
    
    async def check_api_health(self) -> bool:
        """
        Check if external APIs are healthy.
        
        Returns:
            True if APIs are healthy
        """
        try:
            # Try to fetch a simple quote
            test_symbol = "SPY"
            price = await self.get_stock_price(test_symbol)
            
            return price is not None
            
        except Exception as e:
            logger.error(f"API health check failed: {e}")
            return False
    
    def _organize_options_chain(self, contracts: List) -> Dict[str, Any]:
        """Organize options contracts into a structured chain."""
        chain = {
            'calls': {},
            'puts': {},
            'expirations': set()
        }
        
        for contract in contracts:
            expiration = contract.expiration_date
            strike = contract.strike_price
            option_type = contract.contract_type.lower()
            
            chain['expirations'].add(expiration)
            
            if option_type == 'call':
                if expiration not in chain['calls']:
                    chain['calls'][expiration] = {}
                chain['calls'][expiration][strike] = {
                    'symbol': contract.ticker,
                    'strike': strike,
                    'expiration': expiration,
                    'type': 'call'
                }
            else:
                if expiration not in chain['puts']:
                    chain['puts'][expiration] = {}
                chain['puts'][expiration][strike] = {
                    'symbol': contract.ticker,
                    'strike': strike,
                    'expiration': expiration,
                    'type': 'put'
                }
        
        chain['expirations'] = sorted(list(chain['expirations']))
        
        return chain
    
    async def _rate_limit_alpaca(self):
        """Enforce Alpaca rate limiting."""
        elapsed = (datetime.now() - self.last_alpaca_request).total_seconds()
        min_interval = 60 / settings.alpaca_rate_limit
        
        if elapsed < min_interval:
            await asyncio.sleep(min_interval - elapsed)
        
        self.last_alpaca_request = datetime.now()
    
    async def _rate_limit_polygon(self):
        """Enforce Polygon rate limiting."""
        elapsed = (datetime.now() - self.last_polygon_request).total_seconds()
        min_interval = 60 / settings.polygon_rate_limit
        
        if elapsed < min_interval:
            await asyncio.sleep(min_interval - elapsed)
        
        self.last_polygon_request = datetime.now()
