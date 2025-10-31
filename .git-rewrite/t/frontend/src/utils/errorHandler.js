/**
 * Global Error Handling System
 * Centralized error handling with user-friendly messages and logging
 */

class ErrorHandler {
  constructor() {
    this.errorLog = [];
    this.maxLogSize = 100;
    this.setupGlobalErrorHandlers();
  }

  /**
   * Setup global error handlers for unhandled errors
   */
  setupGlobalErrorHandlers() {
    // Handle unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      this.handleError(event.reason, 'Unhandled Promise Rejection');
      event.preventDefault();
    });

    // Handle JavaScript errors
    window.addEventListener('error', (event) => {
      this.handleError(
        new Error(`${event.message} at ${event.filename}:${event.lineno}:${event.colno}`),
        'JavaScript Error'
      );
    });
  }

  /**
   * Handle and categorize errors
   */
  handleError(error, context = 'Unknown') {
    const errorInfo = this.categorizeError(error);
    
    // Log error details
    this.logError({
      ...errorInfo,
      context,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href
    });

    // Show user-friendly message
    this.showUserMessage(errorInfo);

    // Report to monitoring service (if configured)
    this.reportError(errorInfo);
  }

  /**
   * Categorize errors and provide user-friendly messages
   */
  categorizeError(error) {
    const errorInfo = {
      originalError: error,
      type: 'unknown',
      severity: 'medium',
      userMessage: 'An unexpected error occurred. Please try again.',
      technicalMessage: error?.message || 'Unknown error',
      recovery: 'refresh'
    };

    // Network errors
    if (error?.code === 'NETWORK_ERROR' || error?.message?.includes('Network Error')) {
      errorInfo.type = 'network';
      errorInfo.severity = 'high';
      errorInfo.userMessage = 'Connection problem. Please check your internet connection and try again.';
      errorInfo.recovery = 'retry';
    }

    // Authentication errors
    else if (error?.response?.status === 401) {
      errorInfo.type = 'authentication';
      errorInfo.severity = 'high';
      errorInfo.userMessage = 'Your session has expired. Please log in again.';
      errorInfo.recovery = 'login';
    }

    // Authorization errors
    else if (error?.response?.status === 403) {
      errorInfo.type = 'authorization';
      errorInfo.severity = 'medium';
      errorInfo.userMessage = 'You don\'t have permission to perform this action.';
      errorInfo.recovery = 'none';
    }

    // Rate limiting
    else if (error?.response?.status === 429) {
      errorInfo.type = 'rate_limit';
      errorInfo.severity = 'medium';
      errorInfo.userMessage = 'Too many requests. Please wait a moment and try again.';
      errorInfo.recovery = 'wait';
    }

    // Server errors
    else if (error?.response?.status >= 500) {
      errorInfo.type = 'server';
      errorInfo.severity = 'high';
      errorInfo.userMessage = 'Server is temporarily unavailable. Our team has been notified.';
      errorInfo.recovery = 'retry';
    }

    // Validation errors
    else if (error?.response?.status === 400 || error?.response?.status === 422) {
      errorInfo.type = 'validation';
      errorInfo.severity = 'low';
      errorInfo.userMessage = error?.response?.data?.message || 'Please check your input and try again.';
      errorInfo.recovery = 'fix';
    }

    // JavaScript errors
    else if (error instanceof Error) {
      errorInfo.type = 'javascript';
      errorInfo.severity = 'high';
      errorInfo.userMessage = 'Something went wrong. Please refresh the page.';
      errorInfo.recovery = 'refresh';
    }

    return errorInfo;
  }

  /**
   * Show user-friendly error message
   */
  showUserMessage(errorInfo) {
    // Create or update error notification
    this.showNotification(errorInfo);
  }

  /**
   * Show error notification to user
   */
  showNotification(errorInfo) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `error-notification ${errorInfo.severity}`;
    notification.innerHTML = `
      <div class="error-content">
        <div class="error-message">${errorInfo.userMessage}</div>
        <div class="error-actions">
          ${this.getRecoveryButtons(errorInfo.recovery)}
          <button class="dismiss-btn" onclick="this.parentElement.parentElement.parentElement.remove()">×</button>
        </div>
      </div>
    `;

    // Add styles
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      max-width: 400px;
      background: #fee;
      border: 1px solid #fcc;
      border-radius: 8px;
      padding: 16px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      z-index: 10000;
      font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    `;

    // Auto-remove after 10 seconds
    setTimeout(() => {
      if (notification.parentNode) {
        notification.remove();
      }
    }, 10000);

    document.body.appendChild(notification);
  }

  /**
   * Get recovery action buttons
   */
  getRecoveryButtons(recovery) {
    switch (recovery) {
      case 'retry':
        return '<button class="retry-btn" onclick="window.location.reload()">Retry</button>';
      case 'refresh':
        return '<button class="refresh-btn" onclick="window.location.reload()">Refresh Page</button>';
      case 'login':
        return '<button class="login-btn" onclick="localStorage.removeItem(\'fidus_user\'); window.location.href=\'/\'">Login Again</button>';
      case 'wait':
        return '<button class="wait-btn" disabled>Please wait...</button>';
      default:
        return '';
    }
  }

  /**
   * Log error for debugging
   */
  logError(errorDetails) {
    console.error('Error handled:', errorDetails);
    
    // Add to error log
    this.errorLog.push(errorDetails);
    
    // Keep log size manageable
    if (this.errorLog.length > this.maxLogSize) {
      this.errorLog = this.errorLog.slice(-this.maxLogSize);
    }
  }

  /**
   * Report error to monitoring service
   */
  reportError(errorInfo) {
    // In production, this would send to monitoring service like Sentry
    if (process.env.NODE_ENV === 'production') {
      // Send to monitoring service
      console.log('Would report to monitoring:', errorInfo);
    }
  }

  /**
   * Get error statistics for debugging
   */
  getErrorStats() {
    const stats = {
      total: this.errorLog.length,
      byType: {},
      bySeverity: {},
      recent: this.errorLog.slice(-10)
    };

    this.errorLog.forEach(error => {
      stats.byType[error.type] = (stats.byType[error.type] || 0) + 1;
      stats.bySeverity[error.severity] = (stats.bySeverity[error.severity] || 0) + 1;
    });

    return stats;
  }

  /**
   * Clear error log
   */
  clearLog() {
    this.errorLog = [];
  }
}

// Global error handler instance
export const errorHandler = new ErrorHandler();

// Convenience functions
export const handleError = (error, context) => errorHandler.handleError(error, context);
export const getErrorStats = () => errorHandler.getErrorStats();
export const clearErrorLog = () => errorHandler.clearLog();

export default errorHandler;