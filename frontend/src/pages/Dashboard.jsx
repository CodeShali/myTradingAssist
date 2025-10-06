import React, { useEffect, useState } from 'react';
import { TrendingUp, TrendingDown, DollarSign, Activity, AlertCircle } from 'lucide-react';
import { dashboardAPI } from '../services/api';
import { formatCurrency, formatPercent, formatPnL, getPnLColorClass } from '../utils/formatters';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const response = await dashboardAPI.getStats();
      setStats(response.data);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const statCards = [
    {
      title: 'Total P&L',
      value: stats?.totalPnL || 0,
      format: 'currency',
      icon: DollarSign,
      color: stats?.totalPnL >= 0 ? 'green' : 'red',
    },
    {
      title: 'Today\'s P&L',
      value: stats?.todayPnL || 0,
      format: 'currency',
      icon: TrendingUp,
      color: stats?.todayPnL >= 0 ? 'green' : 'red',
    },
    {
      title: 'Open Positions',
      value: stats?.openPositions || 0,
      format: 'number',
      icon: Activity,
      color: 'blue',
    },
    {
      title: 'Win Rate',
      value: stats?.winRate || 0,
      format: 'percent',
      icon: TrendingUp,
      color: 'purple',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => (
          <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">{stat.title}</p>
                <p className={`text-2xl font-bold mt-2 ${
                  stat.format === 'currency' ? getPnLColorClass(stat.value) : 'text-gray-900'
                }`}>
                  {stat.format === 'currency' && formatPnL(stat.value)}
                  {stat.format === 'number' && stat.value}
                  {stat.format === 'percent' && formatPercent(stat.value / 100)}
                </p>
              </div>
              <div className={`w-12 h-12 rounded-lg flex items-center justify-center bg-${stat.color}-50`}>
                <stat.icon className={`w-6 h-6 text-${stat.color}-600`} />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Signals */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Signals</h3>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">AAPL 150 Call</p>
                  <p className="text-sm text-gray-500">5 minutes ago</p>
                </div>
                <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                  Bullish
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Open Positions */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Open Positions</h3>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">TSLA 200 Put</p>
                  <p className="text-sm text-gray-500">Opened 2 hours ago</p>
                </div>
                <div className="text-right">
                  <p className="font-medium text-green-600">+$245.50</p>
                  <p className="text-sm text-gray-500">+12.3%</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Trading Mode Warning */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-start space-x-3">
        <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5" />
        <div>
          <h4 className="font-medium text-yellow-900">Paper Trading Mode</h4>
          <p className="text-sm text-yellow-700 mt-1">
            You're currently in paper trading mode. No real money is at risk.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
