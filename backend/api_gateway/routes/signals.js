/**
 * Signal routes
 */
import express from 'express';
import { query } from '../utils/db.js';
import { logger } from '../utils/logger.js';

const router = express.Router();

// Get pending signals for user
router.get('/pending', async (req, res, next) => {
    try {
        const userId = req.query.user_id || req.user.id;
        
        const result = await query(
            `SELECT * FROM trade_signals 
             WHERE user_id = $1 AND status = 'pending' 
             ORDER BY created_at DESC`,
            [userId]
        );
        
        res.json(result.rows);
    } catch (error) {
        next(error);
    }
});

// Get signal by ID
router.get('/:id', async (req, res, next) => {
    try {
        const { id } = req.params;
        
        const result = await query(
            `SELECT * FROM trade_signals WHERE id = $1`,
            [id]
        );
        
        if (result.rows.length === 0) {
            return res.status(404).json({ error: 'Signal not found' });
        }
        
        res.json(result.rows[0]);
    } catch (error) {
        next(error);
    }
});

// Confirm signal
router.post('/:id/confirm', async (req, res, next) => {
    try {
        const { id } = req.params;
        const { source } = req.body;
        
        // Update signal status
        const result = await query(
            `UPDATE trade_signals 
             SET status = 'confirmed', 
                 confirmation_source = $1,
                 confirmed_at = NOW(),
                 confirmed_by = $2
             WHERE id = $3 AND status = 'pending'
             RETURNING *`,
            [source || 'web', req.user.id, id]
        );
        
        if (result.rows.length === 0) {
            return res.status(400).json({ 
                success: false,
                error: 'Signal not found or already processed' 
            });
        }
        
        const signal = result.rows[0];
        
        logger.info(`Signal ${id} confirmed by user ${req.user.id} via ${source}`);
        
        // Trigger execution (in production, this would be handled by a queue)
        // For now, we'll just return success
        
        res.json({
            success: true,
            signal
        });
        
    } catch (error) {
        next(error);
    }
});

// Reject signal
router.post('/:id/reject', async (req, res, next) => {
    try {
        const { id } = req.params;
        const { source } = req.body;
        
        const result = await query(
            `UPDATE trade_signals 
             SET status = 'rejected',
                 confirmation_source = $1,
                 confirmed_at = NOW(),
                 confirmed_by = $2
             WHERE id = $3 AND status = 'pending'
             RETURNING *`,
            [source || 'web', req.user.id, id]
        );
        
        if (result.rows.length === 0) {
            return res.status(400).json({ 
                success: false,
                error: 'Signal not found or already processed' 
            });
        }
        
        logger.info(`Signal ${id} rejected by user ${req.user.id} via ${source}`);
        
        res.json({
            success: true,
            signal: result.rows[0]
        });
        
    } catch (error) {
        next(error);
    }
});

// Get signal history
router.get('/history', async (req, res, next) => {
    try {
        const userId = req.user.id;
        const limit = parseInt(req.query.limit) || 50;
        const offset = parseInt(req.query.offset) || 0;
        
        const result = await query(
            `SELECT * FROM trade_signals 
             WHERE user_id = $1 
             ORDER BY created_at DESC 
             LIMIT $2 OFFSET $3`,
            [userId, limit, offset]
        );
        
        res.json(result.rows);
    } catch (error) {
        next(error);
    }
});

export default router;
