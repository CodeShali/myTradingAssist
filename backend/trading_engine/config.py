"""
Configuration management for the trading engine.
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = Field(..., env='DATABASE_URL')
    
    # Redis
    redis_url: str = Field(..., env='REDIS_URL')
    
    # API Keys
    alpaca_api_key: str = Field(..., env='ALPACA_API_KEY')
    alpaca_secret_key: str = Field(..., env='ALPACA_SECRET_KEY')
    alpaca_base_url: str = Field(
        default='https://paper-api.alpaca.markets',
        env='ALPACA_BASE_URL'
    )
    polygon_api_key: str = Field(..., env='POLYGON_API_KEY')
    news_api_key: str = Field(..., env='NEWS_API_KEY')
    
    # Trading Configuration
    trading_mode: str = Field(default='paper', env='TRADING_MODE')
    max_position_size_pct: float = Field(default=10.0, env='MAX_POSITION_SIZE_PCT')
    max_daily_trades: int = Field(default=20, env='MAX_DAILY_TRADES')
    default_profit_target_pct: float = Field(default=50.0, env='DEFAULT_PROFIT_TARGET_PCT')
    default_stop_loss_pct: float = Field(default=50.0, env='DEFAULT_STOP_LOSS_PCT')
    
    # Risk Management
    max_portfolio_delta: float = Field(default=100.0, env='MAX_PORTFOLIO_DELTA')
    max_portfolio_gamma: float = Field(default=50.0, env='MAX_PORTFOLIO_GAMMA')
    max_portfolio_vega: float = Field(default=500.0, env='MAX_PORTFOLIO_VEGA')
    max_concentration_pct: float = Field(default=25.0, env='MAX_CONCENTRATION_PCT')
    
    # Signal Generation
    signal_generation_interval: int = Field(default=300, env='SIGNAL_GENERATION_INTERVAL')
    signal_expiration_time: int = Field(default=300, env='SIGNAL_EXPIRATION_TIME')
    min_liquidity_score: float = Field(default=0.6, env='MIN_LIQUIDITY_SCORE')
    max_bid_ask_spread_pct: float = Field(default=5.0, env='MAX_BID_ASK_SPREAD_PCT')
    
    # Position Management
    position_update_interval: int = Field(default=3, env='POSITION_UPDATE_INTERVAL')
    auto_sell_enabled: bool = Field(default=True, env='AUTO_SELL_ENABLED')
    trailing_stop_enabled: bool = Field(default=False, env='TRAILING_STOP_ENABLED')
    
    # Feature Flags
    enable_auto_trading: bool = Field(default=True, env='ENABLE_AUTO_TRADING')
    enable_news_sentiment: bool = Field(default=True, env='ENABLE_NEWS_SENTIMENT')
    
    # Rate Limiting
    alpaca_rate_limit: int = Field(default=200, env='ALPACA_RATE_LIMIT')
    polygon_rate_limit: int = Field(default=5, env='POLYGON_RATE_LIMIT')
    news_api_rate_limit: int = Field(default=1000, env='NEWS_API_RATE_LIMIT')
    
    # Logging
    log_level: str = Field(default='INFO', env='LOG_LEVEL')
    log_to_file: bool = Field(default=True, env='LOG_TO_FILE')
    
    # Analytics
    analytics_update_interval: int = Field(default=60, env='ANALYTICS_UPDATE_INTERVAL')
    performance_lookback_days: int = Field(default=365, env='PERFORMANCE_LOOKBACK_DAYS')
    
    @validator('trading_mode')
    def validate_trading_mode(cls, v):
        if v not in ['paper', 'live']:
            raise ValueError('trading_mode must be either "paper" or "live"')
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'log_level must be one of {valid_levels}')
        return v.upper()
    
    class Config:
        env_file = '.env'
        case_sensitive = False


class StrategyConfig:
    """Configuration for trading strategies."""
    
    CREDIT_SPREAD = {
        'name': 'credit_spread',
        'description': 'Sell credit spreads for income generation',
        'min_credit': 0.30,  # Minimum credit as % of spread width
        'max_dte': 45,  # Maximum days to expiration
        'min_dte': 7,   # Minimum days to expiration
        'delta_target': 0.30,  # Target delta for short strike
        'spread_width': 5,  # Width of spread in dollars
        'profit_target_pct': 50.0,
        'stop_loss_pct': 100.0,
    }
    
    DEBIT_SPREAD = {
        'name': 'debit_spread',
        'description': 'Buy debit spreads for directional plays',
        'max_debit': 0.70,  # Maximum debit as % of spread width
        'max_dte': 60,
        'min_dte': 14,
        'delta_target': 0.60,
        'spread_width': 5,
        'profit_target_pct': 100.0,
        'stop_loss_pct': 50.0,
    }
    
    IRON_CONDOR = {
        'name': 'iron_condor',
        'description': 'Sell iron condors in neutral markets',
        'min_credit': 0.25,
        'max_dte': 45,
        'min_dte': 14,
        'delta_target': 0.20,
        'spread_width': 5,
        'profit_target_pct': 50.0,
        'stop_loss_pct': 100.0,
    }
    
    COVERED_CALL = {
        'name': 'covered_call',
        'description': 'Sell covered calls on existing stock positions',
        'max_dte': 45,
        'min_dte': 7,
        'delta_target': 0.30,
        'profit_target_pct': 50.0,
        'stop_loss_pct': 100.0,
    }
    
    @classmethod
    def get_strategy(cls, strategy_name: str) -> dict:
        """Get configuration for a specific strategy."""
        strategies = {
            'credit_spread': cls.CREDIT_SPREAD,
            'debit_spread': cls.DEBIT_SPREAD,
            'iron_condor': cls.IRON_CONDOR,
            'covered_call': cls.COVERED_CALL,
        }
        return strategies.get(strategy_name, {})
    
    @classmethod
    def get_all_strategies(cls) -> List[dict]:
        """Get all available strategies."""
        return [
            cls.CREDIT_SPREAD,
            cls.DEBIT_SPREAD,
            cls.IRON_CONDOR,
            cls.COVERED_CALL,
        ]


class MarketHours:
    """Market hours configuration."""
    
    MARKET_OPEN = "09:30"  # ET
    MARKET_CLOSE = "16:00"  # ET
    PRE_MARKET_OPEN = "04:00"  # ET
    AFTER_HOURS_CLOSE = "20:00"  # ET
    
    # Days when US markets are closed
    MARKET_HOLIDAYS_2024 = [
        "2024-01-01",  # New Year's Day
        "2024-01-15",  # MLK Day
        "2024-02-19",  # Presidents' Day
        "2024-03-29",  # Good Friday
        "2024-05-27",  # Memorial Day
        "2024-06-19",  # Juneteenth
        "2024-07-04",  # Independence Day
        "2024-09-02",  # Labor Day
        "2024-11-28",  # Thanksgiving
        "2024-12-25",  # Christmas
    ]


class LiquidityThresholds:
    """Thresholds for liquidity scoring."""
    
    # Minimum values for liquid options
    MIN_VOLUME = 100
    MIN_OPEN_INTEREST = 500
    MAX_BID_ASK_SPREAD_PCT = 5.0
    
    # Scoring weights
    VOLUME_WEIGHT = 0.4
    OPEN_INTEREST_WEIGHT = 0.3
    SPREAD_WEIGHT = 0.3
    
    # Reference values for scoring
    EXCELLENT_VOLUME = 1000
    EXCELLENT_OPEN_INTEREST = 5000
    EXCELLENT_SPREAD_PCT = 1.0


class RiskLimits:
    """Risk management limits."""
    
    # Position limits
    MAX_POSITION_SIZE_PCT = 10.0
    MAX_CONCENTRATION_PCT = 25.0
    MAX_DAILY_TRADES = 20
    
    # Greeks limits
    MAX_PORTFOLIO_DELTA = 100.0
    MAX_PORTFOLIO_GAMMA = 50.0
    MAX_PORTFOLIO_VEGA = 500.0
    MAX_PORTFOLIO_THETA = -100.0
    
    # Loss limits
    MAX_DAILY_LOSS_PCT = 5.0
    MAX_POSITION_LOSS_PCT = 50.0
    
    # Margin requirements
    MIN_BUYING_POWER_PCT = 20.0  # Keep 20% buying power in reserve


# Global settings instance
settings = Settings()
