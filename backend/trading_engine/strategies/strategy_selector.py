"""
Strategy selection and recommendation engine.
"""
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
from loguru import logger

from config import StrategyConfig
from core.models import UserConfig


class StrategySelector:
    """Selects optimal trading strategies based on market conditions."""
    
    def __init__(self):
        """Initialize strategy selector."""
        logger.info("Strategy selector initialized")
    
    async def select_strategy(
        self,
        symbol: str,
        stock_price: float,
        options_chain: Dict[str, Any],
        historical_volatility: Optional[float],
        news_sentiment: Optional[Dict[str, Any]],
        user_config: UserConfig
    ) -> Optional[Dict[str, Any]]:
        """
        Select best strategy for current market conditions.
        
        Args:
            symbol: Stock symbol
            stock_price: Current stock price
            options_chain: Options chain data
            historical_volatility: Historical volatility
            news_sentiment: News sentiment summary
            user_config: User configuration
            
        Returns:
            Strategy recommendation or None
        """
        try:
            # Get allowed strategies
            allowed_strategies = user_config.allowed_strategies or []
            
            if not allowed_strategies:
                logger.debug("No allowed strategies configured")
                return None
            
            # Analyze market conditions
            market_analysis = self._analyze_market_conditions(
                stock_price=stock_price,
                historical_volatility=historical_volatility,
                news_sentiment=news_sentiment
            )
            
            # Score each strategy
            strategy_scores = {}
            
            for strategy_name in allowed_strategies:
                score = self._score_strategy(
                    strategy_name=strategy_name,
                    market_analysis=market_analysis,
                    options_chain=options_chain,
                    stock_price=stock_price
                )
                
                if score > 0:
                    strategy_scores[strategy_name] = score
            
            if not strategy_scores:
                logger.debug(f"No suitable strategies for {symbol}")
                return None
            
            # Select best strategy
            best_strategy = max(strategy_scores, key=strategy_scores.get)
            confidence_score = min(strategy_scores[best_strategy] * 10, 100)
            
            # Build trade recommendation
            recommendation = await self._build_trade_recommendation(
                strategy_name=best_strategy,
                symbol=symbol,
                stock_price=stock_price,
                options_chain=options_chain,
                market_analysis=market_analysis,
                confidence_score=confidence_score,
                user_config=user_config
            )
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Error selecting strategy: {e}")
            return None
    
    def _analyze_market_conditions(
        self,
        stock_price: float,
        historical_volatility: Optional[float],
        news_sentiment: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze current market conditions."""
        analysis = {
            'volatility_regime': 'normal',
            'sentiment': 'neutral',
            'trend': 'neutral',
            'volatility_level': historical_volatility or 30.0
        }
        
        # Volatility regime
        if historical_volatility:
            if historical_volatility > 50:
                analysis['volatility_regime'] = 'high'
            elif historical_volatility < 20:
                analysis['volatility_regime'] = 'low'
        
        # Sentiment
        if news_sentiment:
            avg_sentiment = news_sentiment.get('avg_sentiment', 0)
            if avg_sentiment > 0.3:
                analysis['sentiment'] = 'positive'
            elif avg_sentiment < -0.3:
                analysis['sentiment'] = 'negative'
        
        return analysis
    
    def _score_strategy(
        self,
        strategy_name: str,
        market_analysis: Dict[str, Any],
        options_chain: Dict[str, Any],
        stock_price: float
    ) -> float:
        """Score a strategy based on market conditions."""
        score = 5.0  # Base score
        
        volatility_regime = market_analysis['volatility_regime']
        sentiment = market_analysis['sentiment']
        
        if strategy_name == 'credit_spread':
            # Credit spreads work well in low-medium volatility
            if volatility_regime == 'low':
                score += 2.0
            elif volatility_regime == 'high':
                score -= 1.0
            
            # Prefer in neutral sentiment
            if sentiment == 'neutral':
                score += 1.0
        
        elif strategy_name == 'debit_spread':
            # Debit spreads work well with directional conviction
            if sentiment in ['positive', 'negative']:
                score += 2.0
            
            # Better in lower volatility (cheaper to buy)
            if volatility_regime == 'low':
                score += 1.0
        
        elif strategy_name == 'iron_condor':
            # Iron condors need low volatility and neutral sentiment
            if volatility_regime == 'low' and sentiment == 'neutral':
                score += 3.0
            elif volatility_regime == 'high':
                score -= 2.0
        
        elif strategy_name == 'covered_call':
            # Covered calls work in neutral to slightly bullish markets
            if sentiment in ['neutral', 'positive']:
                score += 1.5
            
            # Better in higher volatility (higher premiums)
            if volatility_regime == 'high':
                score += 1.0
        
        return max(score, 0)
    
    async def _build_trade_recommendation(
        self,
        strategy_name: str,
        symbol: str,
        stock_price: float,
        options_chain: Dict[str, Any],
        market_analysis: Dict[str, Any],
        confidence_score: float,
        user_config: UserConfig
    ) -> Optional[Dict[str, Any]]:
        """Build detailed trade recommendation."""
        try:
            strategy_config = StrategyConfig.get_strategy(strategy_name)
            
            if not strategy_config:
                return None
            
            # Find suitable expiration
            expiration = self._find_suitable_expiration(
                options_chain=options_chain,
                min_dte=strategy_config['min_dte'],
                max_dte=strategy_config['max_dte'],
                allowed_expirations=user_config.allowed_expirations
            )
            
            if not expiration:
                logger.debug(f"No suitable expiration found for {symbol}")
                return None
            
            # Find suitable strike
            strike_info = self._find_suitable_strike(
                options_chain=options_chain,
                expiration=expiration,
                stock_price=stock_price,
                strategy_config=strategy_config,
                market_analysis=market_analysis
            )
            
            if not strike_info:
                logger.debug(f"No suitable strike found for {symbol}")
                return None
            
            # Calculate position size
            quantity = self._calculate_position_size(
                stock_price=stock_price,
                user_config=user_config
            )
            
            # Build reasoning
            reasoning = self._build_reasoning(
                strategy_name=strategy_name,
                symbol=symbol,
                market_analysis=market_analysis,
                strike_info=strike_info
            )
            
            return {
                'strategy_type': strategy_name,
                'signal_type': strike_info['signal_type'],
                'option_symbol': strike_info['option_symbol'],
                'strike_price': strike_info['strike'],
                'expiration_date': expiration,
                'option_type': strike_info['option_type'],
                'quantity': quantity,
                'limit_price': strike_info.get('limit_price'),
                'fallback_strikes': strike_info.get('fallback_strikes', []),
                'confidence_score': confidence_score,
                'reasoning': reasoning
            }
            
        except Exception as e:
            logger.error(f"Error building trade recommendation: {e}")
            return None
    
    def _find_suitable_expiration(
        self,
        options_chain: Dict[str, Any],
        min_dte: int,
        max_dte: int,
        allowed_expirations: List[str]
    ) -> Optional[date]:
        """Find suitable expiration date."""
        try:
            expirations = options_chain.get('expirations', [])
            
            if not expirations:
                return None
            
            today = date.today()
            
            for exp in expirations:
                if isinstance(exp, str):
                    exp_date = date.fromisoformat(exp)
                else:
                    exp_date = exp
                
                dte = (exp_date - today).days
                
                # Check DTE range
                if min_dte <= dte <= max_dte:
                    # Check if expiration type is allowed
                    if self._is_expiration_allowed(dte, allowed_expirations):
                        return exp_date
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding expiration: {e}")
            return None
    
    def _is_expiration_allowed(self, dte: int, allowed_expirations: List[str]) -> bool:
        """Check if expiration type is allowed."""
        if 'weekly' in allowed_expirations and dte <= 7:
            return True
        if 'monthly' in allowed_expirations and 20 <= dte <= 45:
            return True
        if 'quarterly' in allowed_expirations and 60 <= dte <= 120:
            return True
        
        return False
    
    def _find_suitable_strike(
        self,
        options_chain: Dict[str, Any],
        expiration: date,
        stock_price: float,
        strategy_config: Dict[str, Any],
        market_analysis: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Find suitable strike price."""
        try:
            strategy_name = strategy_config['name']
            
            if strategy_name == 'credit_spread':
                return self._find_credit_spread_strikes(
                    options_chain, expiration, stock_price, strategy_config, market_analysis
                )
            elif strategy_name == 'debit_spread':
                return self._find_debit_spread_strikes(
                    options_chain, expiration, stock_price, strategy_config, market_analysis
                )
            elif strategy_name == 'covered_call':
                return self._find_covered_call_strike(
                    options_chain, expiration, stock_price, strategy_config
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding strike: {e}")
            return None
    
    def _find_credit_spread_strikes(
        self,
        options_chain: Dict[str, Any],
        expiration: date,
        stock_price: float,
        strategy_config: Dict[str, Any],
        market_analysis: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Find strikes for credit spread."""
        # Simplified version - sell put spread below current price
        exp_str = expiration.isoformat()
        puts = options_chain.get('puts', {}).get(exp_str, {})
        
        if not puts:
            return None
        
        # Target strike ~30 delta (roughly 70% OTM)
        target_strike = stock_price * 0.95  # 5% OTM
        
        # Find closest strike
        strikes = sorted([float(s) for s in puts.keys()])
        closest_strike = min(strikes, key=lambda x: abs(x - target_strike))
        
        if closest_strike in puts:
            option_data = puts[closest_strike]
            
            return {
                'signal_type': 'sell',
                'option_symbol': option_data['symbol'],
                'strike': closest_strike,
                'option_type': 'put',
                'limit_price': None,  # Will be determined at execution
                'fallback_strikes': []
            }
        
        return None
    
    def _find_debit_spread_strikes(
        self,
        options_chain: Dict[str, Any],
        expiration: date,
        stock_price: float,
        strategy_config: Dict[str, Any],
        market_analysis: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Find strikes for debit spread."""
        sentiment = market_analysis.get('sentiment', 'neutral')
        
        # Choose calls for bullish, puts for bearish
        if sentiment == 'positive':
            option_type = 'call'
            options = options_chain.get('calls', {})
            target_strike = stock_price * 1.03  # 3% OTM
        else:
            option_type = 'put'
            options = options_chain.get('puts', {})
            target_strike = stock_price * 0.97  # 3% OTM
        
        exp_str = expiration.isoformat()
        exp_options = options.get(exp_str, {})
        
        if not exp_options:
            return None
        
        strikes = sorted([float(s) for s in exp_options.keys()])
        closest_strike = min(strikes, key=lambda x: abs(x - target_strike))
        
        if closest_strike in exp_options:
            option_data = exp_options[closest_strike]
            
            return {
                'signal_type': 'buy',
                'option_symbol': option_data['symbol'],
                'strike': closest_strike,
                'option_type': option_type,
                'limit_price': None,
                'fallback_strikes': []
            }
        
        return None
    
    def _find_covered_call_strike(
        self,
        options_chain: Dict[str, Any],
        expiration: date,
        stock_price: float,
        strategy_config: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Find strike for covered call."""
        exp_str = expiration.isoformat()
        calls = options_chain.get('calls', {}).get(exp_str, {})
        
        if not calls:
            return None
        
        # Target strike ~30 delta (slightly OTM)
        target_strike = stock_price * 1.05  # 5% OTM
        
        strikes = sorted([float(s) for s in calls.keys()])
        closest_strike = min(strikes, key=lambda x: abs(x - target_strike))
        
        if closest_strike in calls:
            option_data = calls[closest_strike]
            
            return {
                'signal_type': 'sell',
                'option_symbol': option_data['symbol'],
                'strike': closest_strike,
                'option_type': 'call',
                'limit_price': None,
                'fallback_strikes': []
            }
        
        return None
    
    def _calculate_position_size(
        self,
        stock_price: float,
        user_config: UserConfig
    ) -> int:
        """Calculate position size based on user config."""
        # Simplified - in production, would use actual portfolio value
        assumed_portfolio = 100000  # $100k portfolio
        
        max_position_value = assumed_portfolio * (user_config.max_position_size_pct / 100)
        
        # For options, assume ~$500 per contract risk
        contracts = int(max_position_value / 500)
        
        return max(1, min(contracts, 10))  # Between 1 and 10 contracts
    
    def _build_reasoning(
        self,
        strategy_name: str,
        symbol: str,
        market_analysis: Dict[str, Any],
        strike_info: Dict[str, Any]
    ) -> str:
        """Build human-readable reasoning for the trade."""
        reasoning_parts = [
            f"Strategy: {strategy_name.replace('_', ' ').title()}",
            f"Market Analysis: {market_analysis['volatility_regime'].title()} volatility, {market_analysis['sentiment'].title()} sentiment",
            f"Strike: ${strike_info['strike']:.2f} {strike_info['option_type'].upper()}",
            f"Action: {strike_info['signal_type'].upper()}"
        ]
        
        return " | ".join(reasoning_parts)
