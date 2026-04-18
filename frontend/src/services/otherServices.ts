import api from './api';
import type { ApiResponse, Notification, PaginatedResponse, Feedback } from '../types';

export const notificationService = {
  async getNotifications(params: { type?: string; page?: number; page_size?: number }) {
    const res = await api.get<ApiResponse<PaginatedResponse<Notification>>>('/notifications', { params });
    return res.data;
  },

  async markAllRead() {
    const res = await api.post<ApiResponse>('/notifications/read-all');
    return res.data;
  },

  async markRead(id: string) {
    const res = await api.post<ApiResponse>(`/notifications/${id}/read`);
    return res.data;
  },

  async getUnreadCount() {
    const res = await api.get<ApiResponse<{ count: number }>>('/notifications/unread-count');
    return res.data;
  },
};

export const feedbackService = {
  async createFeedback(data: { type: string; content: string; screenshots?: string[]; contact?: string }) {
    const res = await api.post<ApiResponse<Feedback>>('/feedback', data);
    return res.data;
  },

  async getFeedbackHistory(params: { page?: number; page_size?: number }) {
    const res = await api.get<ApiResponse<PaginatedResponse<Feedback>>>('/feedback', { params });
    return res.data;
  },
};

export const searchService = {
  async search(params: { query: string; type: string; page?: number; page_size?: number }) {
    const res = await api.get<ApiResponse<PaginatedResponse<any>>>('/search', { params });
    return res.data;
  },

  async getHotKeywords() {
    const res = await api.get<ApiResponse<string[]>>('/search/hot');
    return res.data;
  },

  async getSearchHistory() {
    const res = await api.get<ApiResponse<string[]>>('/search/history');
    return res.data;
  },

  async clearSearchHistory() {
    const res = await api.delete<ApiResponse>('/search/history');
    return res.data;
  },
};

export const ledgerService = {
  async checkin() {
    const res = await api.post<ApiResponse<{ beans: number; credit: number }>>('/ledger/checkin');
    return res.data;
  },

  async getBalance() {
    const res = await api.get<ApiResponse<{ beans: number; credit: number }>>('/ledger/balance');
    return res.data;
  },

  async getTransactions(params: { page?: number; page_size?: number }) {
    const res = await api.get<ApiResponse<PaginatedResponse<any>>>('/ledger/transactions', { params });
    return res.data;
  },
};
