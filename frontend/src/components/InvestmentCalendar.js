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
  Info
} from "lucide-react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const InvestmentCalendar = ({ user }) => {
  const [investments, setInvestments] = useState([]);
  const [calendarEvents, setCalendarEvents] = useState([]);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [viewMode, setViewMode] = useState('month'); // month, upcoming

  useEffect(() => {
    fetchInvestmentData();
  }, [user.id]);

  const fetchInvestmentData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/investments/client/${user.id}`);
      
      if (response.data.success) {
        const investmentData = response.data.investments;
        setInvestments(investmentData);
        generateCalendarEvents(investmentData);
      }
    } catch (err) {
      setError("Failed to load investment data");
    } finally {
      setLoading(false);
    }
  };

  const generateCalendarEvents = (investments) => {
    const events = [];
    const today = new Date();
    
    investments.forEach(investment => {
      const depositDate = new Date(investment.deposit_date);
      const interestStartDate = new Date(investment.interest_start_date);
      const principalRedemptionDate = new Date(investment.minimum_hold_end_date);
      
      // Add investment start event
      events.push({
        id: `start-${investment.investment_id}`,
        date: depositDate,
        type: 'investment_start',
        title: `Investment Started`,
        description: `${investment.fund_code} Fund - ${formatCurrency(investment.principal_amount)}`,
        fund: investment.fund_code,
        amount: investment.principal_amount,
        investment_id: investment.investment_id
      });

      // Add interest start event
      if (interestStartDate > depositDate) {
        events.push({
          id: `interest-start-${investment.investment_id}`,
          date: interestStartDate,
          type: 'interest_start',
          title: `Interest Payments Begin`,
          description: `${investment.fund_code} Fund - ${getFundInterestRate(investment.fund_code)}% monthly`,
          fund: investment.fund_code,
          investment_id: investment.investment_id
        });
      }

      // Generate monthly interest payment events
      generateInterestPayments(events, investment, interestStartDate, today);
      
      // Generate interest redemption opportunities
      generateInterestRedemptions(events, investment, interestStartDate, today);
      
      // Add principal redemption date
      events.push({
        id: `principal-${investment.investment_id}`,
        date: principalRedemptionDate,
        type: 'principal_redemption',
        title: `Principal Redemption Available`,
        description: `${investment.fund_code} Fund - Principal ${formatCurrency(investment.principal_amount)}`,
        fund: investment.fund_code,
        amount: investment.principal_amount,
        investment_id: investment.investment_id
      });
    });

    // Sort events by date
    events.sort((a, b) => new Date(a.date) - new Date(b.date));
    setCalendarEvents(events);
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
    return calendarEvents.filter(event => {
      const eventDate = new Date(event.date);
      return eventDate.toDateString() === date.toDateString();
    });
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
          Investment Calendar
        </h2>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-900/20 border border-red-600 rounded-lg p-3">
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {/* Calendar Navigation */}
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