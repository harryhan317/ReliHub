import api from './api';
import type { ApiResponse, Notification, PaginatedResponse, Feedback } from '../types';

export const notificationService = {
  async getNotifications(params: { type?: string; page?: number; page_size?: number }) {
    const res = await api.get<ApiResponse<any>>('/notifications', {
      params: {
        notification_type: params.type || undefined,
        page: params.page || 1,
        page_size: params.page_size || 20,
      },
    });
    return res.data;
  },

  async markAllRead() {
    const res = await api.post<ApiResponse>('/notifications/mark-all-as-read');
    return res.data;
  },

  async markRead(id: string) {
    const res = await api.post<ApiResponse>('/notifications/mark-as-read', { notification_ids: [id] });
    return res.data;
  },

  async getUnreadCount() {
    const res = await api.get<ApiResponse<any>>('/notifications/stats');
    return res.data;
  },
};

export const feedbackService = {
  async createFeedback(data: { type: string; content: string; screenshots?: string[]; contact?: string }) {
    const res = await api.post<ApiResponse<Feedback>>('/feedback', {
      type: data.type,
      content: data.content,
      images: data.screenshots,
      contact: data.contact,
    });
    return res.data;
  },

  async getFeedbackHistory(params: { page?: number; page_size?: number }) {
    const res = await api.get<ApiResponse<any>>('/feedback/my', {
      params: { page: params.page || 1, size: params.page_size || 20 },
    });
    return res.data;
  },
};

export const searchService = {
  async search(params: { query: string; type: string; page?: number; page_size?: number }) {
    const res = await api.get<ApiResponse<any>>('/search', {
      params: {
        q: params.query,
        type: params.type === 'RESOURCE' ? 'RESOURCE' : params.type === 'COMMUNITY' ? 'COMMUNITY' : params.type === 'AI' ? 'AI' : 'ALL',
        page: params.page || 1,
        size: params.page_size || 20,
      },
    });
    return res.data;
  },

  async getHotKeywords() {
    const res = await api.get<ApiResponse<any>>('/search/trending');
    return res.data;
  },

  async getSearchHistory() {
    const res = await api.get<ApiResponse<any>>('/search/history');
    return res.data;
  },

  async clearSearchHistory() {
    const res = await api.delete<ApiResponse>('/search/history');
    return res.data;
  },
};

export const ledgerService = {
  async checkin() {
    const res = await api.post<ApiResponse<any>>('/ledger/checkin');
    return res.data;
  },

  async getBalance() {
    const res = await api.get<ApiResponse<any>>('/ledger/balance');
    return res.data;
  },

  async getTransactions(params: { page?: number; page_size?: number }) {
    const res = await api.get<ApiResponse<any>>('/ledger/history', {
      params: { page: params.page || 1, page_size: params.page_size || 50 },
    });
    return res.data;
  },
};
