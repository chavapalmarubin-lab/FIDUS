/**
 * FIDUS Frontend Configuration
 * PRODUCTION FIX: Hardcode backend URL since supervisor doesn't pass environment variables
 */

// Production backend URL (hardcoded fix for supervisor environment variable issue)
export const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://fidus-invest.emergent.host';
export const API_BASE_URL = `${BACKEND_URL}/api`;

// Export for backward compatibility
export default {
  BACKEND_URL,
  API_BASE_URL
};