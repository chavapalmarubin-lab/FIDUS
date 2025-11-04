import React, { useState, useEffect } from 'react';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Badge } from '../ui/badge';
import referralService from '../../services/referralService';

const ReferralCodeInput = ({ value, onChange, autoFocus = false, className = '' }) => {
  const [code, setCode] = useState(value || '');
  const [validating, setValidating] = useState(false);
  const [isValid, setIsValid] = useState(null);
  const [salesperson, setSalesperson] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    // Auto-validate if value provided (from URL)
    if (value) {
      validateCode(value);
    }
  }, [value]);

  const validateCode = async (referralCode) => {
    if (!referralCode || referralCode.length < 3) {
      setIsValid(null);
      setSalesperson(null);
      setError('');
      return;
    }

    setValidating(true);
    setError('');

    try {
      // Call public API to validate code
      const data = await referralService.getSalespersonByCode(referralCode);
      
      if (data && data.active) {
        setIsValid(true);
        setSalesperson(data);
        onChange(referralCode, data); // Pass back to parent
      } else {
        setIsValid(false);
        setSalesperson(null);
        setError('Referral code is not active');
        onChange('', null);
      }
    } catch (err) {
      setIsValid(false);
      setSalesperson(null);
      setError('Invalid referral code');
      onChange('', null);
    } finally {
      setValidating(false);
    }
  };

  const handleChange = (e) => {
    const newCode = e.target.value.trim().toUpperCase();
    setCode(newCode);
    
    // Debounce validation
    if (newCode) {
      const timer = setTimeout(() => validateCode(newCode), 500);
      return () => clearTimeout(timer);
    } else {
      setIsValid(null);
      setSalesperson(null);
      onChange('', null);
    }
  };

  return (
    <div className={`space-y-2 ${className}`}>
      <Label htmlFor="referral-code">
        Referral Code <span className="text-gray-400 text-sm">(Optional)</span>
      </Label>
      
      <div className="relative">
        <Input
          id="referral-code"
          type="text"
          placeholder="Enter referral code (e.g., SP-2025)"
          value={code}
          onChange={handleChange}
          autoFocus={autoFocus}
          className={`pr-10 ${
            isValid === true ? 'border-green-500' :
            isValid === false ? 'border-red-500' :
            ''
          }`}
        />
        
        {/* Status Icon */}
        <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
          {validating && (
            <svg className="animate-spin h-4 w-4 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          )}
          {!validating && isValid === true && (
            <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          )}
          {!validating && isValid === false && (
            <svg className="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          )}
        </div>
      </div>

      {/* Salesperson Info */}
      {isValid && salesperson && (
        <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-lg">
          <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-green-900">
              Referred by {salesperson.name}
            </p>
            <p className="text-xs text-green-700">{salesperson.email}</p>
          </div>
          <Badge className="bg-green-600 text-white">Verified</Badge>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <p className="text-sm text-red-600 flex items-center gap-1">
          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
          {error}
        </p>
      )}

      {/* Help Text */}
      {!code && !isValid && (
        <p className="text-xs text-gray-500">
          If you were referred by an advisor, enter their referral code here
        </p>
      )}
    </div>
  );
};

export default ReferralCodeInput;
