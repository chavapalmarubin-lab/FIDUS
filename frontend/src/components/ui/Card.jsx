/**
 * Card Component - FIDUS Platform
 * Consistent card styling across the entire application
 */

import React from 'react';
import { CARD_STYLES, SPACING, TRANSITIONS, cn } from '../../constants/styles';

export const Card = ({ 
  children,
  variant = 'default',
  hover = true,
  className = '',
  ...props 
}) => {
  const cardClasses = cn(
    CARD_STYLES.base,
    CARD_STYLES[variant],
    hover && CARD_STYLES.hover,
    SPACING.cardPadding,
    TRANSITIONS.base,
    className
  );

  return (
    <div className={cardClasses} {...props}>
      {children}
    </div>
  );
};

export const CardHeader = ({ children, className = '', ...props }) => {
  return (
    <div className={cn('mb-4 border-b border-slate-700 pb-4', className)} {...props}>
      {children}
    </div>
  );
};

export const CardTitle = ({ children, className = '', ...props }) => {
  return (
    <h3 className={cn('text-xl font-semibold text-white', className)} {...props}>
      {children}
    </h3>
  );
};

export const CardContent = ({ children, className = '', ...props }) => {
  return (
    <div className={cn('', className)} {...props}>
      {children}
    </div>
  );
};

export const CardFooter = ({ children, className = '', ...props }) => {
  return (
    <div className={cn('mt-4 pt-4 border-t border-slate-700', className)} {...props}>
      {children}
    </div>
  );
};

export default Card;
