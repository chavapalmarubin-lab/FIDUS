/**
 * FIDUS Investment Platform - Shared Style Constants
 * 
 * This file defines all styling constants used across the application
 * to ensure UI/UX consistency. Import and use these constants in all components.
 * 
 * Created: Phase 7 - Final Polish
 */

// ============================================
// SPACING CONSTANTS
// ============================================
export const SPACING = {
  // Section spacing
  sectionMargin: 'mb-8',
  sectionPadding: 'p-6',
  
  // Card spacing
  cardPadding: 'p-6',
  cardMargin: 'mb-6',
  
  // Grid gaps
  gridGap: 'gap-6',
  gridGapSmall: 'gap-4',
  gridGapLarge: 'gap-8',
  
  // Header margins
  headerMargin: 'mb-6',
  subHeaderMargin: 'mb-4',
  
  // Element spacing
  elementMargin: 'mb-4',
  elementPadding: 'p-4',
};

// ============================================
// TYPOGRAPHY CONSTANTS
// ============================================
export const TYPOGRAPHY = {
  // Headings
  h1: 'text-3xl font-bold text-white',
  h2: 'text-2xl font-semibold text-white',
  h3: 'text-xl font-semibold text-white',
  h4: 'text-lg font-semibold text-white',
  
  // Body text
  body: 'text-base text-white',
  bodySecondary: 'text-base text-slate-400',
  bodySmall: 'text-sm text-slate-400',
  
  // Labels
  label: 'text-sm font-medium text-slate-300',
  labelSmall: 'text-xs font-medium text-slate-400 uppercase',
  
  // Special text
  value: 'text-lg font-bold text-white',
  valuePositive: 'text-lg font-bold text-green-500',
  valueNegative: 'text-lg font-bold text-red-500',
};

// ============================================
// COLOR CONSTANTS (FIDUS Brand)
// ============================================
export const COLORS = {
  // Primary brand colors
  primary: {
    cyan: '#00bcd4',
    cyanRgba: 'rgba(0, 188, 212, 0.2)',
    orange: '#ffa726',
    orangeRgba: 'rgba(255, 167, 38, 0.2)',
  },
  
  // Background colors
  background: {
    dark: 'rgba(10, 15, 28, 1)',
    card: 'rgba(26, 34, 56, 0.8)',
    cardDark: 'rgba(15, 23, 42, 0.9)',
    cardHover: 'rgba(26, 34, 56, 0.9)',
  },
  
  // Status colors
  status: {
    success: '#4caf50',
    successBg: 'rgba(76, 175, 80, 0.2)',
    successBorder: 'rgba(76, 175, 80, 0.3)',
    
    warning: '#ffa726',
    warningBg: 'rgba(255, 167, 38, 0.2)',
    warningBorder: 'rgba(255, 167, 38, 0.3)',
    
    danger: '#ef4444',
    dangerBg: 'rgba(239, 68, 68, 0.2)',
    dangerBorder: 'rgba(239, 68, 68, 0.3)',
    
    info: '#00bcd4',
    infoBg: 'rgba(0, 188, 212, 0.2)',
    infoBorder: 'rgba(0, 188, 212, 0.3)',
  },
  
  // Text colors
  text: {
    primary: '#ffffff',
    secondary: '#94a3b8',
    muted: '#64748b',
    disabled: '#475569',
  },
  
  // Border colors
  border: {
    primary: 'rgba(0, 188, 212, 0.2)',
    secondary: 'rgba(148, 163, 184, 0.2)',
    hover: 'rgba(0, 188, 212, 0.4)',
  },
};

// ============================================
// BUTTON STYLES
// ============================================
export const BUTTON_STYLES = {
  // Base button classes
  base: 'px-4 py-2 rounded-lg font-medium transition-all duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-offset-2',
  
  // Size variants
  sizes: {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  },
  
  // Color variants
  variants: {
    primary: 'bg-gradient-to-r from-cyan-600 to-cyan-700 hover:from-cyan-700 hover:to-cyan-800 text-white shadow-lg hover:shadow-cyan-500/50',
    secondary: 'bg-slate-700 hover:bg-slate-600 text-white',
    success: 'bg-green-600 hover:bg-green-700 text-white shadow-lg hover:shadow-green-500/50',
    danger: 'bg-red-600 hover:bg-red-700 text-white shadow-lg hover:shadow-red-500/50',
    warning: 'bg-orange-600 hover:bg-orange-700 text-white shadow-lg hover:shadow-orange-500/50',
    outline: 'border-2 border-cyan-500 text-cyan-500 hover:bg-cyan-500/10',
    ghost: 'text-slate-300 hover:bg-slate-800',
  },
};

// ============================================
// CARD STYLES
// ============================================
export const CARD_STYLES = {
  // Base card
  base: 'rounded-lg backdrop-blur-sm transition-all duration-200',
  
  // Variants
  default: 'bg-slate-800/80 border border-cyan-500/20 shadow-lg',
  hover: 'hover:shadow-xl hover:-translate-y-1 hover:border-cyan-500/40',
  active: 'bg-slate-800/90 border-cyan-500/40 shadow-xl',
  
  // Special cards
  gradient: 'bg-gradient-to-br from-slate-800/80 to-slate-900/80 border border-cyan-500/20',
  glassmorphism: 'bg-slate-800/40 backdrop-blur-md border border-cyan-500/20',
};

