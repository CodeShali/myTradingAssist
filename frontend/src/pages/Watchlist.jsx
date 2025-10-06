import React from 'react';
import { Eye } from 'lucide-react';

const Watchlist = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Watchlist</h1>
        <button className="btn-primary">
          Add Symbol
        </button>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
        <Eye className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">No Symbols in Watchlist</h3>
        <p className="text-gray-600">Add symbols to track their options chains.</p>
      </div>
    </div>
  );
};

export default Watchlist;
