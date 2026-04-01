import api from './api.js';

export const getCategoriesService = async () => {
    const { data } = await api.get('/categories');
    return data;
};

export const createCategoryService = async (categoryData) => {
    const { data } = await api.post('/categories', categoryData);
    return data;
};