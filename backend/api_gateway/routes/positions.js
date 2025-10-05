/**
 * Position routes
 */
import express from 'express';
import { query } from '../utils/db.js';
import { logger } from '../utils/logger.js';

const router = express.Router();

// Get all positions for user
router.get('/', async (req, res, next) => {
    try {
        const userId = req.query.user_id || req.user.id;
        const status = req.query.status || 'open';
        
        const result = await query(
            `SELECT * FROM positions 
             WHERE user_id = $1 AND status = $2 
             ORDER BY opened_at DESC`,
            [userId, status]
        );
        
        // Calculate portfolio summary
        const positions = result.rows;
        const totalUnrealizedPnl = positions.reduce((sum, p) => sum + (parseFloat(p.unrealized_pnl) || 0), 0);
        
        // Get today's closed positions
        const closedToday = await query(
            `SELECT * FROM positions 
             WHERE user_id = $1 AND status = 'closed' 
             AND closed_at >= CURRENT_DATE 
             ORDER BY closed_at DESC`,
            [userId]
        );
        
        const dailyRealizedPnl = closedToday.rows.reduce((sum, p) => sum + (parseFloat(p.realized_pnl) || 0), 0);
        
        res.json({
            open_positions: positions.length,
            total_unrealized_pnl: totalUnrealizedPnl,
            daily_realized_pnl: dailyRealizedPnl,
            positions: positions
        });
        
    } catch (error) {
        next(error);
    }
});

// Get position by ID
router.get('/:id', async (req, res, next) => {
    try {
        const { id } = req.params;
        
        const result = await query(
            `SELECT * FROM positions WHERE id = $1`,
            [id]
        );
        
        if (result.rows.length === 0) {
            return res.status(404).json({ error: 'Position not found' });
        }
        
        res.json(result.rows[0]);
    } catch (error) {
        next(error);
    }
});

// Get position history
router.get('/:id/history', async (req, res, next) => {
    try {
        const { id } = req.params;
        
        const result = await query(
            `SELECT * FROM position_history 
             WHERE position_id = $1 
             ORDER BY snapshot_at DESC 
             LIMIT 100`,
            [id]
        );
        
        res.json(result.rows);
    } catch (error) {
        next(error);
    }
});

// Close position manually
router.post('/:id/close', async (req, res, next) => {
    try {
        const { id } = req.params;
        
        // Verify position belongs to user
        const posResult = await query(
            `SELECT * FROM positions WHERE id = $1 AND user_id = $2`,
            [id, req.user.id]
        );
        
        if (posResult.rows.length === 0) {
            return res.status(404).json({ error: 'Position not found' });
        }
        
        const position = posResult.rows[0];
        
        if (position.status !== 'open') {
            return res.status(400).json({ error: 'Position is not open' });
        }
        
        logger.info(`Manual close requested for position ${id} by user ${req.user.id}`);
        
        // In production, this would trigger the execution service
        // For now, return success
        res.json({
            success: true,
            message: 'Close order submitted',
            position_id: id
        });
        
    } catch (error) {
        next(error);
    }
});

// Update position exit parameters
router.patch('/:id/exit-params', async (req, res, next) => {
    try {
        const { id } = req.params;
        const { profit_target_pct, stop_loss_pct, trailing_stop_pct } = req.body;
        
        // Build update query dynamically
        const updates = [];
        const values = [];
        let paramCount = 1;
        
        if (profit_target_pct !== undefined) {
            updates.push(`profit_target_pct = $${paramCount++}`);
            values.push(profit_target_pct);
        }
        
        if (stop_loss_pct !== undefined) {
            updates.push(`stop_loss_pct = $${paramCount++}`);
            values.push(stop_loss_pct);
        }
        
        if (trailing_stop_pct !== undefined) {
            updates.push(`trailing_stop_pct = $${paramCount++}`);
            values.push(trailing_stop_pct);
        }
        
        if (updates.length === 0) {
            return res.status(400).json({ error: 'No updates provided' });
        }
        
        values.push(id, req.user.id);
        
        const result = await query(
            `UPDATE positions 
             SET ${updates.join(', ')} 
             WHERE id = $${paramCount++} AND user_id = $${paramCount++} AND status = 'open'
             RETURNING *`,
            values
        );
        
        if (result.rows.length === 0) {
            return res.status(404).json({ error: 'Position not found or not open' });
        }
        
        logger.info(`Exit parameters updated for position ${id}`);
        
        res.json({
            success: true,
            position: result.rows[0]
        });
        
    } catch (error) {
        next(error);
    }
});

// Get portfolio Greeks
router.get('/portfolio/greeks', async (req, res, next) => {
    try {
        const userId = req.user.id;
        
        const result = await query(
            `SELECT 
                SUM(delta) as total_delta,
                SUM(gamma) as total_gamma,
                SUM(theta) as total_theta,
                SUM(vega) as total_vega
             FROM positions 
             WHERE user_id = $1 AND status = 'open'`,
            [userId]
        );
        
        res.json(result.rows[0]);
    } catch (error) {
        next(error);
    }
});

export default router;
