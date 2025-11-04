/**
 * Referral System API Service
 * Handles all API calls for salespeople and commissions management
 */

import apiAxios from '../utils/apiAxios';

// Salespeople Management
export const getSalespeople = async (activeOnly = true) => {
  const response = await apiAxios.get(
    `/api/admin/referrals/salespeople?active_only=${activeOnly}`
  );
  return response.data;
};

export const getSalespersonById = async (id) => {
  const response = await apiAxios.get(`/api/admin/referrals/salespeople/${id}`);
  return response.data;
};

export const createSalesperson = async (data) => {
  const response = await apiAxios.post('/api/admin/referrals/salespeople', data);
  return response.data;
};

export const updateSalesperson = async (id, data) => {
  const response = await apiAxios.put(`/api/admin/referrals/salespeople/${id}`, data);
  return response.data;
};

// Commission Management
export const getCommissionCalendar = async (startDate, endDate, salespersonId = null) => {
  let url = `/api/admin/referrals/commissions/calendar?start_date=${startDate}&end_date=${endDate}`;
  if (salespersonId) {
    url += `&salesperson_id=${salespersonId}`;
  }
  const response = await apiAxios.get(url);
  return response.data;
};

export const getPendingCommissions = async (salespersonId = null, statusFilter = 'all') => {
  let url = `/api/admin/referrals/commissions/pending?status_filter=${statusFilter}`;
  if (salespersonId) {
    url += `&salesperson_id=${salespersonId}`;
  }
  const response = await apiAxios.get(url);
  return response.data;
};

export const approveCommission = async (commissionId) => {
  const response = await apiAxios.post(
    `/api/admin/referrals/commissions/${commissionId}/approve`
  );
  return response.data;
};

export const markCommissionPaid = async (commissionId, paymentDetails) => {
  const response = await apiAxios.post(
    `/api/admin/referrals/commissions/${commissionId}/mark-paid`,
    paymentDetails
  );
  return response.data;
};

// Client Referral
export const updateClientReferral = async (clientId, salespersonId) => {
  const response = await apiAxios.put(
    `/api/admin/referrals/clients/${clientId}/referral`,
    { salesperson_id: salespersonId }
  );
  return response.data;
};

// Public endpoints (no auth needed)
export const getPublicSalespeople = async () => {
  const response = await apiAxios.get('/public/salespeople');
  return response.data;
};

export const getSalespersonByCode = async (referralCode) => {
  const response = await apiAxios.get(`/public/salespeople/${referralCode}`);
  return response.data;
};

export default {
  getSalespeople,
  getSalespersonById,
  createSalesperson,
  updateSalesperson,
  getCommissionCalendar,
  getPendingCommissions,
  approveCommission,
  markCommissionPaid,
  updateClientReferral,
  getPublicSalespeople,
  getSalespersonByCode
};
