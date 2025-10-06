import React from 'react';
import { TrendingUp } from 'lucide-react';

const Signals = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Trading Signals</h1>
        <button className="btn-primary">
          Refresh Signals
        </button>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
        <TrendingUp className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">No Active Signals</h3>
        <p className="text-gray-600">AI-generated signals will appear here when available.</p>
      </div>
    </div>
  );
};

export default Signals;
