import React from 'react';
import { LOADING } from '../constants/uiConstants';

/**
 * Consistent Loading Spinner Component
 * Phase 7: UI/UX Consistency
 */
const LoadingSpinner = ({ 
  size = 'md', 
  message = '', 
  fullPage = false,
  className = '' 
}) => {
  const sizeClasses = {
    sm: LOADING.spinner.sm,
    md: LOADING.spinner.md,
    lg: LOADING.spinner.lg,
    xl: LOADING.spinner.xl
  };

  const spinner = (
    <div className={`text-center ${className}`}>
      <div className={`${LOADING.spinnerClass} ${sizeClasses[size]} mx-auto`}></div>
      {message && (
        <p className="mt-3 text-sm text-gray-600 font-medium">{message}</p>
      )}
    </div>
  );

  if (fullPage) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        {spinner}
      </div>
    );
  }

  return spinner;
};

export default LoadingSpinner;
