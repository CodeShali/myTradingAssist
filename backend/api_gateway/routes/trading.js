/**
 * Trading control routes
 */
import express from 'express';
import { createClient } from 'redis';
import { logger } from '../utils/logger.js';

const router = express.Router();
const redisClient = createClient({ url: process.env.REDIS_URL });
await redisClient.connect();

// Pause trading for user
router.post('/pause', async (req, res, next) => {
    try {
        const userId = req.body.user_id || req.user.id;
        
        // Set pause flag in Redis
        await redisClient.set(`trading:paused:${userId}`, 'true', {
            EX: 86400 * 7 // 7 days expiration
        });
        
        logger.info(`Trading paused for user ${userId}`);
        
        res.json({ success: true, message: 'Trading paused' });
    } catch (error) {
        next(error);
    }
});

// Resume trading for user
router.post('/resume', async (req, res, next) => {
    try {
        const userId = req.body.user_id || req.user.id;
        
        // Remove pause flag
        await redisClient.del(`trading:paused:${userId}`);
        
        logger.info(`Trading resumed for user ${userId}`);
        
        res.json({ success: true, message: 'Trading resumed' });
    } catch (error) {
        next(error);
    }
});

// Get trading status
router.get('/status', async (req, res, next) => {
    try {
        const userId = req.user.id;
        
        const isPaused = await redisClient.get(`trading:paused:${userId}`);
        
        res.json({
            is_paused: isPaused === 'true',
            trading_active: isPaused !== 'true'
        });
    } catch (error) {
        next(error);
    }
});

export default router;
