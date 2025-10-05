"""
Position management service for monitoring and auto-exiting positions.
"""
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid
from loguru import logger

from config import settings
from core import get_db_context, redis_manager, get_trade_logger
from core.models import Position, PositionHistory
from services.execution_service import ExecutionService
from services.market_data_service import MarketDataService


class PositionManager:
    """Service for managing open positions and auto-exits."""
    
    def __init__(
        self,
        execution_service: ExecutionService,
        market_data_service: MarketDataService
    ):
        """Initialize position manager."""
        self.execution_service = execution_service
        self.market_data_service = market_data_service
        self.trade_logger = get_trade_logger()
        
        logger.info("Position manager initialized")
    
    async def monitor_positions(self):
        """Monitor all open positions for exit conditions."""
        try:
            # Get all open positions
            with get_db_context() as db:
                positions = db.query(Position).filter(Position.status == 'open').all()
            
            if not positions:
                logger.debug("No open positions to monitor")
                return
            
            logger.debug(f"Monitoring {len(positions)} open positions")
            
            # Update each position
            for position in positions:
                try:
                    await self._update_position(position)
                    await self._check_exit_conditions(position)
                except Exception as e:
                    logger.error(f"Error monitoring position {position.id}: {e}")
            
        except Exception as e:
            logger.error(f"Error in position monitoring: {e}")
    
    async def _update_position(self, position: Position):
        """Update position with current market data."""
        try:
            # Get current option price
            quote = await self.market_data_service.get_option_quote(position.option_symbol)
            
            if not quote:
                logger.warning(f"Could not get quote for {position.option_symbol}")
                return
            
            current_price = quote['mid']
            
            # Calculate unrealized P&L
            if position.quantity > 0:  # Long position
                unrealized_pnl = (current_price - position.entry_price) * position.quantity * 100
            else:  # Short position
                unrealized_pnl = (position.entry_price - current_price) * abs(position.quantity) * 100
            
            unrealized_pnl_pct = (unrealized_pnl / (position.entry_price * abs(position.quantity) * 100)) * 100
            
            # Update position in database
            with get_db_context() as db:
                db_position = db.query(Position).filter(Position.id == position.id).first()
                
                if db_position:
                    db_position.current_price = current_price
                    db_position.unrealized_pnl = unrealized_pnl
                    db_position.unrealized_pnl_pct = unrealized_pnl_pct
                    db_position.last_updated_at = datetime.now()
                    
                    # Update Greeks if available (simplified - in production, calculate actual Greeks)
                    db_position.delta = None  # Would calculate from option pricing model
                    db_position.gamma = None
                    db_position.theta = None
                    db_position.vega = None
                    db_position.iv = None
                    
                    db.commit()
            
            # Record history snapshot
            await self._record_position_history(position.id, current_price, unrealized_pnl, unrealized_pnl_pct)
            
            # Publish update to Redis for real-time UI
            await self._publish_position_update(position.id, {
                'current_price': current_price,
                'unrealized_pnl': unrealized_pnl,
                'unrealized_pnl_pct': unrealized_pnl_pct
            })
            
        except Exception as e:
            logger.error(f"Error updating position {position.id}: {e}")
    
    async def _check_exit_conditions(self, position: Position):
        """Check if position should be auto-exited."""
        try:
            if not settings.auto_sell_enabled:
                return
            
            # Refresh position data
            with get_db_context() as db:
                position = db.query(Position).filter(Position.id == position.id).first()
            
            if not position or position.status != 'open':
                return
            
            # Check profit target
            if position.unrealized_pnl_pct >= position.profit_target_pct:
                logger.info(
                    f"Position {position.id} hit profit target: "
                    f"{position.unrealized_pnl_pct:.2f}% >= {position.profit_target_pct}%"
                )
                await self._auto_exit_position(position.id, 'profit_target')
                return
            
            # Check stop loss
            if position.unrealized_pnl_pct <= -position.stop_loss_pct:
                logger.info(
                    f"Position {position.id} hit stop loss: "
                    f"{position.unrealized_pnl_pct:.2f}% <= -{position.stop_loss_pct}%"
                )
                await self._auto_exit_position(position.id, 'stop_loss')
                return
            
            # Check trailing stop if enabled
            if settings.trailing_stop_enabled and position.trailing_stop_pct:
                await self._check_trailing_stop(position)
            
            # Check expiration
            days_to_expiration = (position.expiration_date - datetime.now().date()).days
            if days_to_expiration <= 0:
                logger.info(f"Position {position.id} expired")
                await self._auto_exit_position(position.id, 'expiration')
                return
            
        except Exception as e:
            logger.error(f"Error checking exit conditions for position {position.id}: {e}")
    
    async def _check_trailing_stop(self, position: Position):
        """Check trailing stop condition."""
        try:
            # Simplified trailing stop logic
            # In production, track high water mark and adjust stop dynamically
            
            if position.unrealized_pnl_pct > 25:  # If up 25%+
                # Tighten stop loss to lock in gains
                adjusted_stop = position.stop_loss_pct / 2
                
                if position.unrealized_pnl_pct <= -adjusted_stop:
                    logger.info(f"Position {position.id} hit trailing stop")
                    await self._auto_exit_position(position.id, 'auto_exit')
            
        except Exception as e:
            logger.error(f"Error checking trailing stop: {e}")
    
    async def _auto_exit_position(self, position_id: uuid.UUID, reason: str):
        """Automatically exit a position."""
        try:
            self.trade_logger.info(f"Auto-exiting position {position_id} - Reason: {reason}")
            
            result = await self.execution_service.close_position(position_id, reason)
            
            if result:
                self.trade_logger.info(
                    f"Auto-exit successful - P&L: ${result['realized_pnl']:.2f} "
                    f"({result['realized_pnl_pct']:.2f}%)"
                )
                
                # Publish notification
                await self._publish_exit_notification(position_id, result, reason)
            else:
                logger.error(f"Failed to auto-exit position {position_id}")
            
        except Exception as e:
            logger.error(f"Error auto-exiting position {position_id}: {e}")
    
    async def _record_position_history(
        self,
        position_id: uuid.UUID,
        current_price: float,
        unrealized_pnl: float,
        unrealized_pnl_pct: float
    ):
        """Record position history snapshot."""
        try:
            with get_db_context() as db:
                history = PositionHistory(
                    position_id=position_id,
                    current_price=current_price,
                    unrealized_pnl=unrealized_pnl,
                    unrealized_pnl_pct=unrealized_pnl_pct,
                    snapshot_at=datetime.now()
                )
                
                db.add(history)
                db.commit()
            
        except Exception as e:
            logger.error(f"Error recording position history: {e}")
    
    async def _publish_position_update(
        self,
        position_id: uuid.UUID,
        update_data: Dict[str, Any]
    ):
        """Publish position update to Redis."""
        try:
            with get_db_context() as db:
                position = db.query(Position).filter(Position.id == position_id).first()
                
                if position:
                    message = {
                        'type': 'position_update',
                        'position_id': str(position_id),
                        'user_id': str(position.user_id),
                        'symbol': position.symbol,
                        'current_price': update_data['current_price'],
                        'unrealized_pnl': update_data['unrealized_pnl'],
                        'unrealized_pnl_pct': update_data['unrealized_pnl_pct'],
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Publish to user-specific channel
                    channel = f"positions:{position.user_id}"
                    redis_manager.publish(channel, message)
            
        except Exception as e:
            logger.error(f"Error publishing position update: {e}")
    
    async def _publish_exit_notification(
        self,
        position_id: uuid.UUID,
        exit_result: Dict[str, Any],
        reason: str
    ):
        """Publish exit notification."""
        try:
            with get_db_context() as db:
                position = db.query(Position).filter(Position.id == position_id).first()
                
                if position:
                    message = {
                        'type': 'position_closed',
                        'position_id': str(position_id),
                        'user_id': str(position.user_id),
                        'symbol': position.symbol,
                        'strategy_type': position.strategy_type,
                        'exit_price': exit_result['exit_price'],
                        'realized_pnl': exit_result['realized_pnl'],
                        'realized_pnl_pct': exit_result['realized_pnl_pct'],
                        'close_reason': reason,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Publish to user-specific channel
                    channel = f"positions:{position.user_id}"
                    redis_manager.publish(channel, message)
                    
                    # Also publish to notifications channel
                    notif_channel = f"notifications:{position.user_id}"
                    redis_manager.publish(notif_channel, message)
            
        except Exception as e:
            logger.error(f"Error publishing exit notification: {e}")
    
    async def get_portfolio_summary(self, user_id: uuid.UUID) -> Dict[str, Any]:
        """Get portfolio summary for a user."""
        try:
            with get_db_context() as db:
                positions = db.query(Position).filter(
                    Position.user_id == user_id,
                    Position.status == 'open'
                ).all()
                
                total_unrealized_pnl = sum(p.unrealized_pnl or 0 for p in positions)
                
                # Calculate portfolio Greeks
                total_delta = sum(p.delta or 0 for p in positions)
                total_gamma = sum(p.gamma or 0 for p in positions)
                total_vega = sum(p.vega or 0 for p in positions)
                total_theta = sum(p.theta or 0 for p in positions)
                
                # Get closed positions for today
                from datetime import date
                today = date.today()
                closed_today = db.query(Position).filter(
                    Position.user_id == user_id,
                    Position.status == 'closed',
                    Position.closed_at >= datetime.combine(today, datetime.min.time())
                ).all()
                
                daily_realized_pnl = sum(p.realized_pnl or 0 for p in closed_today)
                
                return {
                    'open_positions': len(positions),
                    'total_unrealized_pnl': round(total_unrealized_pnl, 2),
                    'daily_realized_pnl': round(daily_realized_pnl, 2),
                    'portfolio_greeks': {
                        'delta': round(total_delta, 2),
                        'gamma': round(total_gamma, 2),
                        'vega': round(total_vega, 2),
                        'theta': round(total_theta, 2)
                    },
                    'positions': [
                        {
                            'id': str(p.id),
                            'symbol': p.symbol,
                            'strategy_type': p.strategy_type,
                            'quantity': p.quantity,
                            'entry_price': float(p.entry_price),
                            'current_price': float(p.current_price) if p.current_price else None,
                            'unrealized_pnl': float(p.unrealized_pnl) if p.unrealized_pnl else 0,
                            'unrealized_pnl_pct': float(p.unrealized_pnl_pct) if p.unrealized_pnl_pct else 0,
                            'opened_at': p.opened_at.isoformat()
                        }
                        for p in positions
                    ]
                }
            
        except Exception as e:
            logger.error(f"Error getting portfolio summary: {e}")
            return {
                'open_positions': 0,
                'total_unrealized_pnl': 0,
                'daily_realized_pnl': 0,
                'portfolio_greeks': {'delta': 0, 'gamma': 0, 'vega': 0, 'theta': 0},
                'positions': []
            }
