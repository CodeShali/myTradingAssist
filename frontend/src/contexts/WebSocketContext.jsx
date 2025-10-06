import React, { createContext, useContext, useEffect, useState } from 'react';
import websocketService from '../services/websocket';
import { useAuth } from './AuthContext';

const WebSocketContext = createContext(null);

export const WebSocketProvider = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const [connected, setConnected] = useState(false);
  const [events, setEvents] = useState([]);

  useEffect(() => {
    if (isAuthenticated) {
      websocketService.on('connect', () => setConnected(true));
      websocketService.on('disconnect', () => setConnected(false));
    }

    return () => {
      websocketService.off('connect');
      websocketService.off('disconnect');
    };
  }, [isAuthenticated]);

  const subscribe = (event, callback) => {
    websocketService.on(event, callback);
    return () => websocketService.off(event, callback);
  };

  const send = (event, data) => {
    websocketService.send(event, data);
  };

  const value = {
    connected,
    subscribe,
    send,
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within WebSocketProvider');
  }
  return context;
};

export default WebSocketContext;
