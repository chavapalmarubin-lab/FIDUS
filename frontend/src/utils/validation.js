/**
 * Advanced Form Validation System for FIDUS Investment Platform
 * Implements real-time validation, security checks, and user-friendly feedback
 */

/**
 * Validation Rules Library
 */
export const ValidationRules = {
  // Basic field validation
  required: (value, message = 'This field is required') => {
    if (!value || (typeof value === 'string' && value.trim() === '')) {
      return message;
    }
    return null;
  },

  // Email validation with business rules
  email: (value, message = 'Please enter a valid email address') => {
    if (!value) return null; // Allow empty if not required
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
      return message;
    }

    // Additional business rules for financial platform
    const commonDomains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com'];
    const domain = value.split('@')[1]?.toLowerCase();
    
    // Warn about personal email domains for business accounts
    if (commonDomains.includes(domain)) {
      return {
        type: 'warning',
        message: 'Consider using a business email address for professional accounts'
      };
    }

    return null;
  },

  // Password validation for financial platform security
  password: (value, message = 'Password does not meet security requirements') => {
    if (!value) return null;

    const requirements = {
      minLength: value.length >= 8,
      hasUppercase: /[A-Z]/.test(value),
      hasLowercase: /[a-z]/.test(value),
      hasNumbers: /\d/.test(value),
      hasSpecialChar: /[!@#$%^&*(),.?":{}|<>]/.test(value),
      noCommonPatterns: !/(123456|password|qwerty|admin)/i.test(value),
    };

    const failedRequirements = Object.entries(requirements)
      .filter(([_, passed]) => !passed)
      .map(([requirement]) => requirement);

    if (failedRequirements.length > 0) {
      return {
        type: 'error',
        message,
        details: {
          requirements: {
            'Minimum 8 characters': requirements.minLength,
            'Uppercase letter': requirements.hasUppercase,
            'Lowercase letter': requirements.hasLowercase,
            'Number': requirements.hasNumbers,
            'Special character': requirements.hasSpecialChar,
            'No common patterns': requirements.noCommonPatterns,
          }
        }
      };
    }

    return null;
  },

  // Financial amount validation
  amount: (value, options = {}) => {
    const { min = 0, max = Infinity, currency = 'USD' } = options;
    
    if (!value) return null;

    const numValue = parseFloat(value);
    
    if (isNaN(numValue)) {
      return 'Please enter a valid amount';
    }

    if (numValue < min) {
      return `Minimum amount is ${new Intl.NumberFormat('en-US', { 
        style: 'currency', 
        currency 
      }).format(min)}`;
    }

    if (numValue > max) {
      return `Maximum amount is ${new Intl.NumberFormat('en-US', { 
        style: 'currency', 
        currency 
      }).format(max)}`;
    }

    return null;
  },

  // Phone number validation
  phone: (value, message = 'Please enter a valid phone number') => {
    if (!value) return null;

    // Remove all non-digit characters
    const digits = value.replace(/\D/g, '');
    
    // Check for valid length (10-15 digits)
    if (digits.length < 10 || digits.length > 15) {
      return message;
    }

    return null;
  },

  // Date validation
  date: (value, options = {}) => {
    const { min, max, format = 'YYYY-MM-DD' } = options;
    
    if (!value) return null;

    const date = new Date(value);
    
    if (isNaN(date.getTime())) {
      return 'Please enter a valid date';
    }

    if (min && date < new Date(min)) {
      return `Date must be after ${new Date(min).toLocaleDateString()}`;
    }

    if (max && date > new Date(max)) {
      return `Date must be before ${new Date(max).toLocaleDateString()}`;
    }

    return null;
  },

  // Custom business rule validators
  investmentAmount: (value) => {
    const numValue = parseFloat(value);
    
    if (isNaN(numValue)) {
      return 'Please enter a valid investment amount';
    }

    // Business rules for investment amounts
    if (numValue < 1000) {
      return 'Minimum investment amount is $1,000';
    }

    if (numValue > 10000000) {
      return 'Please contact support for investments over $10M';
    }

    // Check for unusual patterns
    if (numValue % 1 !== 0 && numValue.toString().split('.')[1]?.length > 2) {
      return 'Investment amounts should not have more than 2 decimal places';
    }

    return null;
  },

  // Client ID validation
  clientId: (value) => {
    if (!value) return null;

    // Format: client_XXX or CLIENTXXX
    const clientIdRegex = /^(client_|CLIENT)\w+$/i;
    
    if (!clientIdRegex.test(value)) {
      return 'Client ID must start with "client_" or "CLIENT"';
    }

    return null;
  },
};

/**
 * Form Validator Class
 */
export class FormValidator {
  constructor(schema = {}) {
    this.schema = schema;
    this.errors = {};
    this.warnings = {};
    this.isValid = true;
  }

