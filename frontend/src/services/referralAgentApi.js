import axios from 'axios';

const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const getAuthHeaders = () => {
  const token = localStorage.getItem('referral_agent_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

const toCamelCase = (str) => {
  return str.replace(/_([a-z])/g, (g) => g[1].toUpperCase());
};

const transformKeys = (obj) => {
  if (Array.isArray(obj)) {
    return obj.map(transformKeys);
  }
  if (obj !== null && typeof obj === 'object') {
    return Object.keys(obj).reduce((acc, key) => {
      const camelKey = toCamelCase(key);
      acc[camelKey] = transformKeys(obj[key]);
      return acc;
    }, {});
  }
  return obj;
};

const referralAgentApi = {
  login: async (email, password) => {
    const response = await axios.post(`${API_BASE}/api/referral-agent/auth/login`, {
      email,
      password,
    });
    return transformKeys(response.data);
  },

  logout: async () => {
    const response = await axios.post(
      `${API_BASE}/api/referral-agent/auth/logout`,
      {},
      { headers: getAuthHeaders() }
    );
    return transformKeys(response.data);
  },

  getCurrentAgent: async () => {
    const response = await axios.get(
      `${API_BASE}/api/referral-agent/auth/me`,
      { headers: getAuthHeaders() }
    );
    return transformKeys(response.data);
  },

  changePassword: async (currentPassword, newPassword) => {
    const response = await axios.put(
      `${API_BASE}/api/referral-agent/auth/change-password`,
      { current_password: currentPassword, new_password: newPassword },
      { headers: getAuthHeaders() }
    );
    return transformKeys(response.data);
  },

  getDashboard: async () => {
    const response = await axios.get(
      `${API_BASE}/api/referral-agent/crm/dashboard`,
      { headers: getAuthHeaders() }
    );
    return transformKeys(response.data);
  },

  getLeads: async (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.status) params.append('status', filters.status);
    if (filters.priority) params.append('priority', filters.priority);
    if (filters.search) params.append('search', filters.search);

    const response = await axios.get(
      `${API_BASE}/api/referral-agent/crm/leads?${params.toString()}`,
      { headers: getAuthHeaders() }
    );
    return transformKeys(response.data);
  },

  getLeadDetail: async (leadId) => {
    const response = await axios.get(
      `${API_BASE}/api/referral-agent/crm/leads/${leadId}`,
      { headers: getAuthHeaders() }
    );
    return transformKeys(response.data);
  },

  addLeadNote: async (leadId, noteText) => {
    const response = await axios.post(
      `${API_BASE}/api/referral-agent/crm/leads/${leadId}/notes`,
      { note_text: noteText },
      { headers: getAuthHeaders() }
    );
    return transformKeys(response.data);
  },

  updateLeadStatus: async (leadId, status, nextFollowUp = null) => {
    const response = await axios.put(
      `${API_BASE}/api/referral-agent/crm/leads/${leadId}/status`,
      { status, next_follow_up: nextFollowUp },
      { headers: getAuthHeaders() }
    );
    return transformKeys(response.data);
  },

  getClients: async () => {
    const response = await axios.get(
      `${API_BASE}/api/referral-agent/crm/clients`,
      { headers: getAuthHeaders() }
    );
    return transformKeys(response.data);
  },

  getCommissions: async () => {
    const response = await axios.get(
      `${API_BASE}/api/referral-agent/commissions/schedule`,
      { headers: getAuthHeaders() }
    );
    return transformKeys(response.data);
  },

  createLead: async (leadData) => {
    const response = await axios.post(
      `${API_BASE}/api/referral-agent/crm/leads`,
      leadData,
      { headers: getAuthHeaders() }
    );
    return transformKeys(response.data);
  },
};

export default referralAgentApi;
