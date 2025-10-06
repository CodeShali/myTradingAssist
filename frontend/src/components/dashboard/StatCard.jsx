import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

const StatCard = ({ title, value, change, changeType, icon: Icon, gradient }) => {
  const isPositive = changeType === 'positive';
  
  return (
    <div className={`relative overflow-hidden rounded-2xl bg-gradient-to-br ${gradient} p-6 shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1`}>
      {/* Background decoration */}
      <div className="absolute top-0 right-0 -mt-4 -mr-4 h-24 w-24 rounded-full bg-white/10 blur-2xl"></div>
      
      <div className="relative">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-white/20 rounded-xl backdrop-blur-sm">
              <Icon className="w-6 h-6 text-white" />
            </div>
            <h3 className="text-sm font-medium text-white/80">{title}</h3>
          </div>
        </div>
        
        <div className="space-y-2">
          <p className="text-3xl font-bold text-white">{value}</p>
          
          {change && (
            <div className={`flex items-center space-x-1 text-sm font-medium ${
              isPositive ? 'text-green-300' : 'text-red-300'
            }`}>
              {isPositive ? (
                <TrendingUp className="w-4 h-4" />
              ) : (
                <TrendingDown className="w-4 h-4" />
              )}
              <span>{change}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StatCard;
