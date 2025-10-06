"""
Main entry point for the AI-Assisted Options Trading Engine.
"""
import asyncio
import signal
import sys
from typing import Optional
from loguru import logger
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from core import setup_logger, check_db_connection, redis_manager
from services.signal_generator import SignalGenerator
from services.position_manager import PositionManager
from services.market_data_service import MarketDataService
from services.execution_service import ExecutionService
from api.routes import router as api_router


class TradingEngine:
    """Main trading engine orchestrator."""
    
    def __init__(self):
        """Initialize trading engine."""
        self.running = False
        self.signal_generator: Optional[SignalGenerator] = None
        self.position_manager: Optional[PositionManager] = None
        self.market_data_service: Optional[MarketDataService] = None
        self.execution_service: Optional[ExecutionService] = None
        
    async def initialize(self):
        """Initialize all services."""
        logger.info("Initializing Trading Engine...")
        
        # Check database connection
        if not check_db_connection():
            logger.error("Database connection failed. Exiting.")
            sys.exit(1)
        
        # Check Redis connection
        if not redis_manager.ping():
            logger.error("Redis connection failed. Exiting.")
            sys.exit(1)
        
        # Initialize services
        try:
            self.market_data_service = MarketDataService()
            self.execution_service = ExecutionService()
            self.signal_generator = SignalGenerator(
                market_data_service=self.market_data_service
            )
            self.position_manager = PositionManager(
                execution_service=self.execution_service,
                market_data_service=self.market_data_service
            )
            
            logger.info("All services initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            raise
    
    async def start(self):
        """Start the trading engine."""
        logger.info("Starting Trading Engine...")
        logger.info(f"Trading Mode: {settings.trading_mode.upper()}")
        logger.info(f"Auto Trading: {'ENABLED' if settings.enable_auto_trading else 'DISABLED'}")
        
        self.running = True
        
        # Start background tasks
        tasks = [
            asyncio.create_task(self._signal_generation_loop()),
            asyncio.create_task(self._position_monitoring_loop()),
            asyncio.create_task(self._market_data_update_loop()),
            asyncio.create_task(self._health_check_loop()),
        ]
        
        logger.info("Trading Engine started successfully")
        
        # Wait for all tasks
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            logger.info("Tasks cancelled, shutting down...")
    
    async def stop(self):
        """Stop the trading engine."""
        logger.info("Stopping Trading Engine...")
        self.running = False
        
        # Give tasks time to finish current iteration
        await asyncio.sleep(2)
        
        logger.info("Trading Engine stopped")
    
    async def _signal_generation_loop(self):
        """Background task for generating trade signals."""
        logger.info("Signal generation loop started")
        
        while self.running:
            try:
                if settings.enable_auto_trading:
                    logger.debug("Running signal generation...")
                    await self.signal_generator.generate_signals()
                
                # Wait for next interval
                await asyncio.sleep(settings.signal_generation_interval)
                
            except Exception as e:
                logger.error(f"Error in signal generation loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _position_monitoring_loop(self):
        """Background task for monitoring open positions."""
        logger.info("Position monitoring loop started")
        
        while self.running:
            try:
                logger.debug("Monitoring positions...")
                await self.position_manager.monitor_positions()
                
                # Wait for next interval
                await asyncio.sleep(settings.position_update_interval)
                
            except Exception as e:
                logger.error(f"Error in position monitoring loop: {e}")
                await asyncio.sleep(10)  # Wait before retrying
    
    async def _market_data_update_loop(self):
        """Background task for updating market data."""
        logger.info("Market data update loop started")
        
        while self.running:
            try:
                logger.debug("Updating market data...")
                await self.market_data_service.update_market_data()
                
                # Wait for next interval (every minute)
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in market data update loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _health_check_loop(self):
        """Background task for health checks."""
        logger.info("Health check loop started")
        
        while self.running:
            try:
                # Check database
                db_healthy = check_db_connection()
                
                # Check Redis
                redis_healthy = redis_manager.ping()
                
                # Check external APIs
                api_healthy = await self.market_data_service.check_api_health()
                
                if not all([db_healthy, redis_healthy, api_healthy]):
                    logger.warning("Health check failed - some services are unhealthy")
                else:
                    logger.debug("Health check passed - all services healthy")
                
                # Wait for next check (every 5 minutes)
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(300)


async def main():
    """Main application entry point."""
    # Setup logger
    setup_logger()
    
    logger.info("=" * 80)
    logger.info("AI-Assisted Options Trading Platform")
    logger.info("=" * 80)
    
    # Create trading engine
    engine = TradingEngine()
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}, initiating shutdown...")
        asyncio.create_task(engine.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize and start
        await engine.initialize()
        await engine.start()
        
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
    finally:
        await engine.stop()
        logger.info("Trading Engine shutdown complete")


def create_app() -> FastAPI:
    """Create FastAPI application"""
    app = FastAPI(title="Trading Engine API")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(api_router)
    
    return app

app = create_app()

if __name__ == "__main__":
    # Run both FastAPI server and trading engine
    import threading
    
    # Start FastAPI server in a separate thread
    def run_api():
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    
    # Run trading engine in main thread
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
    except Exception as e:
        logger.error(f"Application crashed: {e}")
        sys.exit(1)
