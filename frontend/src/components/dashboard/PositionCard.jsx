import React from 'react';
import { TrendingUp, TrendingDown, DollarSign } from 'lucide-react';

const PositionCard = ({ symbol, quantity, entryPrice, currentPrice, pnl, pnlPercent }) => {
  const isProfit = pnl >= 0;
  
  return (
    <div className="bg-gray-800/50 backdrop-blur-xl rounded-xl p-4 border border-gray-700/50 hover:border-gray-600 transition-all duration-300 hover:shadow-lg">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-3">
          <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
            isProfit ? 'bg-green-500/20' : 'bg-red-500/20'
          }`}>
            <span className="text-lg font-bold text-white">{symbol.charAt(0)}</span>
          </div>
          <div>
            <h4 className="text-white font-semibold">{symbol}</h4>
            <p className="text-gray-400 text-sm">{quantity} contracts</p>
          </div>
        </div>
        
        <div className={`flex items-center space-x-1 px-3 py-1 rounded-lg ${
          isProfit ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
        }`}>
          {isProfit ? (
            <TrendingUp className="w-4 h-4" />
          ) : (
            <TrendingDown className="w-4 h-4" />
          )}
          <span className="text-sm font-semibold">{pnlPercent}%</span>
        </div>
      </div>
      
      <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-gray-700/50">
        <div>
          <p className="text-gray-400 text-xs mb-1">Entry</p>
          <p className="text-white font-semibold text-sm">${entryPrice}</p>
        </div>
        <div>
          <p className="text-gray-400 text-xs mb-1">Current</p>
          <p className="text-white font-semibold text-sm">${currentPrice}</p>
        </div>
        <div>
          <p className="text-gray-400 text-xs mb-1">P&L</p>
          <p className={`font-semibold text-sm ${isProfit ? 'text-green-400' : 'text-red-400'}`}>
            ${Math.abs(pnl).toLocaleString()}
          </p>
        </div>
      </div>
    </div>
  );
};

export default PositionCard;
