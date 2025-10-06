import { io } from 'socket.io-client';

const WS_URL = import.meta.env.VITE_WS_URL || 'http://localhost:3000';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.listeners = new Map();
  }

  connect(token) {
    if (this.socket?.connected) return;

    this.socket = io(WS_URL, {
      auth: { token },
      transports: ['websocket'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5,
    });

    this.socket.on('connect', () => {
      console.log('✅ WebSocket connected');
    });

    this.socket.on('disconnect', () => {
      console.log('❌ WebSocket disconnected');
    });

    this.socket.on('error', (error) => {
      console.error('WebSocket error:', error);
    });

    // Set up event listeners
    this.setupListeners();
  }

  setupListeners() {
    // Signal events
    this.socket.on('signal:new', (data) => this.emit('signal:new', data));
    this.socket.on('signal:updated', (data) => this.emit('signal:updated', data));
    
    // Position events
    this.socket.on('position:opened', (data) => this.emit('position:opened', data));
    this.socket.on('position:closed', (data) => this.emit('position:closed', data));
    this.socket.on('position:updated', (data) => this.emit('position:updated', data));
    
    // Market data events
    this.socket.on('market:quote', (data) => this.emit('market:quote', data));
    
    // Notification events
    this.socket.on('notification', (data) => this.emit('notification', data));
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  off(event, callback) {
    if (!this.listeners.has(event)) return;
    const callbacks = this.listeners.get(event);
    const index = callbacks.indexOf(callback);
    if (index > -1) {
      callbacks.splice(index, 1);
    }
  }

  emit(event, data) {
    if (!this.listeners.has(event)) return;
    this.listeners.get(event).forEach(callback => callback(data));
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
    this.listeners.clear();
  }

  // Send events to server
  send(event, data) {
    if (this.socket?.connected) {
      this.socket.emit(event, data);
    }
  }
}

export default new WebSocketService();
