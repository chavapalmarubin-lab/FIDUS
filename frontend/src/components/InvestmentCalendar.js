import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { 
  Calendar as CalendarIcon, 
  ChevronLeft, 
  ChevronRight,
  DollarSign,
  TrendingUp,
  ArrowDownCircle,
  Clock,
  Info,
  CheckCircle,
  AlertCircle
} from "lucide-react";
import axios from "axios";
import apiAxios from "../utils/apiAxios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const InvestmentCalendar = ({ user }) => {
  const [calendarData, setCalendarData] = useState(null);
  const [monthlyTimeline, setMonthlyTimeline] = useState({});
  const [contractSummary, setContractSummary] = useState(null);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [viewMode, setViewMode] = useState('timeline'); // timeline, upcoming, month
  const [currentDate, setCurrentDate] = useState(new Date()); // For month navigation

  useEffect(() => {
    fetchCalendarData();
  }, [user.id]);

  const fetchCalendarData = async () => {
    try {
      setLoading(true);
      const response = await apiAxios.get(`/client/${user.id}/calendar`);
      
      if (response.data.success && response.data.calendar) {
        const { calendar_events, monthly_timeline, contract_summary } = response.data.calendar;
        setCalendarData(calendar_events || []);
        setMonthlyTimeline(monthly_timeline || {});
        setContractSummary(contract_summary);
      } else {
        setError(response.data.error || "Failed to load calendar data");
      }
    } catch (err) {
      setError("Failed to load investment calendar");
      console.error('Calendar fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRedemptionRequest = async (event) => {
    try {
      // This would integrate with the existing redemption system
      // For now, just show that it's pending
      console.log('Redemption request for:', event);
      
      // You could call the redemption API here
      // await apiAxios.post('/redemptions/request', {
      //   investment_id: event.investment_id,
      //   requested_amount: event.amount,
      //   reason: 'Client calendar redemption request'
      // });
      
      alert('Redemption request functionality would be integrated with existing system');
    } catch (err) {
      console.error('Redemption request error:', err);
      alert('Failed to submit redemption request');
    }
  };

  const generateInterestPayments = (events, investment, startDate, endDate) => {
    const interestRate = getFundInterestRate(investment.fund_code) / 100;
    const monthlyInterest = investment.principal_amount * interestRate;
    
    let currentDate = new Date(startDate);
    const maxDate = new Date(endDate);
    maxDate.setFullYear(maxDate.getFullYear() + 2); // Show 2 years ahead
    
    let monthCount = 1;
    
    while (currentDate <= maxDate) {
      // Add one month
      currentDate.setMonth(currentDate.getMonth() + 1);
      
      events.push({
        id: `interest-${investment.investment_id}-${monthCount}`,
        date: new Date(currentDate),
        type: 'interest_payment',
        title: `Interest Payment`,
        description: `${investment.fund_code} Fund - Month ${monthCount}`,
        fund: investment.fund_code,
        amount: monthlyInterest,
        investment_id: investment.investment_id,
        monthNumber: monthCount
      });
      
      monthCount++;
    }
  };

  const generateInterestRedemptions = (events, investment, startDate, endDate) => {
    const frequency = getFundRedemptionFrequency(investment.fund_code);
    const monthsInterval = getRedemptionInterval(frequency);
    
    let currentDate = new Date(startDate);
    const maxDate = new Date(endDate);
    maxDate.setFullYear(maxDate.getFullYear() + 2); // Show 2 years ahead
    
    let redemptionCount = 1;
    
    // Start from the first redemption opportunity
    currentDate.setMonth(currentDate.getMonth() + monthsInterval);
    
    while (currentDate <= maxDate) {
      const interestRate = getFundInterestRate(investment.fund_code) / 100;
      const accumulatedInterest = investment.principal_amount * interestRate * monthsInterval;
      
      events.push({
        id: `redemption-${investment.investment_id}-${redemptionCount}`,
        date: new Date(currentDate),
        type: 'interest_redemption',
        title: `Interest Redemption Available`,
        description: `${investment.fund_code} Fund - ${frequency} redemption`,
        fund: investment.fund_code,
        amount: accumulatedInterest,
        investment_id: investment.investment_id,
        frequency: frequency
      });
      
      currentDate.setMonth(currentDate.getMonth() + monthsInterval);
      redemptionCount++;
    }
  };

  const getFundInterestRate = (fundCode) => {
    const rates = { CORE: 1.5, BALANCE: 2.5, DYNAMIC: 3.5, UNLIMITED: 0 };
    return rates[fundCode] || 0;
  };

  const getFundRedemptionFrequency = (fundCode) => {
    const frequencies = { 
      CORE: 'monthly', 
      BALANCE: 'quarterly', 
      DYNAMIC: 'semi_annually', 
      UNLIMITED: 'flexible' 
    };
    return frequencies[fundCode] || 'monthly';
  };

  const getRedemptionInterval = (frequency) => {
    const intervals = { 
      monthly: 1, 
      quarterly: 3, 
      semi_annually: 6, 
      annually: 12, 
      flexible: 1 
    };
    return intervals[frequency] || 1;
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const getEventTypeIcon = (type) => {
    switch (type) {
      case 'investment_start':
        return DollarSign;
      case 'incubation_end':
        return Clock;
      case 'interest_redemption':
        return TrendingUp;
      case 'final_redemption':
        return ArrowDownCircle;
      default:
        return CalendarIcon;
    }
  };

  const getEventTypeColor = (type) => {
    switch (type) {
      case 'investment_start':
        return 'bg-blue-600';
      case 'incubation_end':
        return 'bg-yellow-600';
      case 'interest_redemption':
        return 'bg-green-600';
      case 'final_redemption':
        return 'bg-red-600';
      default:
        return 'bg-gray-600';
    }
  };

  const getFundColor = (fundCode) => {
    switch (fundCode) {
      case 'CORE':
        return 'text-orange-400';
      case 'BALANCE':
        return 'text-cyan-400';
      case 'DYNAMIC':
        return 'text-green-400';
      default:
        return 'text-gray-400';
    }
  };

  const getEventTypeConfig = (eventType) => {
    const configs = {
      investment_start: { 
        color: 'bg-blue-500', 
        icon: DollarSign, 
        textColor: 'text-blue-600',
        bgColor: 'bg-blue-100' 
      },
      interest_start: { 
        color: 'bg-green-500', 
        icon: TrendingUp, 
        textColor: 'text-green-600',
        bgColor: 'bg-green-100' 
      },
      interest_payment: { 
        color: 'bg-green-400', 
        icon: TrendingUp, 
        textColor: 'text-green-600',
        bgColor: 'bg-green-50' 
      },
      interest_redemption: { 
        color: 'bg-orange-500', 
        icon: ArrowDownCircle, 
        textColor: 'text-orange-600',
        bgColor: 'bg-orange-100' 
      },
      principal_redemption: { 
        color: 'bg-red-500', 
        icon: ArrowDownCircle, 
        textColor: 'text-red-600',
        bgColor: 'bg-red-100' 
      }
    };
    return configs[eventType] || configs.interest_payment;
  };

  const getDaysInMonth = (date) => {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
  };

  const getFirstDayOfMonth = (date) => {
    return new Date(date.getFullYear(), date.getMonth(), 1).getDay();
  };

  const getEventsForDate = (date) => {
    if (!calendarData || !Array.isArray(calendarData)) return [];
    return calendarData.filter(event => {
      const eventDate = new Date(event.date);
      return eventDate.toDateString() === date.toDateString();
    });
  };

  const getUpcomingEvents = () => {
    if (!calendarData || !Array.isArray(calendarData)) return [];
    const today = new Date();
    const ninetyDaysFromNow = new Date();
    ninetyDaysFromNow.setDate(today.getDate() + 90);
    
    return calendarData
      .filter(event => {
        const eventDate = new Date(event.date);
        return eventDate >= today && eventDate <= ninetyDaysFromNow;
      })
      .sort((a, b) => new Date(a.date) - new Date(b.date));
  };

  const getNextInterestPayment = () => {
    if (!calendarData || !Array.isArray(calendarData)) return null;
    const today = new Date();
    return calendarData
      .filter(event => event.type === 'interest_payment' && new Date(event.date) >= today)
      .sort((a, b) => new Date(a.date) - new Date(b.date))[0];
  };

  const getNextRedemption = () => {
    if (!calendarData || !Array.isArray(calendarData)) return null;
    const today = new Date();
    return calendarData
      .filter(event => event.type === 'interest_redemption' && new Date(event.date) >= today)
      .sort((a, b) => new Date(a.date) - new Date(b.date))[0];
  };

  const navigateMonth = (direction) => {
    const newDate = new Date(currentDate);
    newDate.setMonth(newDate.getMonth() + direction);
    setCurrentDate(newDate);
  };

  const renderCalendarGrid = () => {
    const daysInMonth = getDaysInMonth(currentDate);
    const firstDay = getFirstDayOfMonth(currentDate);
    const days = [];
    const today = new Date();

    // Empty cells for days before the first day of the month
    for (let i = 0; i < firstDay; i++) {
      days.push(<div key={`empty-${i}`} className="h-24 border border-slate-700"></div>);
    }

    // Days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
      const events = getEventsForDate(date);
      const isToday = date.toDateString() === today.toDateString();
      const isPast = date < today;

      days.push(
        <div
          key={day}
          className={`h-24 border border-slate-700 p-1 ${
            isToday ? 'bg-cyan-900/30 border-cyan-500' : ''
          } ${isPast ? 'opacity-75' : ''}`}
        >
          <div className={`text-sm font-medium ${
            isToday ? 'text-cyan-400' : 'text-white'
          }`}>
            {day}
          </div>
          <div className="space-y-1 mt-1">
            {events.slice(0, 2).map(event => {
              const config = getEventTypeConfig(event.type);
              const Icon = config.icon;
              return (
                <motion.div
                  key={event.id}
                  whileHover={{ scale: 1.02 }}
                  className={`${config.color} text-white text-xs p-1 rounded cursor-pointer flex items-center`}
                  onClick={() => setSelectedEvent(event)}
                >
                  <Icon className="w-3 h-3 mr-1" />
                  <span className="truncate">{event.title}</span>
                </motion.div>
              );
            })}
            {events.length > 2 && (
              <div className="text-xs text-slate-400">
                +{events.length - 2} more
              </div>
            )}
          </div>
        </div>
      );
    }

    return days;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-white text-xl">Loading calendar...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white flex items-center">
          <CalendarIcon className="mr-3 h-8 w-8 text-cyan-400" />
          Investment Calendar - Full Contract Timeline
        </h2>
        <div className="flex space-x-2">
          <Button
            variant={viewMode === 'timeline' ? 'default' : 'outline'}
            onClick={() => setViewMode('timeline')}
            className="text-white"
          >
            14 Months View
          </Button>
          <Button
            variant={viewMode === 'upcoming' ? 'default' : 'outline'}
            onClick={() => setViewMode('upcoming')}
            className="text-white"
          >
            Upcoming Events
          </Button>
          <Button
            variant={viewMode === 'month' ? 'default' : 'outline'}
            onClick={() => setViewMode('month')}
            className="text-white"
          >
            Monthly View
          </Button>
        </div>
      </div>

      {/* Contract Summary */}
      {contractSummary && (
        <Card className="dashboard-card">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <Info className="mr-2 h-5 w-5 text-cyan-400" />
              Contract Overview
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-slate-400">Contract Period:</span>
                <div className="text-white font-medium">
                  {contractSummary.contract_start ? 
                    `${formatDate(contractSummary.contract_start)} - ${formatDate(contractSummary.contract_end)}` :
                    'No active investments'
                  }
                </div>
                <div className="text-slate-400 text-xs">
                  {contractSummary.contract_duration_days} days
                </div>
              </div>
              <div>
                <span className="text-slate-400">Total Investment:</span>
                <div className="text-cyan-400 font-medium">
                  {formatCurrency(contractSummary.total_investment)}
                </div>
              </div>
              <div>
                <span className="text-slate-400">Total Interest:</span>
                <div className="text-green-400 font-medium">
                  {formatCurrency(contractSummary.total_interest)}
                </div>
              </div>
              <div>
                <span className="text-slate-400">Final Value:</span>
                <div className="text-white font-bold">
                  {formatCurrency(contractSummary.total_value)}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error Message */}
      {error && (
        <div className="bg-red-900/20 border border-red-600 rounded-lg p-3">
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {/* Full Timeline View - 14 Months */}
      {viewMode === 'timeline' && (
        <Card className="dashboard-card">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <CalendarIcon className="mr-2 h-5 w-5 text-cyan-400" />
              Full Contract Timeline (14 Months)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {Object.keys(monthlyTimeline).length === 0 ? (
                <div className="text-center py-8 text-slate-400">
                  <CalendarIcon className="mx-auto h-12 w-12 mb-4 opacity-50" />
                  <p>No investment timeline data available</p>
                </div>
              ) : (
                Object.entries(monthlyTimeline)
                  .sort(([a], [b]) => new Date(a) - new Date(b))
                  .map(([monthKey, monthData]) => (
                    <motion.div
                      key={monthKey}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className={`border rounded-lg p-6 ${monthData.is_past ? 'bg-slate-800/30 border-slate-700' : 'bg-slate-800/50 border-slate-600'}`}
                    >
                      {/* Month Header */}
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-xl font-bold text-white">
                          📅 {monthData.month_name}
                        </h3>
                        {monthData.total_due > 0 && (
                          <div className="text-right">
                            <div className="text-lg font-bold text-cyan-400">
                              Total Due: {formatCurrency(monthData.total_due)}
                            </div>
                            {!monthData.is_past && (
                              <div className="text-sm text-slate-400">
                                {monthData.days_until} days away
                              </div>
                            )}
                          </div>
                        )}
                      </div>

                      {/* Month Events */}
                      <div className="space-y-3">
                        {monthData.events.map(event => {
                          const Icon = getEventTypeIcon(event.type);
                          const eventColor = getEventTypeColor(event.type);
                          const fundColor = getFundColor(event.fund_code);
                          
                          return (
                            <motion.div
                              key={event.id}
                              whileHover={{ scale: 1.01 }}
                              className="flex items-center p-4 bg-slate-700/50 rounded-lg cursor-pointer"
                              onClick={() => setSelectedEvent(event)}
                            >
                              <div className={`${eventColor} p-2 rounded mr-3`}>
                                <Icon className="w-4 h-4 text-white" />
                              </div>
                              
                              <div className="flex-1">
                                <div className="flex items-center mb-1">
                                  <span className="text-white font-medium mr-2">
                                    {formatDate(event.date)}
                                  </span>
                                  <Badge className={`${fundColor} bg-transparent border`}>
                                    {event.fund_code}
                                  </Badge>
                                </div>
                                
                                <h4 className="text-white font-semibold">{event.title}</h4>
                                <p className="text-slate-400 text-sm">{event.description}</p>
                                
                                {event.amount && (
                                  <div className="flex items-center mt-2 space-x-4">
                                    <span className={`font-bold ${event.type === 'final_redemption' ? 'text-red-400' : 'text-green-400'}`}>
                                      {formatCurrency(event.amount)}
                                    </span>
                                    
                                    {event.can_redeem && (
                                      <div className="ml-auto">
                                        {event.is_available ? (
                                          <Button
                                            size="sm"
                                            onClick={(e) => {
                                              e.stopPropagation();
                                              handleRedemptionRequest(event);
                                            }}
                                            className="bg-green-600 hover:bg-green-700 text-white"
                                          >
                                            <ArrowDownCircle className="w-4 h-4 mr-1" />
                                            Request Redemption
                                          </Button>
                                        ) : (
                                          <Badge variant="outline" className="text-yellow-400 border-yellow-400">
                                            <Clock className="w-3 h-3 mr-1" />
                                            Available in {event.days_until} days
                                          </Badge>
                                        )}
                                      </div>
                                    )}
                                  </div>
                                )}
                              </div>
                            </motion.div>
                          );
                        })}
                      </div>

                      {/* Monthly Summary */}
                      {monthData.total_due > 0 && (
                        <div className="mt-4 p-3 bg-slate-900/50 rounded border border-slate-600">
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                            {monthData.core_interest > 0 && (
                              <div>
                                <span className="text-slate-400">CORE Interest:</span>
                                <div className="text-orange-400 font-medium">
                                  {formatCurrency(monthData.core_interest)}
                                </div>
                              </div>
                            )}
                            {monthData.balance_interest > 0 && (
                              <div>
                                <span className="text-slate-400">BALANCE Interest:</span>
                                <div className="text-cyan-400 font-medium">
                                  {formatCurrency(monthData.balance_interest)}
                                </div>
                              </div>
                            )}
                            {monthData.dynamic_interest > 0 && (
                              <div>
                                <span className="text-slate-400">DYNAMIC Interest:</span>
                                <div className="text-green-400 font-medium">
                                  {formatCurrency(monthData.dynamic_interest)}
                                </div>
                              </div>
                            )}
                            {monthData.principal_amount > 0 && (
                              <div>
                                <span className="text-slate-400">Principal:</span>
                                <div className="text-red-400 font-medium">
                                  {formatCurrency(monthData.principal_amount)}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </motion.div>
                  ))
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Upcoming Events View */}
      {viewMode === 'upcoming' && (
        <Card className="dashboard-card">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <Clock className="mr-2 h-5 w-5 text-cyan-400" />
              Upcoming Events (Next 90 Days)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {calendarData && calendarData.length > 0 ? (
                calendarData
                  .filter(event => {
                    const eventDate = new Date(event.date);
                    const today = new Date();
                    const diffDays = Math.ceil((eventDate - today) / (1000 * 60 * 60 * 24));
                    return diffDays >= 0 && diffDays <= 90;
                  })
                  .slice(0, 10)
                  .map(event => {
                    const Icon = getEventTypeIcon(event.type);
                    const eventColor = getEventTypeColor(event.type);
                    const daysUntil = Math.ceil((new Date(event.date) - new Date()) / (1000 * 60 * 60 * 24));
                    
                    return (
                      <motion.div
                        key={event.id}
                        whileHover={{ scale: 1.02 }}
                        className="flex items-center p-4 bg-slate-800/50 rounded-lg border border-slate-700 cursor-pointer"
                        onClick={() => setSelectedEvent(event)}
                      >
                        <div className={`${eventColor} p-3 rounded-lg mr-4`}>
                          <Icon className="w-5 h-5 text-white" />
                        </div>
                        <div className="flex-1">
                          <h3 className="text-white font-semibold">{event.title}</h3>
                          <p className="text-slate-400 text-sm">{event.description}</p>
                          <div className="flex items-center mt-2 space-x-4">
                            <span className="text-cyan-400 text-sm font-medium">
                              {formatDate(event.date)}
                            </span>
                            {daysUntil >= 0 && (
                              <Badge variant="outline" className="text-slate-300">
                                {daysUntil === 0 ? 'Today' : 
                                 daysUntil === 1 ? 'Tomorrow' :
                                 `${daysUntil} days`}
                              </Badge>
                            )}
                            {event.amount && (
                              <span className="text-green-400 font-semibold">
                                {formatCurrency(event.amount)}
                              </span>
                            )}
                          </div>
                        </div>
                      </motion.div>
                    );
                  })
              ) : (
                <div className="text-center py-8">
                  <p className="text-slate-400">No upcoming events in the next 90 days</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Calendar Navigation */}
      {viewMode === 'month' && (
      <Card className="dashboard-card">
        <CardHeader>
          <div className="flex items-center justify-between">
            <Button
              variant="ghost"
              onClick={() => navigateMonth(-1)}
              className="text-white hover:bg-slate-700"
            >
              <ChevronLeft className="w-4 h-4" />
            </Button>
            <CardTitle className="text-white text-xl">
              {currentDate.toLocaleDateString('en-US', { 
                month: 'long', 
                year: 'numeric' 
              })}
            </CardTitle>
            <Button
              variant="ghost"
              onClick={() => navigateMonth(1)}
              className="text-white hover:bg-slate-700"
            >
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {/* Calendar Grid */}
          <div className="grid grid-cols-7 gap-0">
            {/* Day headers */}
            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
              <div key={day} className="h-8 border border-slate-700 bg-slate-800 flex items-center justify-center">
                <span className="text-slate-300 text-sm font-medium">{day}</span>
              </div>
            ))}
            {/* Calendar days */}
            {renderCalendarGrid()}
          </div>
        </CardContent>
      </Card>
      )}

      {/* Investment Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="dashboard-card">
          <CardContent className="p-6">
            <div className="flex items-center">
              <DollarSign className="h-8 w-8 text-green-400 mr-3" />
              <div>
                <p className="text-slate-400 text-sm">Next Interest Payment</p>
                <p className="text-2xl font-bold text-white">
                  {getNextInterestPayment() ? formatDate(getNextInterestPayment().date) : 'N/A'}
                </p>
                {getNextInterestPayment() && (
                  <p className="text-green-400 text-sm">
                    {formatCurrency(getNextInterestPayment().amount)}
                  </p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="dashboard-card">
          <CardContent className="p-6">
            <div className="flex items-center">
              <ArrowDownCircle className="h-8 w-8 text-orange-400 mr-3" />
              <div>
                <p className="text-slate-400 text-sm">Next Redemption</p>
                <p className="text-2xl font-bold text-white">
                  {getNextRedemption() ? formatDate(getNextRedemption().date) : 'N/A'}
                </p>
                {getNextRedemption() && (
                  <p className="text-orange-400 text-sm">
                    {getNextRedemption().frequency || 'Available'}
                  </p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="dashboard-card">
          <CardContent className="p-6">
            <div className="flex items-center">
              <TrendingUp className="h-8 w-8 text-cyan-400 mr-3" />
              <div>
                <p className="text-slate-400 text-sm">Total Events</p>
                <p className="text-2xl font-bold text-white">
                  {getUpcomingEvents().length}
                </p>
                <p className="text-cyan-400 text-sm">Next 90 days</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Legend */}
      <Card className="dashboard-card">
        <CardHeader>
          <CardTitle className="text-white flex items-center">
            <Info className="mr-2 h-5 w-5 text-cyan-400" />
            Event Legend
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {Object.entries({
              investment_start: 'Investment Start',
              interest_start: 'Interest Begins',
              interest_payment: 'Interest Payment',
              interest_redemption: 'Interest Redemption',
              principal_redemption: 'Principal Redemption'
            }).map(([type, label]) => {
              const config = getEventTypeConfig(type);
              const Icon = config.icon;
              return (
                <div key={type} className="flex items-center">
                  <div className={`${config.color} p-2 rounded mr-2`}>
                    <Icon className="w-4 h-4 text-white" />
                  </div>
                  <span className="text-slate-300 text-sm">{label}</span>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Event Detail Modal */}
      <AnimatePresence>
        {selectedEvent && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
            onClick={() => setSelectedEvent(null)}
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              className="bg-slate-800 rounded-lg p-6 max-w-md w-full mx-4"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center mb-4">
                {React.createElement(getEventTypeConfig(selectedEvent.type).icon, {
                  className: "w-6 h-6 mr-2 text-cyan-400"
                })}
                <h3 className="text-xl font-semibold text-white">
                  {selectedEvent.title}
                </h3>
              </div>
              
              <div className="space-y-3">
                <div>
                  <span className="text-slate-400">Date:</span>
                  <span className="text-white ml-2 font-medium">
                    {formatDate(selectedEvent.date)}
                  </span>
                </div>
                
                <div>
                  <span className="text-slate-400">Fund:</span>
                  <Badge className="ml-2 bg-blue-600">
                    {selectedEvent.fund}
                  </Badge>
                </div>
                
                {selectedEvent.amount && (
                  <div>
                    <span className="text-slate-400">Amount:</span>
                    <span className="text-green-400 ml-2 font-medium">
                      {formatCurrency(selectedEvent.amount)}
                    </span>
                  </div>
                )}
                
                <div>
                  <span className="text-slate-400">Description:</span>
                  <p className="text-white mt-1">{selectedEvent.description}</p>
                </div>
              </div>
              
              <Button
                onClick={() => setSelectedEvent(null)}
                className="w-full mt-4 bg-slate-700 hover:bg-slate-600"
              >
                Close
              </Button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default InvestmentCalendar;