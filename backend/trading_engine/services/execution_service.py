"""
Order execution service for placing and managing trades.
"""
import asyncio
from datetime import datetime
from typing import Dict, Optional, Any
import uuid
from loguru import logger
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderType

from config import settings
from core import get_db_context, get_trade_logger
from core.models import TradeSignal, Execution, Position


class ExecutionService:
    """Service for executing trades via broker API."""
    
    def __init__(self):
        """Initialize execution service."""
        self.trading_client = TradingClient(
            api_key=settings.alpaca_api_key,
            secret_key=settings.alpaca_secret_key,
            paper=settings.trading_mode == 'paper'
        )
        
        self.trade_logger = get_trade_logger()
        
        logger.info(f"Execution service initialized in {settings.trading_mode.upper()} mode")
    
    async def execute_signal(self, signal_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """
        Execute a confirmed trade signal.
        
        Args:
            signal_id: Trade signal ID
            
        Returns:
            Execution result or None
        """
        try:
            with get_db_context() as db:
                signal = db.query(TradeSignal).filter(TradeSignal.id == signal_id).first()
                
                if not signal:
                    logger.error(f"Signal {signal_id} not found")
                    return None
                
                if signal.status != 'confirmed':
                    logger.warning(f"Signal {signal_id} is not confirmed (status: {signal.status})")
                    return None
                
                # Update status to executing
                signal.status = 'executing'
                db.commit()
            
            self.trade_logger.info(f"Executing signal {signal_id} for {signal.symbol}")
            
            # Pre-execution validation
            validation_result = await self._pre_execution_validation(signal)
            
            if not validation_result['valid']:
                logger.warning(f"Pre-execution validation failed: {validation_result['reason']}")
                
                # Try fallback strikes if available
                if signal.fallback_strikes:
                    logger.info("Attempting fallback strikes...")
                    # In production, implement fallback logic here
                
                await self._mark_signal_failed(signal_id, validation_result['reason'])
                return None
            
            # Place order
            execution_result = await self._place_order(signal)
            
            if not execution_result:
                await self._mark_signal_failed(signal_id, "Order placement failed")
                return None
            
            # Record execution
            execution = await self._record_execution(signal, execution_result)
            
            # Create position
            position = await self._create_position(signal, execution)
            
            # Update signal status
            with get_db_context() as db:
                signal = db.query(TradeSignal).filter(TradeSignal.id == signal_id).first()
                signal.status = 'executed'
                db.commit()
            
            self.trade_logger.info(
                f"Successfully executed {signal.symbol} {signal.strategy_type} - "
                f"Position ID: {position.id}"
            )
            
            return {
                'signal_id': str(signal_id),
                'execution_id': str(execution.id),
                'position_id': str(position.id),
                'filled_price': execution_result['filled_price'],
                'filled_quantity': execution_result['filled_quantity']
            }
            
        except Exception as e:
            logger.error(f"Error executing signal {signal_id}: {e}")
            await self._mark_signal_failed(signal_id, str(e))
            return None
    
    async def _pre_execution_validation(self, signal: TradeSignal) -> Dict[str, Any]:
        """Validate conditions before execution."""
        try:
            # Check market hours
            if not await self._is_market_open():
                return {'valid': False, 'reason': 'Market is closed'}
            
            # Check account status
            account = self.trading_client.get_account()
            
            if account.trading_blocked:
                return {'valid': False, 'reason': 'Trading is blocked'}
            
            # Check buying power
            if float(account.buying_power) < 1000:  # Minimum buying power
                return {'valid': False, 'reason': 'Insufficient buying power'}
            
            # In production, add more validations:
            # - Current option price vs limit price
            # - Liquidity check
            # - Risk limits
            
            return {'valid': True, 'reason': None}
            
        except Exception as e:
            logger.error(f"Error in pre-execution validation: {e}")
            return {'valid': False, 'reason': str(e)}
    
    async def _place_order(self, signal: TradeSignal) -> Optional[Dict[str, Any]]:
        """Place order with broker."""
        try:
            # Determine order side
            side = OrderSide.BUY if signal.signal_type == 'buy' else OrderSide.SELL
            
            # Use limit order if limit price is specified, otherwise market order
            if signal.limit_price:
                order_request = LimitOrderRequest(
                    symbol=signal.option_symbol,
                    qty=signal.quantity,
                    side=side,
                    time_in_force=TimeInForce.DAY,
                    limit_price=float(signal.limit_price)
                )
                order_type = 'limit'
            else:
                order_request = MarketOrderRequest(
                    symbol=signal.option_symbol,
                    qty=signal.quantity,
                    side=side,
                    time_in_force=TimeInForce.DAY
                )
                order_type = 'market'
            
            # Submit order
            order = self.trading_client.submit_order(order_request)
            
            logger.info(f"Order submitted: {order.id} ({order_type})")
            
            # Wait for fill (with timeout)
            filled_order = await self._wait_for_fill(order.id, timeout=30)
            
            if not filled_order:
                # Cancel unfilled order
                try:
                    self.trading_client.cancel_order_by_id(order.id)
                    logger.warning(f"Order {order.id} cancelled due to timeout")
                except:
                    pass
                
                return None
            
            return {
                'broker_order_id': filled_order.id,
                'filled_price': float(filled_order.filled_avg_price),
                'filled_quantity': int(filled_order.filled_qty),
                'submitted_at': filled_order.submitted_at,
                'filled_at': filled_order.filled_at,
                'order_type': order_type
            }
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None
    
    async def _wait_for_fill(self, order_id: str, timeout: int = 30) -> Optional[Any]:
        """Wait for order to be filled."""
        start_time = datetime.now()
        
        while (datetime.now() - start_time).seconds < timeout:
            try:
                order = self.trading_client.get_order_by_id(order_id)
                
                if order.status == 'filled':
                    return order
                elif order.status in ['cancelled', 'expired', 'rejected']:
                    logger.warning(f"Order {order_id} status: {order.status}")
                    return None
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error checking order status: {e}")
                await asyncio.sleep(1)
        
        logger.warning(f"Order {order_id} fill timeout")
        return None
    
    async def _record_execution(
        self,
        signal: TradeSignal,
        execution_result: Dict[str, Any]
    ) -> Execution:
        """Record execution in database."""
        try:
            with get_db_context() as db:
                execution = Execution(
                    signal_id=signal.id,
                    user_id=signal.user_id,
                    broker_order_id=execution_result['broker_order_id'],
                    order_type=execution_result['order_type'],
                    side=signal.signal_type,
                    filled_quantity=execution_result['filled_quantity'],
                    filled_price=execution_result['filled_price'],
                    commission=0.0,  # Alpaca has no commissions
                    fees=0.0,
                    submitted_at=execution_result['submitted_at'],
                    filled_at=execution_result['filled_at']
                )
                
                db.add(execution)
                db.commit()
                db.refresh(execution)
                
                return execution
                
        except Exception as e:
            logger.error(f"Error recording execution: {e}")
            raise
    
    async def _create_position(
        self,
        signal: TradeSignal,
        execution: Execution
    ) -> Position:
        """Create position record."""
        try:
            with get_db_context() as db:
                # Get user config for exit parameters
                from core.models import UserConfig
                config = db.query(UserConfig).filter(
                    UserConfig.user_id == signal.user_id
                ).order_by(UserConfig.version.desc()).first()
                
                position = Position(
                    user_id=signal.user_id,
                    signal_id=signal.id,
                    execution_id=execution.id,
                    symbol=signal.symbol,
                    option_symbol=signal.option_symbol,
                    strategy_type=signal.strategy_type,
                    strike_price=signal.strike_price,
                    expiration_date=signal.expiration_date,
                    option_type=signal.option_type,
                    quantity=execution.filled_quantity,
                    entry_price=execution.filled_price,
                    current_price=execution.filled_price,
                    profit_target_pct=config.default_profit_target_pct if config else 50.0,
                    stop_loss_pct=config.default_stop_loss_pct if config else 50.0,
                    status='open',
                    opened_at=execution.filled_at
                )
                
                db.add(position)
                db.commit()
                db.refresh(position)
                
                return position
                
        except Exception as e:
            logger.error(f"Error creating position: {e}")
            raise
    
    async def _mark_signal_failed(self, signal_id: uuid.UUID, reason: str):
        """Mark signal as failed."""
        try:
            with get_db_context() as db:
                signal = db.query(TradeSignal).filter(TradeSignal.id == signal_id).first()
                if signal:
                    signal.status = 'failed'
                    db.commit()
                    
                    logger.error(f"Signal {signal_id} marked as failed: {reason}")
                    
        except Exception as e:
            logger.error(f"Error marking signal as failed: {e}")
    
    async def close_position(
        self,
        position_id: uuid.UUID,
        reason: str = 'manual'
    ) -> Optional[Dict[str, Any]]:
        """
        Close an open position.
        
        Args:
            position_id: Position ID
            reason: Close reason
            
        Returns:
            Close result or None
        """
        try:
            with get_db_context() as db:
                position = db.query(Position).filter(Position.id == position_id).first()
                
                if not position:
                    logger.error(f"Position {position_id} not found")
                    return None
                
                if position.status != 'open':
                    logger.warning(f"Position {position_id} is not open")
                    return None
            
            self.trade_logger.info(f"Closing position {position_id} - Reason: {reason}")
            
            # Place closing order (opposite side)
            close_side = OrderSide.SELL if position.quantity > 0 else OrderSide.BUY
            
            order_request = MarketOrderRequest(
                symbol=position.option_symbol,
                qty=abs(position.quantity),
                side=close_side,
                time_in_force=TimeInForce.DAY
            )
            
            order = self.trading_client.submit_order(order_request)
            filled_order = await self._wait_for_fill(order.id, timeout=30)
            
            if not filled_order:
                logger.error(f"Failed to close position {position_id}")
                return None
            
            # Update position
            with get_db_context() as db:
                position = db.query(Position).filter(Position.id == position_id).first()
                
                exit_price = float(filled_order.filled_avg_price)
                
                # Calculate realized P&L
                if position.quantity > 0:  # Long position
                    realized_pnl = (exit_price - position.entry_price) * position.quantity * 100
                else:  # Short position
                    realized_pnl = (position.entry_price - exit_price) * abs(position.quantity) * 100
                
                realized_pnl_pct = (realized_pnl / (position.entry_price * abs(position.quantity) * 100)) * 100
                
                position.current_price = exit_price
                position.realized_pnl = realized_pnl
                position.realized_pnl_pct = realized_pnl_pct
                position.status = 'closed'
                position.close_reason = reason
                position.closed_at = datetime.now()
                
                db.commit()
            
            self.trade_logger.info(
                f"Position {position_id} closed - P&L: ${realized_pnl:.2f} ({realized_pnl_pct:.2f}%)"
            )
            
            return {
                'position_id': str(position_id),
                'exit_price': exit_price,
                'realized_pnl': realized_pnl,
                'realized_pnl_pct': realized_pnl_pct
            }
            
        except Exception as e:
            logger.error(f"Error closing position {position_id}: {e}")
            return None
    
    async def _is_market_open(self) -> bool:
        """Check if market is open."""
        try:
            clock = self.trading_client.get_clock()
            return clock.is_open
        except Exception as e:
            logger.error(f"Error checking market hours: {e}")
            return False
