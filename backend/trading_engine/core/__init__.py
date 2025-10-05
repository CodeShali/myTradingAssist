"""
Core module for the trading engine.
"""
from core.database import Base, engine, get_db, get_db_context, init_db, check_db_connection
from core.models import (
    User, UserConfig, Watchlist, TradeSignal, Execution, Position,
    PositionHistory, MarketDataCache, NewsSentiment, PerformanceMetrics,
    AuditLog, SystemConfig
)
from core.redis_manager import redis_manager, RedisManager, CacheKeys
from core.logger import setup_logger, get_trade_logger

__all__ = [
    # Database
    'Base',
    'engine',
    'get_db',
    'get_db_context',
    'init_db',
    'check_db_connection',
    
    # Models
    'User',
    'UserConfig',
    'Watchlist',
    'TradeSignal',
    'Execution',
    'Position',
    'PositionHistory',
    'MarketDataCache',
    'NewsSentiment',
    'PerformanceMetrics',
    'AuditLog',
    'SystemConfig',
    
    # Redis
    'redis_manager',
    'RedisManager',
    'CacheKeys',
    
    # Logger
    'setup_logger',
    'get_trade_logger',
]
