import express from 'express';
import { authMiddleware } from '../middleware/auth.js';
import { query } from '../utils/db.js';

const router = express.Router();

// Sync Alpaca positions - placeholder for now
router.post('/alpaca', authMiddleware, async (req, res, next) => {
    try {
        const userId = req.user.userId;
        
        // For now, return success - actual sync will be implemented in trading engine
        res.json({
            success: true,
            message: 'Sync initiated. This feature will be fully implemented soon.',
            user_id: userId
        });
    } catch (error) {
        next(error);
    }
});

// Get account info from database
router.get('/account', authMiddleware, async (req, res, next) => {
    try {
        const userId = req.user.userId;
        
        // Get user's positions summary
        const result = await query(
            `SELECT 
                COUNT(*) as total_positions,
                COALESCE(SUM(market_value), 0) as total_value,
                COALESCE(SUM(unrealized_pl), 0) as total_pnl
             FROM positions 
             WHERE user_id = $1 AND status = 'open'`,
            [userId]
        );
        
        res.json({
            total_positions: parseInt(result.rows[0]?.total_positions || 0),
            total_value: parseFloat(result.rows[0]?.total_value || 0),
            total_pnl: parseFloat(result.rows[0]?.total_pnl || 0)
        });
    } catch (error) {
        next(error);
    }
});

export default router;
