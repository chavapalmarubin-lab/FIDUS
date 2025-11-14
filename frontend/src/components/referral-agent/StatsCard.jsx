import React from 'react';
import { Card, CardContent } from '../ui/card';

const StatsCard = ({ title, value, subtitle, icon: Icon, trend, trendValue, loading }) => {
  if (loading) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
            <div className="h-8 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-1/3"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-500">{title}</p>
            <p className="text-3xl font-bold text-gray-900 mt-1">{value}</p>
            {subtitle && (
              <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
            )}
            {trend && trendValue && (
              <div className="flex items-center mt-2">
                <span
                  className={`text-sm font-medium ${
                    trend === 'up' ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {trend === 'up' ? '↑' : '↓'} {trendValue}
                </span>
              </div>
            )}
          </div>
          {Icon && (
            <div className="flex-shrink-0">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                <Icon className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default StatsCard;
