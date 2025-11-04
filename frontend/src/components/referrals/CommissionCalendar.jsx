import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import referralService from '../../services/referralService';

const CommissionCalendar = ({ compact = false, salespersonId = null }) => {
  const [calendar, setCalendar] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentMonth, setCurrentMonth] = useState(new Date());

  useEffect(() => {
    loadCalendar();
  }, [currentMonth, salespersonId]);

  const loadCalendar = async () => {
    try {
      setLoading(true);
      
      const startDate = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), 1);
      const endDate = compact 
        ? new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 3, 0)
        : new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 0);
      
      const data = await referralService.getCommissionCalendar(
        startDate.toISOString().split('T')[0],
        endDate.toISOString().split('T')[0],
        salespersonId
      );
      
      setCalendar(data.calendar || []);
    } catch (error) {
      console.error('Failed to load commission calendar:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value || 0);
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const previousMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1));
  };

  const nextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1));
  };

  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
      </div>
    );
  }

  const months = calendar.sort((a, b) => a.month.localeCompare(b.month));

  if (compact) {
    const allPayments = months.flatMap(month => 
      month.payments.map(payment => ({
        ...payment,
        month: month.month_display
      }))
    ).slice(0, 5);

    return (
      <div className="space-y-2">
        {allPayments.length === 0 ? (
          <p className="text-center text-gray-500 py-4">No upcoming commissions</p>
        ) : (
          allPayments.map((payment, idx) => (
            <div
              key={idx}
              className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50"
            >
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
                <div>
                  <p className="font-medium text-gray-900">{formatDate(payment.date)}</p>
                  <p className="text-sm text-gray-600">{payment.salesperson_name} - {payment.product.replace('FIDUS_', '')}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="font-semibold text-gray-900">{formatCurrency(payment.amount)}</p>
                <Badge variant={payment.status === 'paid' ? 'success' : 'warning'} className="text-xs">
                  {payment.status}
                </Badge>
              </div>
            </div>
          ))
        )}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <Button variant="outline" size="sm" onClick={previousMonth}>
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </Button>
        <h3 className="text-lg font-semibold">
          {currentMonth.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
        </h3>
        <Button variant="outline" size="sm" onClick={nextMonth}>
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </Button>
      </div>

      {months.length === 0 ? (
        <p className="text-center text-gray-500 py-8">No commissions for this period</p>
      ) : (
        months.map((month) => (
          <Card key={month.month} className="border-2">
            <CardHeader className="bg-gray-50">
              <CardTitle className="flex items-center justify-between">
                <span>{month.month_display}</span>
                <Badge className="bg-blue-600">
                  {formatCurrency(month.total_commissions)}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-4">
              <div className="space-y-2">
                {month.payments.map((payment, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50"
                  >
                    <div>
                      <p className="font-medium text-gray-900">{formatDate(payment.date)}</p>
                      <div className="flex items-center gap-4 text-sm text-gray-600 mt-1">
                        <span className="flex items-center gap-1">
                          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                          </svg>
                          {payment.salesperson_name}
                        </span>
                        <span>{payment.client_name}</span>
                        <span>{payment.product.replace('FIDUS_', '')}</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-gray-900">{formatCurrency(payment.amount)}</p>
                      <Badge 
                        variant={
                          payment.status === 'paid' ? 'success' :
                          payment.status === 'approved' ? 'info' :
                          payment.status === 'ready_to_pay' ? 'warning' :
                          'default'
                        }
                        className="text-xs mt-1"
                      >
                        {payment.status.replace('_', ' ')}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        ))
      )}
    </div>
  );
};

export default CommissionCalendar;