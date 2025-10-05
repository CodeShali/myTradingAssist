/**
 * Authentication middleware
 */
import jwt from 'jsonwebtoken';
import { logger } from '../utils/logger.js';
import { query } from '../utils/db.js';

export const authMiddleware = async (req, res, next) => {
    try {
        const token = req.headers.authorization?.split(' ')[1];
        
        if (!token) {
            return res.status(401).json({ error: 'No token provided' });
        }
        
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        
        // Verify user exists and is active
        const result = await query(
            'SELECT id, username, email, is_active FROM users WHERE id = $1',
            [decoded.userId]
        );
        
        if (result.rows.length === 0) {
            return res.status(401).json({ error: 'User not found' });
        }
        
        const user = result.rows[0];
        
        if (!user.is_active) {
            return res.status(401).json({ error: 'User account is inactive' });
        }
        
        req.user = user;
        next();
        
    } catch (error) {
        if (error.name === 'JsonWebTokenError') {
            return res.status(401).json({ error: 'Invalid token' });
        }
        if (error.name === 'TokenExpiredError') {
            return res.status(401).json({ error: 'Token expired' });
        }
        
        logger.error('Auth middleware error:', error);
        res.status(500).json({ error: 'Authentication failed' });
    }
};

export const generateToken = (userId) => {
    return jwt.sign(
        { userId },
        process.env.JWT_SECRET,
        { expiresIn: '7d' }
    );
};
