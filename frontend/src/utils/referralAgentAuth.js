export const TOKEN_KEY = 'referral_agent_token';
export const USER_KEY = 'referral_agent_user';

export const setAuthToken = (token) => {
  localStorage.setItem(TOKEN_KEY, token);
};

export const getAuthToken = () => {
  return localStorage.getItem(TOKEN_KEY);
};

export const removeAuthToken = () => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
};

export const setCurrentAgent = (agent) => {
  localStorage.setItem(USER_KEY, JSON.stringify(agent));
};

export const getCurrentAgent = () => {
  const agentStr = localStorage.getItem(USER_KEY);
  return agentStr ? JSON.parse(agentStr) : null;
};

export const isAuthenticated = () => {
  return !!getAuthToken();
};

export const logout = () => {
  removeAuthToken();
  window.location.href = '/referral-agent/login';
};
