import axios from 'axios';
import type { AxiosError, InternalAxiosRequestConfig } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('admin_access_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ code?: string | number; msg?: string; detail?: unknown }>) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('admin_access_token');
      localStorage.removeItem('admin_user');
      window.location.href = '/admin/login';
    }
    if (error.response?.status === 422) {
      const detail = error.response?.data?.detail;
      let msg = '数据验证失败';
      if (Array.isArray(detail) && detail[0]?.msg) {
        msg = detail[0].msg;
      } else if (typeof detail === 'string') {
        msg = detail;
      }
      return Promise.reject(new Error(msg));
    }
    const msg = error.response?.data?.msg || error.message || '网络错误';
    return Promise.reject(new Error(msg));
  }
);

export default api;
