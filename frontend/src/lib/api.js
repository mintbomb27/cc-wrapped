import axios from 'axios';

const api = axios.create({
    baseURL: '/api/v1',
});

export const getCards = () => api.get('/cards/');
export const createCard = (data) => api.post('/cards/', data);
export const uploadStatement = (cardId, files, password) => {
    const formData = new FormData();
    // Append multiple files
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }
    if (password) {
        formData.append('password', password);
    }
    return api.post(`/cards/${cardId}/upload-statement/`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
};
export const getTransactions = (cardId) => api.get(`/cards/${cardId}/transactions/`);
export const getReport = (cardId) => api.get(`/cards/${cardId}/report/`);

export default api;
