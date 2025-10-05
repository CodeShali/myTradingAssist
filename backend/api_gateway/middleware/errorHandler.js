/**
 * Global error handler middleware
 */
import { logger } from '../utils/logger.js';

export const errorHandler = (err, req, res, next) => {
    logger.error('Error handler caught:', {
        error: err.message,
        stack: err.stack,
        path: req.path,
        method: req.method
    });
    
    // Default error
    let status = 500;
    let message = 'Internal server error';
    
    // Handle specific error types
    if (err.name === 'ValidationError') {
        status = 400;
        message = err.message;
    } else if (err.name === 'UnauthorizedError') {
        status = 401;
        message = 'Unauthorized';
    } else if (err.name === 'NotFoundError') {
        status = 404;
        message = err.message;
    }
    
    res.status(status).json({
        error: message,
        ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
    });
};
