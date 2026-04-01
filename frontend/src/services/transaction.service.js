import api from './api.js';

export const getTransactionsService = async (params = {}) => {
    const { data } = await api.get('/transactions', { params });
    return data;
};

export const createTransactionService = async (transactionData) => {
    const { data } = await api.post('/transactions', transactionData);
    return data;
};

export const updateTransactionService = async (id, transactionData) => {
    const { data } = await api.put(`/transactions/${id}`, transactionData);
    return data;
};

export const deleteTransactionService = async (id) => {
    await api.delete(`/transactions/${id}`);
};

export const getSummaryService = async () => {
    const { data } = await api.get('/transactions/summary');
    return data;
};