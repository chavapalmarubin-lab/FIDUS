import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { TrendingUp, Info, DollarSign } from "lucide-react";

const EnhancedFundCard = ({
  fundName,
  fundInfo,
  balance,
  isActive,
  monthlyEarnings,
  formatCurrency,
  selectedCurrency
}) => {
  
  return (
    <Card className="fund-card group hover:border-blue-500/50 transition-all duration-300 hover:shadow-xl hover:shadow-blue-500/20 hover:-translate-y-1">
      <CardHeader className="pb-3">
        {/* Header with status */}
        <div className="fund-header flex justify-between items-start">
          <div className="fund-title flex items-center gap-3">
            <span className="fund-icon text-3xl">{fundInfo.icon}</span>
            <div>
              <h3 className="text-lg font-bold text-white">{fundName}</h3>
              <p className="text-xs text-slate-400 mt-0.5">{fundInfo.riskLevel} Risk</p>
            </div>
          </div>
          <Badge 
            className={`status-badge ${isActive ? 'bg-green-500/20 text-green-400 border-green-500/50' : 'bg-slate-500/20 text-slate-400 border-slate-500/50'}`}
          >
            {isActive ? '🟢 ACTIVE' : '⚪ NO INVESTMENT'}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Current balance */}
        <div className="fund-balance text-center py-4 bg-slate-800/50 rounded-lg">
          <div className="balance-amount text-4xl font-extrabold text-blue-400">
            {formatCurrency(balance)}
          </div>
          {selectedCurrency !== 'USD' && balance > 0 && (
            <div className="text-slate-400 text-xs mt-1">
              {new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD',
                minimumFractionDigits: 2
              }).format(balance)} USD
            </div>
          )}
          <div className="balance-label text-xs text-slate-400 uppercase tracking-wider mt-2">
            Current Balance
          </div>
        </div>

        {/* Fund Performance Details */}
        <div className="fund-details space-y-2 py-4 border-t border-b border-slate-700">
          <div className="detail-row flex items-center gap-2 text-sm">
            <span className="icon text-lg">💰</span>
            <span className="label text-slate-400 flex-grow">Returns:</span>
            <span className="value font-semibold text-slate-200">
              {fundInfo.interestRate}% Monthly
            </span>
          </div>
          
          <div className="detail-row flex items-center gap-2 text-sm">
            <span className="icon text-lg">📈</span>
            <span className="label text-slate-400 flex-grow">Expected Annual:</span>
            <span className="value font-semibold text-slate-200">
              ~{fundInfo.annualReturn}%
            </span>
          </div>

          <div className="detail-row flex items-center gap-2 text-sm">
            <span className="icon text-lg">⚠️</span>
            <span className="label text-slate-400 flex-grow">Risk Level:</span>
            <span className="value font-semibold text-slate-200">
              {fundInfo.riskLevel}
            </span>
          </div>

          {isActive && monthlyEarnings > 0 && (
            <div className="detail-row highlight bg-green-500/10 border border-green-500/30 rounded-lg p-3 mt-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="icon text-xl">📊</span>
                  <span className="label text-green-300 font-medium">Your Monthly Earnings:</span>
                </div>
                <span className="value earnings text-2xl font-bold text-green-400">
                  ${monthlyEarnings.toLocaleString(undefined, {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                  })}
                </span>
              </div>
            </div>
          )}

          {!isActive && (
            <div className="detail-row highlight bg-blue-500/10 border border-blue-500/30 rounded-lg p-3 mt-3 text-center">
              <span className="icon text-2xl block mb-2">🚀</span>
              <span className="label text-blue-300 font-medium block">
                {fundInfo.highlight}
              </span>
            </div>
          )}
        </div>

        {/* Description */}
        <div className="fund-description">
          <p className="text-xs text-slate-400 leading-relaxed">
            {fundInfo.description}
          </p>
        </div>

        {/* Additional info */}
        <div className="fund-meta grid grid-cols-2 gap-3 p-3 bg-blue-500/5 rounded-lg">
          <div className="meta-item">
            <span className="label block text-xs text-slate-500 uppercase mb-1">
              Min Investment
            </span>
            <span className="value block text-sm font-semibold text-slate-200">
              ${fundInfo.minInvestment.toLocaleString()}
            </span>
          </div>
          <div className="meta-item">
            <span className="label block text-xs text-slate-500 uppercase mb-1">
              Lock Period
            </span>
            <span className="value block text-sm font-semibold text-slate-200">
              {fundInfo.lockPeriod}
            </span>
          </div>
        </div>

        {/* Action buttons */}
        <div className="fund-actions flex gap-3 mt-4">
          {isActive ? (
            <>
              <Button 
                variant="outline"
                className="flex-1 border-slate-600 text-slate-300 hover:bg-slate-800"
                size="sm"
              >
                View Details
              </Button>
              <Button 
                className="flex-1 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-semibold"
                size="sm"
              >
                <DollarSign className="mr-1" size={14} />
                Add Funds
              </Button>
            </>
          ) : (
            <>
              <Button 
                variant="outline"
                className="flex-1 border-slate-600 text-slate-300 hover:bg-slate-800"
                size="sm"
              >
                <Info className="mr-1" size={14} />
                Learn More
              </Button>
              <Button 
                className="flex-1 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-semibold"
                size="sm"
              >
                Start Investing ⭐
              </Button>
            </>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default EnhancedFundCard;
