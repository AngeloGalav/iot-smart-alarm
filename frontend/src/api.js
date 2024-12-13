// api component to interface more easily with the backend servers
import axios from "axios";

const API_HOSTNAME = "http://localhost:5000";
const DATA_ANALYSIS_HOSTNAME = "http://localhost:5001";

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

  sendSamplingRate: async (sampling_rate) => {
    const response = await axios.post(`${API_HOSTNAME}/sampling_rate`, sampling_rate);
    return response.data;
  },

  sendSettings: async (settings) => {
    const response = await axios.post(`${API_HOSTNAME}/send_settings`, settings);
    return response.data;
  },

  stopAlarm: async () => {
    const response = await axios.post(`${API_HOSTNAME}/stop_alarm`);
    return response.data;
  },

  startAlarm: async () => {
    const response = await axios.post(`${API_HOSTNAME}/start_alarm`);
    return response.data;
  },

  getWeather: async () => {
    const response = await axios.get(`${API_HOSTNAME}/weather`);
    return response.data;
  },

  getSleepData: async () => {
    const response = await axios.get(`${DATA_ANALYSIS_HOSTNAME}/sleep_time`);
    return response.data;
  },

  getDelay: async () => {
    const response = await axios.get(`${DATA_ANALYSIS_HOSTNAME}/delay`);
    return response.data;
  },

  getBedPrediction: async () => {
    const response = await axios.get(`${DATA_ANALYSIS_HOSTNAME}/bed_state_pred`);
    return response.data;
  },

  updateLocation: async (weather_location) => {
    const response = await axios.post(`${API_HOSTNAME}/weather`, weather_location);
    return response.data;
  },

};

export default api;
