import api from "./api";

export const detectService = {
    uploadVideo: async (file, projectId) => {
        const form = new FormData();
        form.append("file", file);

        const res = await api.post(`/detect/video?project_id=${projectId}`, form);
        return res.data; 
    }
};
