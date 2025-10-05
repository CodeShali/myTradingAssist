/**
 * User routes
 */
import express from 'express';
import { query } from '../utils/db.js';
import { logger } from '../utils/logger.js';

const router = express.Router();

// Get user profile
router.get('/profile', async (req, res, next) => {
    try {
        const result = await query(
            `SELECT id, username, email, discord_user_id, trading_mode, created_at 
             FROM users WHERE id = $1`,
            [req.user.id]
        );
        
        res.json(result.rows[0]);
    } catch (error) {
        next(error);
    }
});

// Get user configuration
router.get('/:userId/config', async (req, res, next) => {
    try {
        const userId = req.params.userId === 'me' ? req.user.id : req.params.userId;
        
        const result = await query(
            `SELECT * FROM user_configs 
             WHERE user_id = $1 
             ORDER BY version DESC 
             LIMIT 1`,
            [userId]
        );
        
        if (result.rows.length === 0) {
            return res.status(404).json({ error: 'Configuration not found' });
        }
        
        res.json(result.rows[0]);
    } catch (error) {
        next(error);
    }
});

// Update user configuration
router.put('/config', async (req, res, next) => {
    try {
        const {
            max_position_size_pct,
            max_daily_trades,
            default_profit_target_pct,
            default_stop_loss_pct,
            max_portfolio_delta,
            max_portfolio_gamma,
            max_portfolio_vega,
            max_concentration_pct,
            min_option_volume,
            min_open_interest,
            max_bid_ask_spread_pct,
            min_liquidity_score,
            allowed_strategies,
            allowed_expirations,
            auto_sell_enabled,
            trailing_stop_enabled,
            news_sentiment_enabled,
            discord_notifications_enabled,
            web_notifications_enabled
        } = req.body;
        
        // Get current version
        const currentConfig = await query(
            `SELECT version FROM user_configs 
             WHERE user_id = $1 
             ORDER BY version DESC 
             LIMIT 1`,
            [req.user.id]
        );
        
        const newVersion = currentConfig.rows.length > 0 ? currentConfig.rows[0].version + 1 : 1;
        
        // Insert new version
        const result = await query(
            `INSERT INTO user_configs (
                user_id, version,
                max_position_size_pct, max_daily_trades,
                default_profit_target_pct, default_stop_loss_pct,
                max_portfolio_delta, max_portfolio_gamma, max_portfolio_vega,
                max_concentration_pct,
                min_option_volume, min_open_interest,
                max_bid_ask_spread_pct, min_liquidity_score,
                allowed_strategies, allowed_expirations,
                auto_sell_enabled, trailing_stop_enabled,
                news_sentiment_enabled, discord_notifications_enabled,
                web_notifications_enabled
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
                $11, $12, $13, $14, $15, $16, $17, $18,
                $19, $20, $21
            ) RETURNING *`,
            [
                req.user.id, newVersion,
                max_position_size_pct, max_daily_trades,
                default_profit_target_pct, default_stop_loss_pct,
                max_portfolio_delta, max_portfolio_gamma, max_portfolio_vega,
                max_concentration_pct,
                min_option_volume, min_open_interest,
                max_bid_ask_spread_pct, min_liquidity_score,
                JSON.stringify(allowed_strategies), JSON.stringify(allowed_expirations),
                auto_sell_enabled, trailing_stop_enabled,
                news_sentiment_enabled, discord_notifications_enabled,
                web_notifications_enabled
            ]
        );
        
        logger.info(`User ${req.user.id} updated configuration to version ${newVersion}`);
        
        res.json(result.rows[0]);
    } catch (error) {
        next(error);
    }
});

// Link Discord account
router.post('/link-discord', async (req, res, next) => {
    try {
        const { discord_user_id } = req.body;
        
        if (!discord_user_id) {
            return res.status(400).json({ error: 'Discord user ID is required' });
        }
        
        // Check if Discord ID is already linked
        const existing = await query(
            'SELECT id FROM users WHERE discord_user_id = $1 AND id != $2',
            [discord_user_id, req.user.id]
        );
        
        if (existing.rows.length > 0) {
            return res.status(400).json({ error: 'Discord account already linked to another user' });
        }
        
        // Update user
        await query(
            'UPDATE users SET discord_user_id = $1 WHERE id = $2',
            [discord_user_id, req.user.id]
        );
        
        logger.info(`User ${req.user.id} linked Discord account ${discord_user_id}`);
        
        res.json({ success: true });
    } catch (error) {
        next(error);
    }
});

// Get user by Discord ID
router.get('/by-discord/:discordId', async (req, res, next) => {
    try {
        const result = await query(
            'SELECT id, username FROM users WHERE discord_user_id = $1',
            [req.params.discordId]
        );
        
        if (result.rows.length === 0) {
            return res.status(404).json({ error: 'User not found' });
        }
        
        res.json({ user_id: result.rows[0].id });
    } catch (error) {
        next(error);
    }
});

// Get Discord ID for user
router.get('/:userId/discord', async (req, res, next) => {
    try {
        const result = await query(
            'SELECT discord_user_id FROM users WHERE id = $1',
            [req.params.userId]
        );
        
        if (result.rows.length === 0) {
            return res.status(404).json({ error: 'User not found' });
        }
        
        res.json({ discord_user_id: result.rows[0].discord_user_id });
    } catch (error) {
        next(error);
    }
});

// Get/Update watchlist
router.get('/watchlist', async (req, res, next) => {
    try {
        const result = await query(
            `SELECT * FROM watchlists 
             WHERE user_id = $1 AND is_active = true 
             ORDER BY created_at DESC`,
            [req.user.id]
        );
        
        res.json(result.rows);
    } catch (error) {
        next(error);
    }
});

router.post('/watchlist', async (req, res, next) => {
    try {
        const { symbol, notes } = req.body;
        
        if (!symbol) {
            return res.status(400).json({ error: 'Symbol is required' });
        }
        
        // Check if already exists
        const existing = await query(
            'SELECT id FROM watchlists WHERE user_id = $1 AND symbol = $2',
            [req.user.id, symbol.toUpperCase()]
        );
        
        if (existing.rows.length > 0) {
            return res.status(400).json({ error: 'Symbol already in watchlist' });
        }
        
        const result = await query(
            `INSERT INTO watchlists (user_id, symbol, notes) 
             VALUES ($1, $2, $3) 
             RETURNING *`,
            [req.user.id, symbol.toUpperCase(), notes]
        );
        
        logger.info(`User ${req.user.id} added ${symbol} to watchlist`);
        
        res.status(201).json(result.rows[0]);
    } catch (error) {
        next(error);
    }
});

router.delete('/watchlist/:symbol', async (req, res, next) => {
    try {
        await query(
            'UPDATE watchlists SET is_active = false WHERE user_id = $1 AND symbol = $2',
            [req.user.id, req.params.symbol.toUpperCase()]
        );
        
        logger.info(`User ${req.user.id} removed ${req.params.symbol} from watchlist`);
        
        res.json({ success: true });
    } catch (error) {
        next(error);
    }
});

export default router;
