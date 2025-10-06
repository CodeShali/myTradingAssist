import React from 'react';
import { Briefcase } from 'lucide-react';

const Positions = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Open Positions</h1>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
        <Briefcase className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">No Open Positions</h3>
        <p className="text-gray-600">Your active positions will appear here.</p>
      </div>
    </div>
  );
};

export default Positions;
