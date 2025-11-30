import api from './api';

export const dashboardService = {
    getStats: () => api.get('/dashboard/stats'),
    deleteActivity: (id) => api.delete(`/dashboard/activity/${id}`),
};