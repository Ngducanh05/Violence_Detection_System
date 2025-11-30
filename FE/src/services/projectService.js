import api from "./api";

export const projectService = {
    getMyProjects: () => api.get("/projects")
    
};
