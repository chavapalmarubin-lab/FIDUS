/**
 * Badge Component - FIDUS Platform
 * Consistent badge styling for status indicators, tags, and labels
 */

import React from 'react';
import { BADGE_STYLES, getStatusColor, getFundBadgeStyle, getRiskBadgeStyle, cn } from '../../constants/styles';

export const Badge = ({ 
  children,
  variant = 'neutral',
  type = 'default', // 'default', 'status', 'fund', 'risk'
  className = '',
  ...props 
}) => {
  let badgeClasses = BADGE_STYLES.base;

  // Determine badge style based on type
  if (type === 'status') {
    badgeClasses = cn(badgeClasses, getStatusColor(variant));
  } else if (type === 'fund') {
    badgeClasses = cn(badgeClasses, getFundBadgeStyle(variant));
  } else if (type === 'risk') {
    badgeClasses = cn(badgeClasses, getRiskBadgeStyle(variant));
  } else {
    // Default type
    badgeClasses = cn(badgeClasses, BADGE_STYLES[variant] || BADGE_STYLES.neutral);
  }

  return (
    <span className={cn(badgeClasses, className)} {...props}>
      {children}
    </span>
  );
};

export default Badge;
