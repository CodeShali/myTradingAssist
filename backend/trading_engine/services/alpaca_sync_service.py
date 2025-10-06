"""
Service to sync Alpaca account data with local database
"""
import logging
from typing import List, Dict, Any
from datetime import datetime
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass
from core.database import get_db_context
from core.models import Position, User
from core.config import settings
import uuid

logger = logging.getLogger(__name__)

class AlpacaSyncService:
    """Service to sync Alpaca account data with database."""
    
    def __init__(self):
        self.trading_client = TradingClient(
            settings.alpaca_api_key,
            settings.alpaca_secret_key,
            paper=True
        )
        logger.info("Alpaca sync service initialized")
    
    async def sync_account_positions(self, user_id: uuid.UUID):
        """
        Sync all positions from Alpaca account to database.
        
        Args:
            user_id: User ID to associate positions with
        """
        try:
            # Get account info
            account = self.trading_client.get_account()
            logger.info(f"Account equity: ${account.equity}")
            logger.info(f"Account cash: ${account.cash}")
            
            # Get all open positions from Alpaca
            alpaca_positions = self.trading_client.get_all_positions()
            logger.info(f"Found {len(alpaca_positions)} positions in Alpaca account")
            
            if not alpaca_positions:
                logger.info("No positions to sync")
                return {
                    'synced': 0,
                    'account_value': float(account.equity),
                    'cash': float(account.cash)
                }
            
            synced_count = 0
            
            with get_db_context() as db:
                for alpaca_pos in alpaca_positions:
                    # Check if position already exists
                    existing = db.query(Position).filter(
                        Position.user_id == user_id,
                        Position.symbol == alpaca_pos.symbol,
                        Position.status == 'open'
                    ).first()
                    
                    if existing:
                        # Update existing position
                        existing.quantity = int(alpaca_pos.qty)
                        existing.current_price = float(alpaca_pos.current_price)
                        existing.market_value = float(alpaca_pos.market_value)
                        existing.unrealized_pl = float(alpaca_pos.unrealized_pl)
                        existing.unrealized_plpc = float(alpaca_pos.unrealized_plpc)
                        existing.updated_at = datetime.utcnow()
                        logger.info(f"Updated position: {alpaca_pos.symbol}")
                    else:
                        # Create new position
                        new_position = Position(
                            id=uuid.uuid4(),
                            user_id=user_id,
                            symbol=alpaca_pos.symbol,
                            quantity=int(alpaca_pos.qty),
                            entry_price=float(alpaca_pos.avg_entry_price),
                            current_price=float(alpaca_pos.current_price),
                            market_value=float(alpaca_pos.market_value),
                            unrealized_pl=float(alpaca_pos.unrealized_pl),
                            unrealized_plpc=float(alpaca_pos.unrealized_plpc),
                            status='open',
                            side=alpaca_pos.side,
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                        db.add(new_position)
                        logger.info(f"Created new position: {alpaca_pos.symbol}")
                    
                    synced_count += 1
                
                db.commit()
            
            logger.info(f"Successfully synced {synced_count} positions")
            
            return {
                'synced': synced_count,
                'account_value': float(account.equity),
                'cash': float(account.cash),
                'positions': [
                    {
                        'symbol': pos.symbol,
                        'qty': pos.qty,
                        'current_price': float(pos.current_price),
                        'unrealized_pl': float(pos.unrealized_pl)
                    }
                    for pos in alpaca_positions
                ]
            }
            
        except Exception as e:
            logger.error(f"Error syncing Alpaca positions: {e}")
            raise
    
    def get_account_summary(self) -> Dict[str, Any]:
        """Get Alpaca account summary."""
        try:
            account = self.trading_client.get_account()
            
            return {
                'equity': float(account.equity),
                'cash': float(account.cash),
                'buying_power': float(account.buying_power),
                'portfolio_value': float(account.portfolio_value),
                'last_equity': float(account.last_equity),
                'daytrade_count': account.daytrade_count,
                'pattern_day_trader': account.pattern_day_trader
            }
        except Exception as e:
            logger.error(f"Error getting account summary: {e}")
            return {}
