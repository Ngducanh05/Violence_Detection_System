import api from "./api";

export const register = async (name, email, password) => {
    const res = await api.post("/users/register", {
        name,
        email,
        password
    });
    return res.data;
};

export const login = async (email, password) => {
    const res = await api.post("/auth/login", {
        email,
        password
    });
    localStorage.setItem("access_token", res.data.access_token);
    localStorage.setItem("refresh_token", res.data.refresh_token);
    return res.data;
};
