// api component to interface more easily with the backend servers
import axios from "axios";

const API_HOSTNAME = "http://localhost:5000";

const api = {
  getAlarm: async (id) => {
    const response = await axios.get(`${API_HOSTNAME}/alarms/${id}`);
    return response.data;
  },

  getAlarms: async () => {
    const response = await axios.get(`${API_HOSTNAME}/alarms`);
    return response.data;
  },

  createAlarm: async (alarm) => {
    const response = await axios.post(`${API_HOSTNAME}/alarms`, alarm);
    return response.data;
  },

  updateAlarm: async (id, updates) => {
    const response = await axios.put(`${API_HOSTNAME}/alarms/${id}`, updates);
    return response.data;
  },

  toggleAlarm: async (id) => {
    const response = await axios.patch(`${API_HOSTNAME}/alarms/${id}/toggle`);
    return response.data;
  },

  deleteAlarm: async (id) => {
    const response = await axios.delete(`${API_HOSTNAME}/alarms/${id}`);
    return response.data;
  },
};

export default api;
