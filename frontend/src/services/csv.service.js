import api from './api.js';

export const previewCSVService = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const { data } = await api.post('/csv/preview', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
};

export const importCSVService = async (file, categoryId = null) => {
    const formData = new FormData();
    formData.append('file', file);
    if (categoryId) formData.append('category_id', categoryId);
    const { data } = await api.post('/csv/import', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
};