import React from 'react';
import { TrendingUp, TrendingDown, Clock, Zap } from 'lucide-react';

const RecentSignals = ({ signals }) => {
  return (
    <div className="bg-gray-800/50 backdrop-blur-xl rounded-2xl p-6 border border-gray-700/50 shadow-xl">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-blue-600/20 rounded-lg">
            <Zap className="w-5 h-5 text-blue-400" />
          </div>
          <h3 className="text-lg font-semibold text-white">Recent Signals</h3>
        </div>
        <button className="text-sm text-blue-400 hover:text-blue-300 font-medium transition-colors">
          View All
        </button>
      </div>
      
      <div className="space-y-3">
        {signals && signals.length > 0 ? (
          signals.map((signal, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-4 bg-gray-700/30 rounded-xl hover:bg-gray-700/50 transition-all duration-200 cursor-pointer group"
            >
              <div className="flex items-center space-x-4">
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                  signal.type === 'CALL' ? 'bg-green-500/20' : 'bg-red-500/20'
                }`}>
                  {signal.type === 'CALL' ? (
                    <TrendingUp className="w-6 h-6 text-green-400" />
                  ) : (
                    <TrendingDown className="w-6 h-6 text-red-400" />
                  )}
                </div>
                
                <div>
                  <div className="flex items-center space-x-2">
                    <h4 className="text-white font-semibold">{signal.symbol}</h4>
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                      signal.type === 'CALL' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                    }`}>
                      {signal.type}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2 mt-1">
                    <p className="text-gray-400 text-sm">Strike: ${signal.strike}</p>
                    <span className="text-gray-600">•</span>
                    <p className="text-gray-400 text-sm">{signal.expiry}</p>
                  </div>
                </div>
              </div>
              
              <div className="text-right">
                <div className="flex items-center space-x-2 mb-1">
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                  <p className="text-sm font-semibold text-blue-400">{signal.confidence}%</p>
                </div>
                <div className="flex items-center space-x-1 text-gray-400 text-xs">
                  <Clock className="w-3 h-3" />
                  <span>{signal.time}</span>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-8">
            <Zap className="w-12 h-12 text-gray-600 mx-auto mb-3" />
            <p className="text-gray-400">No signals yet</p>
            <p className="text-gray-500 text-sm mt-1">AI is analyzing the market...</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default RecentSignals;
