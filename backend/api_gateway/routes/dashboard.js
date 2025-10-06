import express from 'express';
import { query } from '../utils/db.js';
import { authMiddleware } from '../middleware/auth.js';

const router = express.Router();

// Get dashboard stats - REAL DATA ONLY
router.get('/stats', authMiddleware, async (req, res, next) => {
    try {
        const userId = req.user.userId;
        
        // Get REAL Alpaca account data via trading engine
        let alpacaData = {
            equity: 0,
            cash: 0,
            positions_count: 0
        };
        
        try {
            // Fetch from trading engine's Alpaca connection
            const fetch = (await import('node-fetch')).default;
            const response = await fetch('http://trading_engine:8000/alpaca/account');
            if (response.ok) {
                alpacaData = await response.json();
            }
        } catch (error) {
            console.error('Failed to fetch Alpaca data:', error);
        }
        
        // Get today's trades
        const tradesResult = await query(
            `SELECT COUNT(*) as today_trades
             FROM executions 
             WHERE user_id = $1 AND DATE(filled_at) = CURRENT_DATE`,
            [userId]
        );
        
        // Get pending signals
        const signalsResult = await query(
            `SELECT COUNT(*) as pending_signals
             FROM trade_signals 
             WHERE user_id = $1 AND status = 'pending'`,
            [userId]
        );
        
        // Get watchlist count
        const watchlistResult = await query(
            `SELECT COUNT(*) as watchlist_count
             FROM watchlists 
             WHERE user_id = $1 AND is_active = true`,
            [userId]
        );
        
        // Calculate real P&L: current equity - initial investment (100k for paper account)
        const initialBalance = 100000;
        const currentEquity = parseFloat(alpacaData.equity || 0);
        const realPnL = currentEquity - initialBalance;
        
        const stats = {
            portfolioValue: currentEquity,
            totalPnL: realPnL,
            activePositions: parseInt(alpacaData.positions_count || 0),
            todayTrades: parseInt(tradesResult.rows[0]?.today_trades || 0),
            pendingSignals: parseInt(signalsResult.rows[0]?.pending_signals || 0),
            watchlistCount: parseInt(watchlistResult.rows[0]?.watchlist_count || 0),
        };
        
        res.json(stats);
    } catch (error) {
        next(error);
    }
});

// Get positions from Alpaca
router.get('/positions', authMiddleware, async (req, res, next) => {
    try {
        // Fetch positions from trading engine
        const fetch = (await import('node-fetch')).default;
        const response = await fetch('http://trading_engine:8000/alpaca/positions');
        
        if (response.ok) {
            const positions = await response.json();
            res.json(positions);
        } else {
            res.json([]);
        }
    } catch (error) {
        console.error('Failed to fetch positions:', error);
        res.json([]);
    }
});

// Get recent activity
router.get('/activity', authMiddleware, async (req, res, next) => {
    try {
        const userId = req.user.userId;
        const limit = parseInt(req.query.limit) || 10;
        
        const result = await query(
            `SELECT 
                'signal' as type,
                symbol,
                signal_type as action,
                confidence_score,
                created_at as timestamp
             FROM trade_signals 
             WHERE user_id = $1
             UNION ALL
             SELECT 
                'execution' as type,
                'N/A' as symbol,
                side as action,
                NULL as confidence_score,
                filled_at as timestamp
             FROM executions 
             WHERE user_id = $1
             ORDER BY timestamp DESC
             LIMIT $2`,
            [userId, limit]
        );
        
        res.json(result.rows);
    } catch (error) {
        next(error);
    }
});

// Get performance metrics
router.get('/performance', authMiddleware, async (req, res, next) => {
    try {
        const userId = req.user.userId;
        
        const result = await query(
            `SELECT 
                DATE(created_at) as date,
                COUNT(*) as trades,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losses,
                SUM(pnl) as total_pnl
             FROM position_history 
             WHERE user_id = $1 
             AND created_at >= CURRENT_DATE - INTERVAL '30 days'
             GROUP BY DATE(created_at)
             ORDER BY date DESC`,
            [userId]
        );
        
        res.json(result.rows);
    } catch (error) {
        next(error);
    }
});

export default router;
