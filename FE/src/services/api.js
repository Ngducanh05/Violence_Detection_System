import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000";

const api = axios.create({
    baseURL: API_BASE_URL,
});

// gắn token vào request
api.interceptors.request.use(config => {
    const token = localStorage.getItem("access_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
});

// refresh khi 401
api.interceptors.response.use(
    res => res,
    async err => {
        const original = err.config;

        // chỉ refresh 1 lần
        if (err.response?.status === 401 && !original._retry) {
            original._retry = true;

            const refresh = localStorage.getItem("refresh_token");
            if (!refresh) return Promise.reject(err);

            try {
                const res = await axios.post(`${API_BASE_URL}/auth/refresh`, {
                    refresh_token: refresh,
                });

                localStorage.setItem("access_token", res.data.access_token);
                localStorage.setItem("refresh_token", res.data.refresh_token);

                original.headers.Authorization = `Bearer ${res.data.access_token}`;

                return api(original); // retry request
            } catch {
                return Promise.reject(err);
            }
        }

        return Promise.reject(err);
    }
);

export default api;
