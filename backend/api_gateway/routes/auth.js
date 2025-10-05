/**
 * Authentication routes
 */
import express from 'express';
import bcrypt from 'bcrypt';
import { query } from '../utils/db.js';
import { generateToken } from '../middleware/auth.js';
import { logger } from '../utils/logger.js';

const router = express.Router();

// Register new user
router.post('/register', async (req, res, next) => {
    try {
        const { username, email, password } = req.body;
        
        // Validate input
        if (!username || !email || !password) {
            return res.status(400).json({ error: 'All fields are required' });
        }
        
        // Check if user exists
        const existing = await query(
            'SELECT id FROM users WHERE username = $1 OR email = $2',
            [username, email]
        );
        
        if (existing.rows.length > 0) {
            return res.status(400).json({ error: 'Username or email already exists' });
        }
        
        // Hash password
        const passwordHash = await bcrypt.hash(password, 10);
        
        // Create user
        const result = await query(
            `INSERT INTO users (username, email, password_hash) 
             VALUES ($1, $2, $3) 
             RETURNING id, username, email, created_at`,
            [username, email, passwordHash]
        );
        
        const user = result.rows[0];
        
        // Create default user config
        await query(
            `INSERT INTO user_configs (user_id) VALUES ($1)`,
            [user.id]
        );
        
        // Generate token
        const token = generateToken(user.id);
        
        logger.info(`New user registered: ${username}`);
        
        res.status(201).json({
            user: {
                id: user.id,
                username: user.username,
                email: user.email
            },
            token
        });
        
    } catch (error) {
        next(error);
    }
});

// Login
router.post('/login', async (req, res, next) => {
    try {
        const { username, password } = req.body;
        
        if (!username || !password) {
            return res.status(400).json({ error: 'Username and password are required' });
        }
        
        // Get user
        const result = await query(
            'SELECT * FROM users WHERE username = $1',
            [username]
        );
        
        if (result.rows.length === 0) {
            return res.status(401).json({ error: 'Invalid credentials' });
        }
        
        const user = result.rows[0];
        
        // Check if active
        if (!user.is_active) {
            return res.status(401).json({ error: 'Account is inactive' });
        }
        
        // Verify password
        const validPassword = await bcrypt.compare(password, user.password_hash);
        
        if (!validPassword) {
            return res.status(401).json({ error: 'Invalid credentials' });
        }
        
        // Generate token
        const token = generateToken(user.id);
        
        logger.info(`User logged in: ${username}`);
        
        res.json({
            user: {
                id: user.id,
                username: user.username,
                email: user.email,
                trading_mode: user.trading_mode
            },
            token
        });
        
    } catch (error) {
        next(error);
    }
});

// Verify token
router.get('/verify', async (req, res, next) => {
    try {
        const token = req.headers.authorization?.split(' ')[1];
        
        if (!token) {
            return res.status(401).json({ valid: false });
        }
        
        // This will throw if invalid
        const jwt = await import('jsonwebtoken');
        const decoded = jwt.default.verify(token, process.env.JWT_SECRET);
        
        res.json({ valid: true, userId: decoded.userId });
        
    } catch (error) {
        res.json({ valid: false });
    }
});

export default router;
