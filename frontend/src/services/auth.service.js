import api from './api.js';

export const loginService = async (credentials) => {
    const { data } = await api.post('/auth/login', credentials);
    return data;
};

export const registerService = async (userData) => {
    const { data } = await api.post('/auth/register', userData);
    return data;
};

export const getMeService = async () => {
    const { data } = await api.get('/auth/me');
    return data;
};