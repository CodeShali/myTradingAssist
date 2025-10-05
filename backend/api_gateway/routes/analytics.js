/**
 * Analytics routes
 */
import express from 'express';
import { query } from '../utils/db.js';

const router = express.Router();

// Get P&L summary
router.get('/pnl', async (req, res, next) => {
    try {
        const userId = req.query.user_id || req.user.id;
        
        // Get open positions
        const openPositions = await query(
            `SELECT COUNT(*) as count, SUM(unrealized_pnl) as total_unrealized 
             FROM positions 
             WHERE user_id = $1 AND status = 'open'`,
            [userId]
        );
        
        // Get today's closed positions
        const closedToday = await query(
            `SELECT COUNT(*) as count, SUM(realized_pnl) as total_realized 
             FROM positions 
             WHERE user_id = $1 AND status = 'closed' 
             AND closed_at >= CURRENT_DATE`,
            [userId]
        );
        
        // Get today's trades
        const tradesToday = await query(
            `SELECT COUNT(*) as count 
             FROM trade_signals 
             WHERE user_id = $1 
             AND created_at >= CURRENT_DATE 
             AND status IN ('confirmed', 'executed')`,
            [userId]
        );
        
        res.json({
            open_positions: parseInt(openPositions.rows[0].count) || 0,
            total_unrealized_pnl: parseFloat(openPositions.rows[0].total_unrealized) || 0,
            daily_realized_pnl: parseFloat(closedToday.rows[0].total_realized) || 0,
            trades_today: parseInt(tradesToday.rows[0].count) || 0
        });
        
    } catch (error) {
        next(error);
    }
});

// Get performance metrics
router.get('/performance', async (req, res, next) => {
    try {
        const userId = req.user.id;
        const period = req.query.period || 'all_time';
        
        const result = await query(
            `SELECT * FROM performance_metrics 
             WHERE user_id = $1 AND period_type = $2 
             ORDER BY period_start DESC 
             LIMIT 1`,
            [userId, period]
        );
        
        if (result.rows.length === 0) {
            return res.json({
                total_trades: 0,
                winning_trades: 0,
                losing_trades: 0,
                win_rate: 0,
                total_pnl: 0
            });
        }
        
        res.json(result.rows[0]);
    } catch (error) {
        next(error);
    }
});

// Get trade history
router.get('/trade-history', async (req, res, next) => {
    try {
        const userId = req.user.id;
        const limit = parseInt(req.query.limit) || 50;
        const offset = parseInt(req.query.offset) || 0;
        
        const result = await query(
            `SELECT 
                p.*,
                ts.strategy_type,
                ts.confidence_score
             FROM positions p
             LEFT JOIN trade_signals ts ON p.signal_id = ts.id
             WHERE p.user_id = $1 AND p.status = 'closed'
             ORDER BY p.closed_at DESC
             LIMIT $2 OFFSET $3`,
            [userId, limit, offset]
        );
        
        res.json(result.rows);
    } catch (error) {
        next(error);
    }
});

// Get strategy performance breakdown
router.get('/strategy-performance', async (req, res, next) => {
    try {
        const userId = req.user.id;
        
        const result = await query(
            `SELECT 
                strategy_type,
                COUNT(*) as total_trades,
                SUM(CASE WHEN realized_pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                SUM(realized_pnl) as total_pnl,
                AVG(realized_pnl) as avg_pnl,
                AVG(realized_pnl_pct) as avg_pnl_pct
             FROM positions
             WHERE user_id = $1 AND status = 'closed'
             GROUP BY strategy_type
             ORDER BY total_pnl DESC`,
            [userId]
        );
        
        res.json(result.rows);
    } catch (error) {
        next(error);
    }
});

// Get equity curve data
router.get('/equity-curve', async (req, res, next) => {
    try {
        const userId = req.user.id;
        const days = parseInt(req.query.days) || 30;
        
        const result = await query(
            `SELECT 
                DATE(closed_at) as date,
                SUM(realized_pnl) as daily_pnl,
                SUM(SUM(realized_pnl)) OVER (ORDER BY DATE(closed_at)) as cumulative_pnl
             FROM positions
             WHERE user_id = $1 
             AND status = 'closed'
             AND closed_at >= CURRENT_DATE - INTERVAL '${days} days'
             GROUP BY DATE(closed_at)
             ORDER BY date`,
            [userId]
        );
        
        res.json(result.rows);
    } catch (error) {
        next(error);
    }
});

export default router;