  /**
   * Validate single field
   */
  validateField(fieldName, value, rules = []) {
    const fieldRules = rules.length ? rules : this.schema[fieldName] || [];
    let error = null;
    let warning = null;

    for (const rule of fieldRules) {
      let result;

      if (typeof rule === 'function') {
        result = rule(value);
      } else if (typeof rule === 'object' && rule.validator) {
        result = rule.validator(value, rule.options);
      } else if (typeof rule === 'string' && ValidationRules[rule]) {
        result = ValidationRules[rule](value);
      }

      if (result) {
        if (typeof result === 'string') {
          error = result;
          break; // Stop on first error
        } else if (result.type === 'error') {
          error = result;
          break;
        } else if (result.type === 'warning' && !warning) {
          warning = result;
        }
      }
    }

    // Update errors and warnings
    if (error) {
      this.errors[fieldName] = error;
      this.isValid = false;
    } else {
      delete this.errors[fieldName];
    }

    if (warning) {
      this.warnings[fieldName] = warning;
    } else {
      delete this.warnings[fieldName];
    }

    return { error, warning, isValid: !error };
  }

  /**
   * Validate entire form
   */
  validateForm(formData) {
    this.errors = {};
    this.warnings = {};
    this.isValid = true;

    Object.keys(this.schema).forEach(fieldName => {
      this.validateField(fieldName, formData[fieldName]);
    });

    // Check for overall form validity
    this.isValid = Object.keys(this.errors).length === 0;

    return {
      isValid: this.isValid,
      errors: this.errors,
      warnings: this.warnings,
    };
  }

  /**
   * Get field error
   */
  getFieldError(fieldName) {
    return this.errors[fieldName] || null;
  }

  /**
   * Get field warning
   */
  getFieldWarning(fieldName) {
    return this.warnings[fieldName] || null;
  }

  /**
   * Check if field has error
   */
  hasFieldError(fieldName) {
    return !!this.errors[fieldName];
  }

  /**
   * Get all errors
   */
  getAllErrors() {
    return this.errors;
  }

  /**
   * Clear all errors
   */
  clearErrors() {
    this.errors = {};
    this.warnings = {};
    this.isValid = true;
  }
}

/**
 * Predefined validation schemas for common forms
 */
export const ValidationSchemas = {
  // Login form validation
  login: {
    username: [ValidationRules.required],
    password: [ValidationRules.required],
  },

  // User registration validation
  registration: {
    username: [ValidationRules.required],
    email: [ValidationRules.required, ValidationRules.email],
    password: [ValidationRules.required, ValidationRules.password],
    confirmPassword: [ValidationRules.required],
  },

  // Investment creation validation
  investment: {
    clientId: [ValidationRules.required, ValidationRules.clientId],
    amount: [ValidationRules.required, ValidationRules.investmentAmount],
    fundCode: [ValidationRules.required],
    depositDate: [ValidationRules.required, ValidationRules.date],
  },

  // Client profile validation
  clientProfile: {
    name: [ValidationRules.required],
    email: [ValidationRules.required, ValidationRules.email],
    phone: [ValidationRules.phone],
    dateOfBirth: [ValidationRules.date],
  },

  // Document upload validation
  documentUpload: {
    category: [ValidationRules.required],
    file: [ValidationRules.required],
  },

  // Password reset validation
  passwordReset: {
    email: [ValidationRules.required, ValidationRules.email],
  },

  // Contact form validation
  contact: {
    name: [ValidationRules.required],
    email: [ValidationRules.required, ValidationRules.email],
    subject: [ValidationRules.required],
    message: [ValidationRules.required],
  },
};

/**
 * Real-time validation hook for React components
 */
export const useValidation = (schema, initialData = {}) => {
  const [formData, setFormData] = React.useState(initialData);
  const [validator] = React.useState(() => new FormValidator(schema));
  const [errors, setErrors] = React.useState({});
  const [warnings, setWarnings] = React.useState({});

  const validateField = React.useCallback((fieldName, value) => {
    const result = validator.validateField(fieldName, value);
    
    setErrors(prev => ({
      ...prev,
      [fieldName]: result.error
    }));

    setWarnings(prev => ({
      ...prev,
      [fieldName]: result.warning
    }));

    return result;
  }, [validator]);

  const validateForm = React.useCallback(() => {
    const result = validator.validateForm(formData);
    setErrors(result.errors);
    setWarnings(result.warnings);
    return result;
  }, [validator, formData]);

  const updateField = React.useCallback((fieldName, value) => {
    setFormData(prev => ({
      ...prev,
      [fieldName]: value
    }));

    // Validate field in real-time with debounce
    setTimeout(() => {
      validateField(fieldName, value);
    }, 300);
  }, [validateField]);

  const clearErrors = React.useCallback(() => {
    validator.clearErrors();
    setErrors({});
    setWarnings({});
  }, [validator]);

  return {
    formData,
    errors,
    warnings,
    updateField,
    validateField,
    validateForm,
    clearErrors,
    isValid: Object.keys(errors).length === 0,
  };
};

/**
 * Utility functions
 */
export const sanitizeInput = (input) => {
  if (typeof input !== 'string') return input;
  
  // Remove potentially dangerous characters
  return input
    .trim()
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
    .replace(/[<>]/g, '');
};

export const formatCurrency = (amount, currency = 'USD') => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amount);
};

export const formatPhone = (phone) => {
  const digits = phone.replace(/\D/g, '');
  
  if (digits.length === 10) {
    return `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6)}`;
  }
  
  return phone;
};

export default FormValidator;