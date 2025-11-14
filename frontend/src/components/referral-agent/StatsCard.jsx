import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { TrendingUp, TrendingDown } from 'lucide-react';

const StatsCard = ({ title, value, icon: Icon, loading, trend }) => {
  const isPositive = trend && trend.startsWith('+');
  const isNegative = trend && trend.startsWith('-');

  return (
    <Card className="bg-gradient-to-br from-slate-900 to-slate-800 border-slate-700 hover:border-cyan-600/50 transition-all duration-300">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-slate-400">
          {title}
        </CardTitle>
        {Icon && (
          <div className="h-10 w-10 rounded-full bg-cyan-600/20 flex items-center justify-center">
            <Icon className="h-5 w-5 text-cyan-400" />
          </div>
        )}
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="space-y-2">
            <div className="h-8 w-24 bg-slate-700 animate-pulse rounded"></div>
            {trend && <div className="h-4 w-16 bg-slate-700 animate-pulse rounded"></div>}
          </div>
        ) : (
          <>
            <div className="text-3xl font-bold text-white">{value}</div>
            {trend && (
              <div className="flex items-center gap-1 mt-2">
                {isPositive && <TrendingUp className="h-4 w-4 text-green-400" />}
                {isNegative && <TrendingDown className="h-4 w-4 text-red-400" />}
                <span
                  className={`text-sm font-medium ${
                    isPositive ? 'text-green-400' : isNegative ? 'text-red-400' : 'text-slate-400'
                  }`}
                >
                  {trend}
                </span>
                <span className="text-xs text-slate-500 ml-1">vs last period</span>
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default StatsCard;