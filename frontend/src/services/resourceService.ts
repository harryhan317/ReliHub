import api from './api';
import type { ApiResponse, Resource, PaginatedResponse, ResourceCategory } from '../types';

export const resourceService = {
  async getCategories() {
    const res = await api.get<ApiResponse<ResourceCategory[]>>('/resources/categories');
    return res.data;
  },

  async getResources(params: { category?: string; page?: number; page_size?: number; sort?: string }) {
    const res = await api.get<ApiResponse<PaginatedResponse<Resource>>>('/resources', { params });
    return res.data;
  },

  async getResource(id: string) {
    const res = await api.get<ApiResponse<Resource>>(`/resources/${id}`);
    return res.data;
  },

  async uploadResource(data: FormData) {
    const res = await api.post<ApiResponse<Resource>>('/resources', data, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  async downloadResource(id: string) {
    const res = await api.post<ApiResponse<{ download_url: string }>>(`/resources/${id}/download`);
    return res.data;
  },

  async likeResource(id: string) {
    const res = await api.post<ApiResponse>(`/resources/${id}/like`);
    return res.data;
  },

  async collectResource(id: string) {
    const res = await api.post<ApiResponse>(`/resources/${id}/collect`);
    return res.data;
  },

  async getMyResources(params: { type?: string; page?: number; page_size?: number }) {
    const res = await api.get<ApiResponse<PaginatedResponse<Resource>>>('/resources/my', { params });
    return res.data;
  },
};
