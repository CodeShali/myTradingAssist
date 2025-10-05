"""
SQLAlchemy models for the trading platform.
"""
from datetime import datetime, date
from typing import Optional, Dict, Any, List
from decimal import Decimal
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Date,
    ForeignKey, Text, JSON, CheckConstraint, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from core.database import Base


class User(Base):
    """User model."""
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    discord_user_id = Column(String(255), unique=True, index=True)
    trading_mode = Column(String(20), default='paper')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    configs = relationship("UserConfig", back_populates="user", cascade="all, delete-orphan")
    signals = relationship("TradeSignal", back_populates="user", cascade="all, delete-orphan")
    positions = relationship("Position", back_populates="user", cascade="all, delete-orphan")
    watchlists = relationship("Watchlist", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("trading_mode IN ('paper', 'live')", name='check_trading_mode'),
    )


class UserConfig(Base):
    """User configuration model."""
    __tablename__ = 'user_configs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Position sizing
    max_position_size_pct = Column(Float, default=10.0)
    max_daily_trades = Column(Integer, default=20)
    
    # Risk parameters
    default_profit_target_pct = Column(Float, default=50.0)
    default_stop_loss_pct = Column(Float, default=50.0)
    max_portfolio_delta = Column(Float, default=100.0)
    max_portfolio_gamma = Column(Float, default=50.0)
    max_portfolio_vega = Column(Float, default=500.0)
    max_concentration_pct = Column(Float, default=25.0)
    
    # Liquidity requirements
    min_option_volume = Column(Integer, default=100)
    min_open_interest = Column(Integer, default=500)
    max_bid_ask_spread_pct = Column(Float, default=5.0)
    min_liquidity_score = Column(Float, default=0.6)
    
    # Strategy preferences
    allowed_strategies = Column(JSONB, default=["credit_spread", "debit_spread", "iron_condor", "covered_call"])
    allowed_expirations = Column(JSONB, default=["weekly", "monthly"])
    
    # Feature flags
    auto_sell_enabled = Column(Boolean, default=True)
    trailing_stop_enabled = Column(Boolean, default=False)
    news_sentiment_enabled = Column(Boolean, default=True)
    discord_notifications_enabled = Column(Boolean, default=True)
    web_notifications_enabled = Column(Boolean, default=True)
    
    version = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="configs")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'version', name='uq_user_config_version'),
    )


class Watchlist(Base):
    """Watchlist model."""
    __tablename__ = 'watchlists'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    symbol = Column(String(10), nullable=False)
    is_active = Column(Boolean, default=True)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="watchlists")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'symbol', name='uq_user_symbol'),
        Index('idx_watchlists_user_active', 'user_id', 'is_active'),
    )


class TradeSignal(Base):
    """Trade signal model."""
    __tablename__ = 'trade_signals'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Signal details
    symbol = Column(String(10), nullable=False)
    strategy_type = Column(String(50), nullable=False)
    signal_type = Column(String(20), nullable=False)
    
    # Option details
    option_symbol = Column(String(50), nullable=False)
    strike_price = Column(Float, nullable=False)
    expiration_date = Column(Date, nullable=False)
    option_type = Column(String(4), nullable=False)
    
    # Pricing
    quantity = Column(Integer, nullable=False)
    limit_price = Column(Float)
    max_spread_pct = Column(Float)
    
    # Fallback strikes
    fallback_strikes = Column(JSONB)
    
    # AI reasoning
    confidence_score = Column(Float)
    reasoning = Column(Text)
    market_conditions = Column(JSONB)
    
    # State management
    status = Column(String(20), default='pending')
    confirmation_source = Column(String(20))
    confirmed_at = Column(DateTime(timezone=True))
    confirmed_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Expiration
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="signals", foreign_keys=[user_id])
    executions = relationship("Execution", back_populates="signal", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("signal_type IN ('buy', 'sell')", name='check_signal_type'),
        CheckConstraint("option_type IN ('call', 'put')", name='check_option_type'),
        CheckConstraint("status IN ('pending', 'confirmed', 'rejected', 'expired', 'executing', 'executed', 'failed')", name='check_status'),
        CheckConstraint("confirmation_source IN ('discord', 'web', 'auto')", name='check_confirmation_source'),
        CheckConstraint("confidence_score >= 0 AND confidence_score <= 100", name='check_confidence_score'),
        Index('idx_trade_signals_user_status', 'user_id', 'status'),
        Index('idx_trade_signals_expires_at', 'expires_at'),
    )


class Execution(Base):
    """Execution model."""
    __tablename__ = 'executions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    signal_id = Column(UUID(as_uuid=True), ForeignKey('trade_signals.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Order details
    broker_order_id = Column(String(255))
    order_type = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)
    
    # Execution details
    filled_quantity = Column(Integer, nullable=False)
    filled_price = Column(Float, nullable=False)
    commission = Column(Float, default=0.0)
    fees = Column(Float, default=0.0)
    
    # Timing
    submitted_at = Column(DateTime(timezone=True), nullable=False)
    filled_at = Column(DateTime(timezone=True), nullable=False)
    
    # Quality metrics
    slippage_pct = Column(Float)
    execution_quality_score = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    signal = relationship("TradeSignal", back_populates="executions")
    
    __table_args__ = (
        CheckConstraint("order_type IN ('market', 'limit', 'stop', 'stop_limit')", name='check_order_type'),
        CheckConstraint("side IN ('buy', 'sell')", name='check_side'),
        Index('idx_executions_signal_id', 'signal_id'),
    )


