/**
 * UI Constants for Consistent Styling
 * Phase 7: Final Polish & Optimization
 * 
 * Centralized styling constants to ensure consistency across all components
 */

// COLORS
export const COLORS = {
  // Primary
  primary: {
    DEFAULT: '#3B82F6',  // blue-600
    hover: '#2563EB',     // blue-700
    light: '#DBEAFE',     // blue-100
    dark: '#1E40AF'       // blue-800
  },
  
  // Status Colors
  success: {
    DEFAULT: '#10B981',   // green-600
    hover: '#059669',     // green-700
    light: '#D1FAE5',     // green-100
    dark: '#047857'       // green-800
  },
  
  warning: {
    DEFAULT: '#F59E0B',   // yellow-600
    hover: '#D97706',     // yellow-700
    light: '#FEF3C7',     // yellow-100
    dark: '#B45309'       // yellow-800
  },
  
  danger: {
    DEFAULT: '#EF4444',   // red-600
    hover: '#DC2626',     // red-700
    light: '#FEE2E2',     // red-100
    dark: '#B91C1C'       // red-800
  },
  
  info: {
    DEFAULT: '#8B5CF6',   // purple-600
    hover: '#7C3AED',     // purple-700
    light: '#EDE9FE',     // purple-100
    dark: '#6D28D9'       // purple-800
  },
  
  // Neutrals
  gray: {
    50: '#F9FAFB',
    100: '#F3F4F6',
    200: '#E5E7EB',
    300: '#D1D5DB',
    400: '#9CA3AF',
    500: '#6B7280',
    600: '#4B5563',
    700: '#374151',
    800: '#1F2937',
    900: '#111827'
  }
};

// SPACING
export const SPACING = {
  // Padding
  padding: {
    xs: 'p-2',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
    xl: 'p-12'
  },
  
  // Margin
  margin: {
    xs: 'mb-2',
    sm: 'mb-4',
    md: 'mb-6',
    lg: 'mb-8',
    xl: 'mb-12'
  },
  
  // Gap (for grids/flex)
  gap: {
    sm: 'gap-4',
    md: 'gap-6',
    lg: 'gap-8'
  }
};

// TYPOGRAPHY
export const TYPOGRAPHY = {
  // Headers
  h1: 'text-3xl font-bold text-gray-900',
  h2: 'text-2xl font-bold text-gray-900',
  h3: 'text-lg font-semibold text-gray-900',
  h4: 'text-base font-semibold text-gray-900',
  
  // Body text
  body: 'text-base text-gray-700',
  bodySmall: 'text-sm text-gray-600',
  caption: 'text-xs text-gray-500',
  
  // Special
  code: 'font-mono text-sm',
  label: 'text-sm font-medium text-gray-700'
};

// BORDERS & SHADOWS
export const BORDERS = {
  radius: {
    sm: 'rounded',
    md: 'rounded-lg',
    lg: 'rounded-xl',
    full: 'rounded-full'
  },
  
  width: {
    DEFAULT: 'border',
    thick: 'border-2',
    none: 'border-0'
  },
  
  shadow: {
    sm: 'shadow-sm',
    md: 'shadow-md',
    lg: 'shadow-lg',
    xl: 'shadow-xl'
  }
};

// BUTTONS
export const BUTTONS = {
  // Primary button
  primary: 'px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed',
  
  // Secondary button
  secondary: 'px-4 py-2 bg-white border-2 border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed',
  
  // Success button
  success: 'px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed',
  
  // Danger button
  danger: 'px-4 py-2 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed',
  
  // Icon button
  icon: 'p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors',
  
  // Sizes
  sizes: {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg'
  }
};

// LOADING STATES
export const LOADING = {
  spinner: {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
    xl: 'h-16 w-16'
  },
  
  spinnerClass: 'animate-spin rounded-full border-b-2 border-blue-600'
};

// CARDS
export const CARDS = {
  base: 'bg-white border border-gray-200 rounded-lg shadow-sm',
  hover: 'hover:shadow-lg transition-shadow duration-200',
  padding: 'p-6',
  
  // Card variations
  elevated: 'bg-white rounded-lg shadow-lg border border-gray-200',
  flat: 'bg-white rounded-lg border-2 border-gray-200'
};

// TRANSITIONS
export const TRANSITIONS = {
  fast: 'transition-all duration-150 ease-in-out',
  normal: 'transition-all duration-200 ease-in-out',
  slow: 'transition-all duration-300 ease-in-out'
};

// STATUS BADGES
export const BADGES = {
  success: 'px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold',
  warning: 'px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs font-semibold',
  danger: 'px-3 py-1 bg-red-100 text-red-800 rounded-full text-xs font-semibold',
  info: 'px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-semibold',
  neutral: 'px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-xs font-semibold'
};

// GRID LAYOUTS
export const GRIDS = {
  // Responsive grids
  cards: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6',
  twoCol: 'grid grid-cols-1 md:grid-cols-2 gap-6',
  fourCol: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6',
  
  // Auto-fit grids
  autoFit: 'grid grid-cols-[repeat(auto-fit,minmax(300px,1fr))] gap-6'
};

// ANIMATION CLASSES
export const ANIMATIONS = {
  fadeIn: 'animate-fadeIn',
  slideIn: 'animate-slideIn',
  pulse: 'animate-pulse',
  spin: 'animate-spin',
  bounce: 'animate-bounce'
};

// RESPONSIVE BREAKPOINTS (for reference)
export const BREAKPOINTS = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px'
};

// Z-INDEX LAYERS
export const Z_INDEX = {
  base: 0,
  dropdown: 10,
  sticky: 20,
  modal: 50,
  popover: 60,
  toast: 70,
  tooltip: 80
};

export default {
  COLORS,
  SPACING,
  TYPOGRAPHY,
  BORDERS,
  BUTTONS,
  LOADING,
  CARDS,
  TRANSITIONS,
  BADGES,
  GRIDS,
  ANIMATIONS,
  BREAKPOINTS,
  Z_INDEX
};
