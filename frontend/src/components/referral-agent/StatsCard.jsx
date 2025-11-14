import React from 'react';
import { Card, CardContent } from '../ui/card';

const StatsCard = ({ title, value, subtitle, icon: Icon, trend, trendValue, loading }) => {
  if (loading) {
    return (
      <Card className="bg-slate-900 border-slate-800">
        <CardContent className="pt-6">
          <div className="animate-pulse">
            <div className="h-4 bg-slate-700 rounded w-1/2 mb-2"></div>
            <div className="h-8 bg-slate-700 rounded w-3/4 mb-2"></div>
            <div className="h-3 bg-slate-700 rounded w-1/3"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-slate-900 border-slate-800 hover:border-cyan-600 transition-colors cursor-pointer">
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium text-slate-400">{title}</p>
            <p className="text-3xl font-bold text-white mt-1">{value}</p>
            {subtitle && (
              <p className="text-sm text-slate-400 mt-1">{subtitle}</p>
            )}
            {trend && trendValue && (
              <div className="flex items-center mt-2">
                <span
                  className={`text-sm font-medium ${
                    trend === 'up' ? 'text-green-400' : 'text-red-400'
                  }`}
                >
                  {trend === 'up' ? '↑' : '↓'} {trendValue}
                </span>
              </div>
            )}
          </div>
          {Icon && (
            <div className="flex-shrink-0">
              <div className="w-12 h-12 bg-cyan-600/20 rounded-full flex items-center justify-center">
                <Icon className="h-6 w-6 text-cyan-400" />
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default StatsCard;
