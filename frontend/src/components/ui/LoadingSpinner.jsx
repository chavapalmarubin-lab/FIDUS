/**
 * Loading Spinner Component - FIDUS Platform
 * Consistent loading states across the entire application
 */

import React from 'react';
import { LOADING_STYLES, cn } from '../../constants/styles';

export const LoadingSpinner = ({ 
  size = 'md',
  text = 'Loading...',
  showText = true,
  className = ''
}) => {
  return (
    <div className={cn(LOADING_STYLES.container, className)}>
      <div className={cn(LOADING_STYLES.spinner, LOADING_STYLES.sizes[size])} />
      {showText && text && (
        <p className={LOADING_STYLES.text}>{text}</p>
      )}
    </div>
  );
};

export default LoadingSpinner;
