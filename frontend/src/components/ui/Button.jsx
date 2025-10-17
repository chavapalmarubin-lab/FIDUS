/**
 * Standard Button Component - FIDUS Platform
 * Consistent button styling across the entire application
 */

import React from 'react';
import { BUTTON_STYLES, cn } from '../../constants/styles';

export const Button = ({ 
  children,
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  className = '',
  onClick,
  type = 'button',
  ...props 
}) => {
  const buttonClasses = cn(
    BUTTON_STYLES.base,
    BUTTON_STYLES.sizes[size],
    BUTTON_STYLES.variants[variant],
    disabled && 'opacity-50 cursor-not-allowed',
    loading && 'opacity-75 cursor-wait',
    className
  );

  return (
    <button
      type={type}
      className={buttonClasses}
      onClick={onClick}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <div className="flex items-center gap-2">
          <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
          <span>{children}</span>
        </div>
      ) : (
        children
      )}
    </button>
  );
};

export default Button;
