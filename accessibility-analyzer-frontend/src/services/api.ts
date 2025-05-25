import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const analyzeUrl = async (url: string) => {
    try {
        const response = await axios.post(`${API_URL}/analyze`, { url });
        return response.data;
    } catch (error) {
        console.error("Error analyzing URL:", error);
        throw error;
    }
};