// ============================================
// BADGE STYLES
// ============================================
export const BADGE_STYLES = {
  // Base badge
  base: 'inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold',
  
  // Status variants
  success: 'bg-green-500/20 text-green-500 border border-green-500/30',
  warning: 'bg-orange-500/20 text-orange-500 border border-orange-500/30',
  danger: 'bg-red-500/20 text-red-500 border border-red-500/30',
  info: 'bg-cyan-500/20 text-cyan-500 border border-cyan-500/30',
  neutral: 'bg-slate-500/20 text-slate-400 border border-slate-500/30',
  
  // Fund badges
  balance: 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30',
  core: 'bg-orange-500/20 text-orange-400 border border-orange-500/30',
};

// ============================================
// LOADING STATES
// ============================================
export const LOADING_STYLES = {
  spinner: 'animate-spin rounded-full border-4 border-slate-700 border-t-cyan-500',
  sizes: {
    sm: 'h-6 w-6',
    md: 'h-10 w-10',
    lg: 'h-16 w-16',
  },
  container: 'flex flex-col items-center justify-center p-8',
  text: 'mt-4 text-slate-400',
};

// ============================================
// BORDER RADIUS
// ============================================
export const BORDER_RADIUS = {
  card: 'rounded-lg',
  button: 'rounded-lg',
  badge: 'rounded-full',
  input: 'rounded-md',
  modal: 'rounded-xl',
  small: 'rounded',
  large: 'rounded-2xl',
};

// ============================================
// SHADOWS
// ============================================
export const SHADOWS = {
  card: 'shadow-lg',
  cardHover: 'shadow-xl',
  button: 'shadow-md',
  modal: 'shadow-2xl',
  glow: 'shadow-cyan-500/50',
  glowOrange: 'shadow-orange-500/50',
};

// ============================================
// TRANSITIONS
// ============================================
export const TRANSITIONS = {
  base: 'transition-all duration-200 ease-in-out',
  slow: 'transition-all duration-300 ease-in-out',
  fast: 'transition-all duration-150 ease-in-out',
  colors: 'transition-colors duration-200',
  transform: 'transition-transform duration-200',
};

// ============================================
// ANIMATION CLASSES
// ============================================
export const ANIMATIONS = {
  fadeIn: 'animate-fade-in',
  slideUp: 'animate-slide-up',
  slideDown: 'animate-slide-down',
  pulse: 'animate-pulse',
  bounce: 'animate-bounce',
};

// ============================================
// RESPONSIVE BREAKPOINTS
// ============================================
export const BREAKPOINTS = {
  mobile: '375px',
  mobileLarge: '414px',
  tablet: '768px',
  desktop: '1024px',
  desktopLarge: '1440px',
  desktopXL: '1920px',
};

// ============================================
// GRID LAYOUTS
// ============================================
export const GRID_LAYOUTS = {
  // Responsive grid patterns
  auto: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4',
  two: 'grid grid-cols-1 md:grid-cols-2',
  three: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
  four: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4',
};

// ============================================
// HELPER FUNCTIONS
// ============================================

/**
 * Get status color classes based on status
 */
export const getStatusColor = (status) => {
  const statusColors = {
    online: BADGE_STYLES.success,
    offline: BADGE_STYLES.danger,
    degraded: BADGE_STYLES.warning,
    active: BADGE_STYLES.success,
    inactive: BADGE_STYLES.neutral,
    pending: BADGE_STYLES.warning,
    error: BADGE_STYLES.danger,
  };
  return statusColors[status?.toLowerCase()] || BADGE_STYLES.neutral;
};

/**
 * Get fund badge style based on fund name
 */
export const getFundBadgeStyle = (fundName) => {
  const fundStyles = {
    BALANCE: BADGE_STYLES.balance,
    balance: BADGE_STYLES.balance,
    CORE: BADGE_STYLES.core,
    core: BADGE_STYLES.core,
  };
  return fundStyles[fundName] || BADGE_STYLES.neutral;
};

/**
 * Get risk level badge style
 */
export const getRiskBadgeStyle = (riskLevel) => {
  const riskStyles = {
    low: BADGE_STYLES.success,
    Low: BADGE_STYLES.success,
    medium: BADGE_STYLES.warning,
    Medium: BADGE_STYLES.warning,
    high: BADGE_STYLES.danger,
    High: BADGE_STYLES.danger,
  };
  return riskStyles[riskLevel] || BADGE_STYLES.neutral;
};

/**
 * Format currency value
 */
export const formatCurrency = (value, options = {}) => {
  if (value === null || value === undefined) return 'N/A';
  
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: options.currency || 'USD',
    minimumFractionDigits: options.decimals !== undefined ? options.decimals : 2,
    maximumFractionDigits: options.decimals !== undefined ? options.decimals : 2,
  }).format(value);
};

/**
 * Format percentage value
 */
export const formatPercentage = (value, decimals = 2) => {
  if (value === null || value === undefined) return 'N/A';
  return `${value >= 0 ? '+' : ''}${value.toFixed(decimals)}%`;
};

/**
 * Combine class names
 */
export const cn = (...classes) => {
  return classes.filter(Boolean).join(' ');
};

// ============================================
// EXPORT DEFAULT THEME
// ============================================
export default {
  SPACING,
  TYPOGRAPHY,
  COLORS,
  BUTTON_STYLES,
  CARD_STYLES,
  BADGE_STYLES,
  LOADING_STYLES,
  BORDER_RADIUS,
  SHADOWS,
  TRANSITIONS,
  ANIMATIONS,
  BREAKPOINTS,
  GRID_LAYOUTS,
  // Helper functions
  getStatusColor,
  getFundBadgeStyle,
  getRiskBadgeStyle,
  formatCurrency,
  formatPercentage,
  cn,
};
