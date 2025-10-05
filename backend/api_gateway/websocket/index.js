/**
 * WebSocket setup for real-time updates
 */
import { createClient } from 'redis';
import { logger } from '../utils/logger.js';

export const setupWebSocket = (io) => {
    const redisClient = createClient({ url: process.env.REDIS_URL });
    
    redisClient.connect().then(() => {
        logger.info('WebSocket Redis client connected');
        
        // Subscribe to Redis channels
        const subscriber = redisClient.duplicate();
        subscriber.connect().then(() => {
            // Subscribe to all relevant channels
            subscriber.subscribe('signals:all', (message) => {
                try {
                    const signal = JSON.parse(message);
                    io.to(`user:${signal.user_id}`).emit('new_signal', signal);
                } catch (error) {
                    logger.error('Error broadcasting signal:', error);
                }
            });
            
            subscriber.pSubscribe('positions:*', (message, channel) => {
                try {
                    const update = JSON.parse(message);
                    io.to(`user:${update.user_id}`).emit('position_update', update);
                } catch (error) {
                    logger.error('Error broadcasting position update:', error);
                }
            });
            
            subscriber.pSubscribe('notifications:*', (message, channel) => {
                try {
                    const notification = JSON.parse(message);
                    io.to(`user:${notification.user_id}`).emit('notification', notification);
                } catch (error) {
                    logger.error('Error broadcasting notification:', error);
                }
            });
            
            logger.info('WebSocket subscribed to Redis channels');
        });
    });
    
    // Handle client connections
    io.on('connection', (socket) => {
        logger.info(`WebSocket client connected: ${socket.id}`);
        
        // Authenticate and join user room
        socket.on('authenticate', (data) => {
            const { userId } = data;
            if (userId) {
                socket.join(`user:${userId}`);
                logger.info(`Socket ${socket.id} joined room user:${userId}`);
                socket.emit('authenticated', { success: true });
            }
        });
        
        // Handle disconnection
        socket.on('disconnect', () => {
            logger.info(`WebSocket client disconnected: ${socket.id}`);
        });
        
        // Ping/pong for connection health
        socket.on('ping', () => {
            socket.emit('pong');
        });
    });
    
    logger.info('WebSocket server initialized');
};