class Position(Base):
    """Position model."""
    __tablename__ = 'positions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    signal_id = Column(UUID(as_uuid=True), ForeignKey('trade_signals.id'))
    execution_id = Column(UUID(as_uuid=True), ForeignKey('executions.id'))
    
    # Position details
    symbol = Column(String(10), nullable=False)
    option_symbol = Column(String(50), nullable=False)
    strategy_type = Column(String(50), nullable=False)
    
    # Option details
    strike_price = Column(Float, nullable=False)
    expiration_date = Column(Date, nullable=False)
    option_type = Column(String(4), nullable=False)
    
    # Position sizing
    quantity = Column(Integer, nullable=False)
    entry_price = Column(Float, nullable=False)
    current_price = Column(Float)
    
    # P&L
    unrealized_pnl = Column(Float, default=0.0)
    unrealized_pnl_pct = Column(Float, default=0.0)
    realized_pnl = Column(Float)
    realized_pnl_pct = Column(Float)
    
    # Greeks
    delta = Column(Float)
    gamma = Column(Float)
    theta = Column(Float)
    vega = Column(Float)
    iv = Column(Float)
    
    # Exit parameters
    profit_target_pct = Column(Float, nullable=False)
    stop_loss_pct = Column(Float, nullable=False)
    trailing_stop_pct = Column(Float)
    
    # State
    status = Column(String(20), default='open')
    close_reason = Column(String(50))
    
    # Timing
    opened_at = Column(DateTime(timezone=True), nullable=False)
    closed_at = Column(DateTime(timezone=True))
    last_updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="positions")
    history = relationship("PositionHistory", back_populates="position", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("option_type IN ('call', 'put')", name='check_position_option_type'),
        CheckConstraint("status IN ('open', 'closed', 'expired')", name='check_position_status'),
        CheckConstraint("close_reason IN ('profit_target', 'stop_loss', 'manual', 'expiration', 'auto_exit')", name='check_close_reason'),
        Index('idx_positions_user_status', 'user_id', 'status'),
        Index('idx_positions_symbol', 'symbol'),
    )


class PositionHistory(Base):
    """Position history model."""
    __tablename__ = 'position_history'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    position_id = Column(UUID(as_uuid=True), ForeignKey('positions.id', ondelete='CASCADE'), nullable=False)
    
    # Snapshot data
    current_price = Column(Float, nullable=False)
    unrealized_pnl = Column(Float, nullable=False)
    unrealized_pnl_pct = Column(Float, nullable=False)
    
    # Greeks snapshot
    delta = Column(Float)
    gamma = Column(Float)
    theta = Column(Float)
    vega = Column(Float)
    iv = Column(Float)
    
    snapshot_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    position = relationship("Position", back_populates="history")
    
    __table_args__ = (
        Index('idx_position_history_position_id', 'position_id', 'snapshot_at'),
    )


class MarketDataCache(Base):
    """Market data cache model."""
    __tablename__ = 'market_data_cache'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(10), nullable=False)
    data_type = Column(String(50), nullable=False)
    
    # Data
    data = Column(JSONB, nullable=False)
    
    # Metadata
    source = Column(String(50), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('symbol', 'data_type', name='uq_symbol_data_type'),
        Index('idx_market_data_cache_symbol', 'symbol', 'data_type'),
    )


class NewsSentiment(Base):
    """News sentiment model."""
    __tablename__ = 'news_sentiment'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(10), nullable=False)
    
    # News details
    headline = Column(Text, nullable=False)
    source = Column(String(255))
    url = Column(Text)
    published_at = Column(DateTime(timezone=True), nullable=False)
    
    # Sentiment analysis
    sentiment_score = Column(Float)
    sentiment_label = Column(String(20))
    impact_level = Column(String(20))
    news_category = Column(String(50))
    
    # Processing
    processed = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('symbol', 'url', name='uq_symbol_url'),
        CheckConstraint("sentiment_score >= -1 AND sentiment_score <= 1", name='check_sentiment_score'),
        CheckConstraint("sentiment_label IN ('very_negative', 'negative', 'neutral', 'positive', 'very_positive')", name='check_sentiment_label'),
        CheckConstraint("impact_level IN ('low', 'medium', 'high')", name='check_impact_level'),
        Index('idx_news_sentiment_symbol', 'symbol', 'published_at'),
    )


class PerformanceMetrics(Base):
    """Performance metrics model."""
    __tablename__ = 'performance_metrics'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Time period
    period_type = Column(String(20), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    
    # Performance metrics
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    win_rate = Column(Float)
    
    # P&L metrics
    total_pnl = Column(Float, default=0.0)
    total_pnl_pct = Column(Float, default=0.0)
    avg_win = Column(Float)
    avg_loss = Column(Float)
    profit_factor = Column(Float)
    
    # Risk metrics
    max_drawdown = Column(Float)
    max_drawdown_date = Column(Date)
    sharpe_ratio = Column(Float)
    sortino_ratio = Column(Float)
    
    # Strategy breakdown
    strategy_performance = Column(JSONB)
    
    # Greeks exposure
    avg_delta = Column(Float)
    avg_gamma = Column(Float)
    avg_vega = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('user_id', 'period_type', 'period_start', name='uq_user_period'),
        CheckConstraint("period_type IN ('daily', 'weekly', 'monthly', 'yearly', 'all_time')", name='check_period_type'),
    )


class AuditLog(Base):
    """Audit log model."""
    __tablename__ = 'audit_log'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'))
    
    # Action details
    action_type = Column(String(50), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(UUID(as_uuid=True))
    
    # Changes
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    
    # Context
    ip_address = Column(INET)
    user_agent = Column(Text)
    source = Column(String(50))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_audit_log_user_created', 'user_id', 'created_at'),
    )


class SystemConfig(Base):
    """System configuration model."""
    __tablename__ = 'system_config'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String(255), unique=True, nullable=False)
    value = Column(JSONB, nullable=False)
    description = Column(Text)
    is_sensitive = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
