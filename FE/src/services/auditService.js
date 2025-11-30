import api from './api';

export const auditService = {

    // Summary kết quả theo VIDEO cho trang Audit
    getMyResults: () => api.get('/results/my'),

    // Thông báo riêng của user (chuông)
    getMyNotifications: () => api.get('/audit/my-notifications'),
};
