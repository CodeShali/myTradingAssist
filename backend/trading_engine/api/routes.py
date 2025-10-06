"""
API routes for trading engine
"""
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import JSONResponse
from alpaca.trading.client import TradingClient
from config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Add CORS headers to all responses
@router.middleware("http")
async def add_cors_headers(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

# Initialize Alpaca client
trading_client = TradingClient(
    settings.alpaca_api_key,
    settings.alpaca_secret_key,
    paper=True
)

@router.get("/alpaca/account")
async def get_alpaca_account():
    """Get real Alpaca account data"""
    try:
        account = trading_client.get_account()
        positions = trading_client.get_all_positions()
        
        return {
            "equity": float(account.equity),
            "cash": float(account.cash),
            "buying_power": float(account.buying_power),
            "portfolio_value": float(account.portfolio_value),
            "positions_count": len(positions),
            "daytrade_count": account.daytrade_count,
            "pattern_day_trader": account.pattern_day_trader
        }
    except Exception as e:
        logger.error(f"Error fetching Alpaca account: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alpaca/positions")
async def get_alpaca_positions():
    """Get all positions from Alpaca"""
    try:
        positions = trading_client.get_all_positions()
        
        return [
            {
                "symbol": pos.symbol,
                "qty": int(pos.qty),
                "side": pos.side,
                "avg_entry_price": float(pos.avg_entry_price),
                "current_price": float(pos.current_price),
                "market_value": float(pos.market_value),
                "unrealized_pl": float(pos.unrealized_pl),
                "unrealized_plpc": float(pos.unrealized_plpc),
                "cost_basis": float(pos.cost_basis)
            }
            for pos in positions
        ]
    except Exception as e:
        logger.error(f"Error fetching Alpaca positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
