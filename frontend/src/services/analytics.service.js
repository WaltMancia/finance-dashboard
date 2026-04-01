import api from './api.js';

export const getDashboardService = async () => {
    const { data } = await api.get('/analytics/dashboard');
    return data;
};

export const getCategoryBreakdownService = async (month = null) => {
    const params = month ? { month } : {};
    const { data } = await api.get('/analytics/categories', { params });
    return data;
};