import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { TrendingUp, Info } from "lucide-react";

const InvestmentCalculator = ({ 
  fundName, 
  fundInfo, 
  currentMonthlyEarnings, 
  userBalance 
}) => {
  const [investmentAmount, setInvestmentAmount] = useState(fundInfo.minInvestment);
  
  // Calculate potential earnings
  const monthlyEarnings = (investmentAmount * fundInfo.interestRate) / 100;
  const annualEarnings = monthlyEarnings * 12;
  const fiveYearEarnings = monthlyEarnings * 60;
  
  // Calculate new total earnings
  const newTotalMonthly = currentMonthlyEarnings + monthlyEarnings;
  const increase = monthlyEarnings;
  const percentageIncrease = currentMonthlyEarnings > 0 
    ? ((increase / currentMonthlyEarnings) * 100).toFixed(1) 
    : 0;
  
  // Max investment = min(user balance, fund max suggested)
  const maxInvestment = Math.min(userBalance, fundInfo.maxSuggested || 100000);
  
  return (
    <Card className="investment-calculator">
      <CardHeader>
        <CardTitle className="calculator-header">
          <div className="flex items-center gap-4">
            <span className="fund-icon text-4xl">{fundInfo.icon}</span>
            <div>
              <h3 className="text-xl font-bold text-white">{fundName} - Investment Calculator</h3>
              <p className="text-sm text-slate-400 font-normal mt-1">
                See your potential earnings with this fund
              </p>
            </div>
          </div>
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Investment Amount Slider */}
        <div className="investment-slider">
          <label className="block mb-4 text-slate-300 font-medium">
            If you invest:
          </label>
          <input 
            type="range" 
            min={fundInfo.minInvestment}
            max={maxInvestment}
            step={1000}
            value={investmentAmount}
            onChange={(e) => setInvestmentAmount(Number(e.target.value))}
            className="slider w-full h-3 rounded-lg appearance-none cursor-pointer"
            style={{
              background: `linear-gradient(to right, #3b82f6 0%, #3b82f6 ${((investmentAmount - fundInfo.minInvestment) / (maxInvestment - fundInfo.minInvestment)) * 100}%, #334155 ${((investmentAmount - fundInfo.minInvestment) / (maxInvestment - fundInfo.minInvestment)) * 100}%, #334155 100%)`
            }}
          />
          <div className="amount-display text-center my-6">
            <div className="text-5xl font-extrabold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              ${investmentAmount.toLocaleString()}
            </div>
          </div>
          <div className="range-labels flex justify-between text-sm text-slate-500 font-medium">
            <span>${fundInfo.minInvestment.toLocaleString()}</span>
            <span>${maxInvestment.toLocaleString()}</span>
          </div>
        </div>
        
        {/* Earnings Breakdown */}
        <div className="earnings-breakdown bg-gradient-to-br from-blue-900/30 to-green-900/30 border border-blue-500/30 rounded-xl p-6">
          <h4 className="text-lg font-semibold text-white mb-5 flex items-center">
            <span className="mr-2">💰</span>
            You would earn:
          </h4>
          <div className="earnings-grid grid grid-cols-3 gap-6">
            <div className="earning-item text-center">
              <span className="label block text-xs text-slate-400 uppercase tracking-wider mb-2">
                Monthly
              </span>
              <span className="value block text-3xl font-bold text-green-400">
                ${monthlyEarnings.toLocaleString(undefined, {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2
                })}
              </span>
            </div>
            <div className="earning-item text-center">
              <span className="label block text-xs text-slate-400 uppercase tracking-wider mb-2">
                Annually
              </span>
              <span className="value block text-2xl font-bold text-blue-400">
                ${annualEarnings.toLocaleString(undefined, {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2
                })}
              </span>
            </div>
            <div className="earning-item text-center">
              <span className="label block text-xs text-slate-400 uppercase tracking-wider mb-2">
                5 Years
              </span>
              <span className="value block text-2xl font-bold text-cyan-400">
                ${fiveYearEarnings.toLocaleString(undefined, {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2
                })}
              </span>
            </div>
          </div>
        </div>
        
        {/* New Total Earnings Comparison */}
        <div className="total-comparison bg-gradient-to-br from-green-900/30 to-blue-900/30 border-2 border-green-500/40 rounded-xl p-6">
          <h4 className="text-lg font-semibold text-white mb-5 flex items-center">
            <span className="mr-2">📊</span>
            Your NEW total monthly earnings:
          </h4>
          <div className="comparison-bar flex items-center gap-6 flex-wrap">
            <div className="current">
              <span className="label block text-xs text-slate-400 uppercase tracking-wider mb-1">
                Current
              </span>
              <span className="amount block text-2xl font-bold text-slate-200">
                ${currentMonthlyEarnings.toLocaleString(undefined, {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2
                })}
              </span>
            </div>
            <span className="arrow text-4xl text-blue-400 font-bold">→</span>
            <div className="new">
              <span className="label block text-xs text-slate-400 uppercase tracking-wider mb-1">
                New
              </span>
              <span className="amount block text-2xl font-bold text-slate-200">
                ${newTotalMonthly.toLocaleString(undefined, {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2
                })}
              </span>
            </div>
            <div className="increase ml-auto">
              <span className="badge inline-block px-5 py-3 bg-gradient-to-r from-green-500/20 to-emerald-500/20 border border-green-500/50 rounded-full text-green-400 font-bold text-base whitespace-nowrap">
                +${increase.toLocaleString(undefined, {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2
                })} (+{percentageIncrease}%) 
                <TrendingUp className="inline ml-1" size={18} />
              </span>
            </div>
          </div>
        </div>
        
        {/* Fund Details Summary */}
        <div className="fund-details-compact grid grid-cols-4 gap-3">
          <div className="detail flex items-center gap-2 text-sm p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg hover:bg-blue-500/20 transition-all">
            <span className="icon text-lg">💰</span>
            <span className="text-slate-200">{fundInfo.interestRate}% Monthly</span>
          </div>
          <div className="detail flex items-center gap-2 text-sm p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg hover:bg-blue-500/20 transition-all">
            <span className="icon text-lg">📈</span>
            <span className="text-slate-200">~{fundInfo.annualReturn}% Annual</span>
          </div>
          <div className="detail flex items-center gap-2 text-sm p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg hover:bg-blue-500/20 transition-all">
            <span className="icon text-lg">⚠️</span>
            <span className="text-slate-200">{fundInfo.riskLevel} Risk</span>
          </div>
          <div className="detail flex items-center gap-2 text-sm p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg hover:bg-blue-500/20 transition-all">
            <span className="icon text-lg">🔒</span>
            <span className="text-slate-200">{fundInfo.lockPeriod} Lock</span>
          </div>
        </div>
        
        {/* Description */}
        <p className="fund-description text-sm text-slate-400 leading-relaxed border-l-4 border-blue-500 pl-4 py-2">
          {fundInfo.description}
        </p>
        
        {/* Action Buttons */}
        <div className="calculator-actions flex gap-4">
          <Button 
            variant="outline"
            className="flex-1 border-blue-500 text-blue-400 hover:bg-blue-500/10"
          >
            Learn More About {fundName}
          </Button>
          <Button 
            className="flex-1 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-semibold"
          >
            Start Investing ⭐
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default InvestmentCalculator;
